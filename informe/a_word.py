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
# portada: en Word los logos y la institución se arman aparte (ver posprocesado), no dentro del título
m = re.search(r"\\title\{(\\includegraphics.*?)\\LARGE", s, flags=re.S)
s = s.replace(m.group(1), "")
s = s.replace("\\begin{document}", "\\begin{document}\n\nXXLOGOSXX "
              "\\includegraphics[height=2.6cm]{figuras/logo_ipn.png} \\includegraphics[height=2.1cm]{figuras/logo_escom.png}\n\n"
              "XXINSTXX Instituto Politécnico Nacional\\\\ Escuela Superior de Cómputo\n\n", 1)
open(S + "informe_pandoc.tex", "w").write(s)

subprocess.run([PANDOC, S + "informe_pandoc.tex", "-f", "latex", "-t", "docx", "--resource-path", BASE,
                "--toc", "--lof", "--lot", "-M", "lang=es-MX", "-M", "toc-title=Índice",
                "-M", "lof-title=Índice de figuras", "-M", "lot-title=Índice de tablas",
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
            # una página para cada parte inicial: portada, resumen, índice, figuras, tablas
            SALTO = '<w:p><w:r><w:br w:type="page" /></w:r></w:p>'
            x = x.replace('<w:pStyle w:val="Title" />', '<w:pStyle w:val="Title" /><w:spacing w:before="3000" />', 1)
            x = x.replace('<w:p>\n      <w:pPr>\n        <w:pStyle w:val="AbstractTitle" />',
                          SALTO + '<w:p>\n      <w:pPr>\n        <w:pStyle w:val="AbstractTitle" />', 1)
            x = x.replace("<w:sdt>", SALTO + "<w:sdt>")
            fin = x.rfind("</w:sdt>", 0, x.find('w:val="Heading1"')) + len("</w:sdt>")
            x = x[:fin] + SALTO + x[fin:]
            # mover logos e institución al inicio: logos a las orillas (tabulador derecho), institución centrada
            def parrafo(marca):
                i = x.find(marca)
                return x.rfind("<w:p>", 0, i), x.find("</w:p>", i) + len("</w:p>")
            a0, a1 = parrafo("XXLOGOSXX")
            logos = x[a0:a1]
            logos = re.sub(r"<w:r>(?:(?!</w:r>).)*XXLOGOSXX(?:(?!</w:r>).)*</w:r>", "", logos, flags=re.S)
            corridas = re.findall(r"<w:r>(?:(?!</w:r>).)*?<w:drawing>.*?</w:r>", logos, flags=re.S)
            logos = ('<w:p><w:pPr><w:tabs><w:tab w:val="right" w:pos="9360" /></w:tabs></w:pPr>'
                     + corridas[0] + "<w:r><w:tab /></w:r>" + corridas[1] + "</w:p>")
            x = x[:a0] + x[a1:]
            b0, b1 = parrafo("XXINSTXX")
            inst = x[b0:b1].replace("XXINSTXX ", "").replace("XXINSTXX", "")
            inst = re.sub(r"<w:pPr>.*?</w:pPr>", "", inst, count=1, flags=re.S)
            inst = inst.replace("<w:p>", '<w:p><w:pPr><w:spacing w:before="240" /><w:jc w:val="center" />'
                                '<w:rPr><w:sz w:val="28" /></w:rPr></w:pPr>', 1)
            inst = inst.replace("<w:r>", '<w:r><w:rPr><w:sz w:val="28" /></w:rPr>')
            x = x[:b0] + x[b1:]
            cuerpo = x.find("<w:body>") + len("<w:body>")
            x = x[:cuerpo] + logos + inst + x[cuerpo:]
            x = x.replace('<w:spacing w:before="3000" />', '<w:spacing w:before="1800" />', 1)
            x = x.replace("Índice de Figuras", "Índice de figuras").replace("Índice de Cuadros", "Índice de tablas")
            data = x.encode("utf-8")
        if item.filename == "word/settings.xml":   # Word actualiza el índice al abrir
            data = data.decode("utf-8").replace("<w:rsids>", '<w:updateFields w:val="true" /><w:rsids>', 1).encode("utf-8")
        zout.writestr(item, data)
shutil.move(tmp, docx)
print("tablas ajustadas")
