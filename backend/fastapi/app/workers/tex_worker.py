import asyncio
import json
import logging
import os
import subprocess
import re
import hashlib
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.services.tex_service import TexService
from app.core.config import settings
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TexWorker")

from app.repositories.article_repository import ArticleRepository
from motor.motor_asyncio import AsyncIOMotorClient

class TexWorker:
    def __init__(self):
        self.tex_service = TexService()
        self.consumer = None
        self.producer = None
        self.repo = None
        self.db_client = None

    async def start(self):
        # Initialize DB
        self.db_client = AsyncIOMotorClient(settings.mongodb_url)
        db = self.db_client[settings.mongodb_db_name]
        self.repo = ArticleRepository(db)

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
            if self.db_client:
                self.db_client.close()

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
            # Use a safe folder name (hash the ID to avoid filesystem limits)
            safe_id = hashlib.md5(article_id.encode()).hexdigest()
            pdf_path = await self.compile_tex(full_tex, safe_id)
            
            if pdf_path:
                logger.info(f"PDF successfully generated for {article_id} in {safe_id}")
                # 4. Update article in DB with the PUBLIC PDF URL
                # The Caddy server exposes /app/exports/pdfs at /pdfs/
                public_url = f"https://uncovernews.ddns.net/pdfs/{safe_id}/article.pdf"
                await self.repo.update_pdf_path(article_id, public_url)
                logger.info(f"Database updated for article {article_id} with public URL.")
        except Exception as e:
            logger.error(f"Failed to process rendering task: {e}")

    async def get_ai_snippet(self, article: dict) -> str:
        prompt = self.tex_service.get_latex_prompt(article)
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                response = await client.post(
                    f"{settings.ollama_host}/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if response.status_code == 200:
                    raw_content = response.json().get('response', '').strip()
                    
                    # Clean the response: Extract only content inside backticks if they exist
                    if "```" in raw_content:
                        # Extract content between the first and last triple backticks
                        match = re.search(r'```(?:latex)?\n?(.*?)\n?```', raw_content, re.DOTALL)
                        if match:
                            clean_content = match.group(1).strip()
                        else:
                            clean_content = raw_content
                    else:
                        clean_content = raw_content
                        
                    # 2. Aggressive cleanup of common LLM mistakes
                    # Remove any duplicate class/preamble/document tags
                    forbidden = [
                        r"\\documentclass.*", 
                        r"\\usepackage.*", 
                        r"\\begin\{document\}", 
                        r"\\end\{document\}",
                        r"\\begin\{multicols\}.*",
                        r"\\end\{multicols\}"
                    ]
                    for pattern in forbidden:
                        clean_content = re.sub(pattern, "", clean_content)
                        
                    # Fix image reference
                    clean_content = clean_content.replace("{image.jpg}", "{atom.jpg}")
                    
                    return clean_content.strip()
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
        template_src = "/app/app/services/article_templates/newspaper"
        for f_name in ["newspaper.sty", "newspaper-mod.sty", "atom.jpg"]:
             src_path = os.path.join(template_src, f_name)
             if os.path.exists(src_path):
                 subprocess.run(["cp", src_path, work_dir])
             else:
                 logger.warning(f"Template asset missing: {src_path}")

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
