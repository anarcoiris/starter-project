import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TexService:
    @staticmethod
    def escape_latex(text: str) -> str:
        """
        Escapes special LaTeX characters to prevent compilation errors.
        """
        if not text:
            return ""
        
        # Order matters
        map = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        
        regex = re.compile('|'.join(re.escape(str(key)) for key in map.keys()))
        return regex.sub(lambda match: map[match.group()], text)

    def get_latex_prompt(self, article: Dict[str, Any]) -> str:
        """
        Generates the system prompt and user content for Ollama to convert an article into LaTeX.
        """
        title = self.escape_latex(article.get('title', ''))
        author = self.escape_latex(article.get('author', 'Agente Symmetry'))
        content = article.get('content', '') # We want AI to format this
        
        # In a real scenario, we would download the image or use its local path
        image_name = "cover_image.jpg" 

        prompt = f"""
Eres un maquetador experto en LaTeX para el periódico "Anarcotimes". 
Tu tarea es convertir el contenido de una noticia en código LaTeX compatible con el paquete 'newspaper'.

REGLAS ESTRICTAS:
1. Usa solo los comandos: \\byline{{TITULO}}{{AUTOR}}, \\begin{{window}}[líneas, l/r, \\includegraphics{{...}}, CAPTION], y \\closearticle.
2. Si hay una imagen, colócala al principio usando el entorno 'window'.
3. No incluyas preámbulo, \\begin{{document}} ni \\end{{document}}. Solo el fragmento de la noticia.
4. Asegúrate de que el texto fluya bien en 3 columnas.
5. Escapa caracteres especiales de LaTeX si los encuentras.

NOTICIA A CONVERTIR:
Título: {title}
Autor: {author}
Contenido: {content}

RESULTADO EN LATEX:
"""
        return prompt

    def build_full_document(self, content_snippets: list) -> str:
        """
        Wraps the generated snippets into the full newspaper template.
        """
        template_header = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{microtype}
\usepackage{newspaper}
\usepackage{graphicx}
\usepackage{multicol}
\usepackage{picinpar}
\usepackage{newspaper-mod}

\SetPaperName{Anarcotimes:}
\SetHeaderName{Anarcotimes}
\SetPaperLocation{Madrid}
\SetPaperSlogan{``La Verdad es Simétrica.''}
\SetPaperPrice{Zero SYM}

\begin{document}
\maketitle
\begin{multicols}{3}
"""

        template_footer = r"""
\end{multicols}
\end{document}
"""
        return template_header + "\n".join(content_snippets) + template_footer
