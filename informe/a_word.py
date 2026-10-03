"""Convierte el informe LaTeX a Word (informe/informe.docx).

Requiere pandoc. Si no está instalado en el sistema:
    .venv/bin/pip install pypandoc_binary
Uso:
    .venv/bin/python informe/a_word.py
"""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

BASE = str(Path(__file__).resolve().parent) + "/"
S = tempfile.mkdtemp() + "/"
PANDOC = shutil.which("pandoc")
if PANDOC is None:
    import pypandoc
    PANDOC = pypandoc.get_pandoc_path()

s = open(BASE + "main.tex").read()
s = re.sub(r"\\input\{(secciones/[^}]+)\}", lambda m: open(BASE + m.group(1) + ".tex").read(), s)
# quitar las definiciones de macros propias (pandoc no entiende \detokenize ni \ding)
s = re.sub(r"\\newcommand\{\\(ok|pend|hecho|falta|archivo)\}(\[1\])?\{[^\n]*\}[^\n]*\n", "", s)
s = s.replace("\\archivo{", "\\texttt{")
for macro, simbolo in [("ok", "✓"), ("pend", "○"), ("hecho", "☑"), ("falta", "☐")]:
    s = re.sub(r"\\" + macro + r"(\{\})?(?![a-zA-Z])", simbolo, s)
# el título lleva saltos de línea forzados que en Word sobran
s = s.replace("actividad económica\\\\\nde la Ciudad", "actividad económica de la Ciudad")
# columnas de ancho fijo propias (L{3cm}) → p{3cm}, que pandoc sí reconoce
s = re.sub(r"\\newcolumntype\{L\}[^\n]*\n", "", s)
s = re.sub(r"[Lp]\{[0-9.]+cm\}", "l", s)  # Word ajusta el ancho solo
open(S + "informe_pandoc.tex", "w").write(s)

subprocess.run([PANDOC, S + "informe_pandoc.tex", "-f", "latex", "-t", "docx", "--resource-path", BASE,
                "--toc", "-M", "lang=es-MX", "-M", "toc-title=Índice",
                "-o", BASE + "informe.docx"], check=True)
print("ok")

# --- posprocesado: tablas al ancho de la página (9360 twips = 6.5") y con bordes
import zipfile
ANCHO = 9360
BORDES = ('<w:tblBorders><w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
          '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
          '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/></w:tblBorders>')

def escalar(m):
    cols = [int(x) for x in re.findall(r'<w:gridCol w:w="(\d+)" ?/>', m.group(0))]
    total = sum(cols)
    return "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{round(c * ANCHO / total)}" />' for c in cols) + "</w:tblGrid>"

docx = BASE + "informe.docx"
tmp = S + "informe_tmp.docx"
with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            x = data.decode("utf-8")
            x = x.replace('<w:tblW w:type="auto" w:w="0" />', f'<w:tblW w:type="pct" w:w="5000" />{BORDES}')
            x = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", escalar, x)
            data = x.encode("utf-8")
        if item.filename == "word/settings.xml":   # Word actualiza el índice al abrir
            data = data.decode("utf-8").replace("<w:rsids>", '<w:updateFields w:val="true" /><w:rsids>', 1).encode("utf-8")
        zout.writestr(item, data)
shutil.move(tmp, docx)
print("tablas ajustadas")
