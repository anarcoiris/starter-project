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
        content = article.get('content', '')
        
        prompt = f"""
Eres un maquetador experto en LaTeX para el periódico "Anarcotimes". 
Tu tarea es convertir el contenido de una noticia (que puede venir en Markdown) en código LaTeX puro y elegante.

REGLAS DE ORO:
1. Devuelve ÚNICAMENTE el código LaTeX. Sin explicaciones, sin saludos, sin backticks.
2. CONVIERTE la sintaxis:
   - Los títulos '# Titulo' o '## Subtitulo' deben ser \\headline{{...}} o simplemente texto en negrita \\textbf{{...}}. NO uses #.
   - Las negritas **texto** pasan a \\textbf{{texto}}.
   - El código ```...``` pasa a \\texttt{{...}}.
3. Usa EXACTAMENTE esta estructura para la imagen (entorno window de picinpar):
   \\begin{{window}}[2, l, \\includegraphics[width=1.0in]{{atom.jpg}}, {{\\centerline{{LEYENDA}}}}]
   TEXTO_DEL_ARTICULO
   \\end{{window}}
4. Empieza con: \\byline{{{title}}}{{{author}}} y termina con: \\closearticle
5. IMPORTANTE: NO incluyas \\documentclass, \\usepackage ni \\begin{{document}}.

CONTENIDO A CONVERTIR:
{content}

RESULTADO (CÓDIGO LATEX PURO):
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
