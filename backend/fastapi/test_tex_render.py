import asyncio
import httpx
from app.services.tex_service import TexService
from app.core.config import settings

async def simulate_rendering():
    tex_service = TexService()
    
    # Noticia de prueba (basada en lo que solemos tener)
    test_article = {
        "title": "La IA de Symmetry alcanza la Singularidad Periodística",
        "author": "Agente Symmetry",
        "content": """Hoy se ha confirmado que el sistema Symmetry ha logrado procesar más de 1000 fuentes de noticias 
        en tiempo real, aplicando un filtro de veracidad basado en blockchain. Los usuarios ahora pueden 
        recibir recompensas en SYM por validar la información. Este hito marca el fin de las fake news 
        tal como las conocemos y el inicio de una era de transparencia absoluta."""
    }
    
    print("\n--- [1] ESCAPANDO CARACTERES PARA SEGURIDAD ---")
    safe_title = tex_service.escape_latex(test_article['title'])
    print(f"Título seguro: {safe_title}")
    
    print("\n--- [2] GENERANDO PROMPT PARA OLLAMA ---")
    prompt = tex_service.get_latex_prompt(test_article)
    # print(prompt)
    
    print("\n--- [3] PIDIENDO MAQUETACIÓN A OLLAMA (SIMULADO) ---")
    # En un entorno real llamaríamos a Ollama. Aquí muestro cómo quedaría el snippet ideal:
    snippet = f"""\\byline{{{safe_title}}}{{{test_article['author']}}}
\\begin{{window}}[2,r,\\includegraphics[width=1.0in]{{atom.jpg}},\\centerline{{Symmetry Core}}]
{test_article['content']}
\\end{{window}}
\\closearticle"""
    
    print("\n--- [4] ENSAMBLANDO DOCUMENTO FINAL (ANARCOTIMES) ---")
    full_doc = tex_service.build_full_document([snippet])
    print(full_doc)

if __name__ == "__main__":
    asyncio.run(simulate_rendering())
