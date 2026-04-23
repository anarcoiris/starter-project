import asyncio
import json
import logging
import os
import subprocess
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.services.tex_service import TexService
from app.core.config import settings
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TexWorker")

class TexWorker:
    def __init__(self):
        self.tex_service = TexService()
        self.consumer = None
        self.producer = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            'tex_rendering_queue',
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id="tex-renderers",
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers
        )
        
        await self.consumer.start()
        await self.producer.start()
        logger.info("Tex Worker started. Listening for rendering tasks...")
        
        try:
            async for msg in self.consumer:
                article_data = msg.value
                logger.info(f"Processing PDF rendering for: {article_data.get('title')}")
                await self.process_task(article_data)
        finally:
            await self.consumer.stop()
            await self.producer.stop()

    async def process_task(self, article: dict):
        try:
            # 1. Get LaTeX snippet from AI
            snippet = await self.get_ai_snippet(article)
            if not snippet:
                return

            # 2. Build full document
            full_tex = self.tex_service.build_full_document([snippet])
            
            # 3. Compile (Using tectonic for speed and auto-package management)
            article_id = article.get('articleId', 'temp')
            pdf_path = await self.compile_tex(full_tex, article_id)
            
            if pdf_path:
                logger.info(f"PDF successfully generated: {pdf_path}")
                # 4. TODO: Upload to Firebase Storage and update article in DB
                # For now, we log the success
        except Exception as e:
            logger.error(f"Failed to process rendering task: {e}")

    async def get_ai_snippet(self, article: dict) -> str:
        prompt = self.tex_service.get_latex_prompt(article)
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{settings.ollama_host}/api/generate",
                    json={
                        "model": "llama3", # Or the model being used
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if response.status_code == 200:
                    return response.json().get('response', '').strip()
                else:
                    logger.error(f"Ollama error: {response.text}")
            except Exception as e:
                logger.error(f"Error calling Ollama: {e}")
        return ""

    async def compile_tex(self, tex_content: str, article_id: str) -> str:
        """
        Saves the content to a file and compiles it using tectonic.
        """
        # We use a stable export path mapped to the host
        export_base = "/app/exports/pdfs"
        work_dir = os.path.join(export_base, article_id)
        os.makedirs(work_dir, exist_ok=True)
        tex_file = os.path.join(work_dir, "article.tex")
        
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(tex_content)
            
        # Copy the .sty and modification files to the work dir
        # In prod, these should be in a shared volume or baked into the image
        template_src = "app/services/article_templates/newspaper"
        for f_name in ["newspaper.sty", "newspaper-mod.sty", "atom.jpg"]:
             src_path = os.path.join(template_src, f_name)
             if os.path.exists(src_path):
                 subprocess.run(["cp", src_path, work_dir])

        try:
            # We use tectonic because it's self-contained and downloads missing packages
            result = subprocess.run(
                ["tectonic", "article.tex"],
                cwd=work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return os.path.join(work_dir, "article.pdf")
            else:
                logger.error(f"Tectonic Error: {result.stderr}")
        except Exception as e:
            logger.error(f"Compilation process failed: {e}")
            
        return ""

if __name__ == "__main__":
    worker = TexWorker()
    asyncio.run(worker.start())
