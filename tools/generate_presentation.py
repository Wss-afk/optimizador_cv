from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile


SLIDE_W = 12192000
SLIDE_H = 6858000

NAVY = "12213D"
BLUE = "3D7BFF"
TEAL = "21C7A8"
RED = "E35D6A"
TEXT = "273043"
MUTED = "6B7280"
LINE = "E6ECF2"
BOX_BG = "F8FBFF"
BOX_BG_ALT = "F6FFFB"


@dataclass
class Paragraph:
    text: str
    size: int = 2000
    bold: bool = False
    color: str = TEXT


@dataclass
class Shape:
    xml: str


def emu(x: float) -> int:
    return int(x * 914400)


def paragraph_xml(paragraph: Paragraph) -> str:
    bold = ' b="1"' if paragraph.bold else ""
    return (
        "<a:p>"
        "<a:r>"
        f'<a:rPr lang="es-ES" sz="{paragraph.size}"{bold} dirty="0" smtClean="0">'
        f'<a:solidFill><a:srgbClr val="{paragraph.color}"/></a:solidFill>'
        '<a:latin typeface="Aptos"/><a:cs typeface="Aptos"/>'
        "</a:rPr>"
        f"<a:t>{escape(paragraph.text)}</a:t>"
        "</a:r>"
        f'<a:endParaRPr lang="es-ES" sz="{paragraph.size}"/>'
        "</a:p>"
    )


def text_box(shape_id: int, name: str, x: int, y: int, w: int, h: int, paragraphs: list[Paragraph]) -> Shape:
    paras = "".join(paragraph_xml(p) for p in paragraphs)
    xml = f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="{escape(name)}"/>
        <p:cNvSpPr txBox="1"/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:noFill/>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="t"/>
        <a:lstStyle/>{paras}
      </p:txBody>
    </p:sp>
    """
    return Shape(xml)


def filled_box(
    shape_id: int,
    name: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fill: str,
    line: str = LINE,
    radius: str = "roundRect",
) -> Shape:
    xml = f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="{escape(name)}"/>
        <p:cNvSpPr/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="{radius}"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>
        <a:ln w="12700"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>
      </p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
    </p:sp>
    """
    return Shape(xml)


def line_box(shape_id: int, x: int, y: int, w: int, h: int, fill: str) -> Shape:
    return filled_box(shape_id, f"Line {shape_id}", x, y, w, h, fill, fill, "rect")


def slide_xml(shapes: list[Shape]) -> str:
    shape_xml = "".join(shape.xml for shape in shapes)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {shape_xml}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"""


def title_band(slide_title: str, kicker: str) -> list[Shape]:
    return [
        line_box(2, 0, 0, SLIDE_W, emu(0.06), BLUE),
        line_box(3, emu(11.6), 0, emu(1.73), emu(0.06), TEAL),
        text_box(4, "Title", emu(0.7), emu(0.55), emu(8.6), emu(0.7), [Paragraph(slide_title, 3000, True, NAVY)]),
        text_box(5, "Kicker", emu(10.7), emu(0.72), emu(2.0), emu(0.4), [Paragraph(kicker, 1200, False, BLUE)]),
        line_box(6, emu(0.7), emu(1.38), emu(11.9), emu(0.02), LINE),
    ]


def footer(slide_no: int, label: str) -> list[Shape]:
    return [
        text_box(90, "FooterLeft", emu(0.7), emu(7.1), emu(2.2), emu(0.25), [Paragraph("OptimizadorCV", 1100, True, NAVY)]),
        text_box(91, "FooterRight", emu(10.1), emu(7.1), emu(2.5), emu(0.25), [Paragraph(f"{label} • Diapositiva {slide_no}", 1100, False, MUTED)]),
    ]


def cover_slide() -> str:
    shapes = [
        line_box(2, 0, 0, SLIDE_W, emu(0.06), BLUE),
        line_box(3, emu(11.6), 0, emu(1.73), emu(0.06), TEAL),
        text_box(4, "Eyebrow", emu(4.5), emu(2.0), emu(3.0), emu(0.3), [Paragraph("PRESENTACION FINAL DEL PROYECTO", 1200, False, BLUE)]),
        text_box(5, "Main", emu(3.0), emu(2.5), emu(6.6), emu(0.9), [Paragraph("Optimizador de CV", 3200, True, NAVY)]),
        text_box(
            6,
            "Subtitle",
            emu(2.5),
            emu(3.3),
            emu(7.6),
            emu(0.8),
            [Paragraph("Matching automatico de ofertas y optimizacion ATS con IA local", 1800, False, MUTED)],
        ),
        text_box(7, "Bottom", emu(4.15), emu(5.8), emu(4.5), emu(0.35), [Paragraph("Grupo • Presentacion tecnica", 1300, False, TEXT)]),
        *footer(1, "Portada"),
    ]
    return slide_xml(shapes)


def bullet_slide(slide_no: int, title: str, kicker: str, left_title: str, left_points: list[str], right_title: str, right_points: list[str], label: str) -> str:
    shapes = title_band(title, kicker)
    shapes += [
        filled_box(10, "LeftBox", emu(0.7), emu(2.25), emu(5.8), emu(3.35), "FFF7F8", "F7D4D8"),
        filled_box(11, "RightBox", emu(7.0), emu(2.25), emu(5.6), emu(3.35), "F5FFFB", "CBEFE5"),
        text_box(12, "LeftTitle", emu(1.05), emu(2.55), emu(4.6), emu(0.45), [Paragraph(left_title, 2200, True, RED)]),
        text_box(13, "RightTitle", emu(7.35), emu(2.55), emu(4.6), emu(0.45), [Paragraph(right_title, 2200, True, TEAL)]),
        text_box(14, "LeftPoints", emu(1.05), emu(3.15), emu(5.0), emu(2.0), [Paragraph("- " + p, 1800, False, TEXT) for p in left_points]),
        text_box(15, "RightPoints", emu(7.35), emu(3.15), emu(4.9), emu(2.0), [Paragraph("- " + p, 1800, False, TEXT) for p in right_points]),
        *footer(slide_no, label),
    ]
    return slide_xml(shapes)


def project_idea_slide() -> str:
    shapes = title_band("La Idea del Proyecto", "PROPOSITO CORE")
    ys = [2.15, 3.25, 4.35, 5.45]
    titles = [
        "1. Subir CV",
        "2. Matching automatico",
        "3. Revision completa",
        "4. Descargar PDF",
    ]
    desc = [
        "El usuario carga un CV en PDF o TXT.",
        "El sistema busca la oferta mas compatible con embeddings.",
        "Un agente unificado analiza, optimiza, puntua ATS y recomienda mejoras.",
        "Se devuelve el CV final y se puede exportar a PDF.",
    ]
    sid = 10
    for i in range(4):
        shapes.append(filled_box(sid, f"Step{i}", emu(0.7), emu(ys[i]), emu(5.9), emu(0.82), BOX_BG, LINE))
        sid += 1
        shapes.append(text_box(sid, f"StepTitle{i}", emu(1.0), emu(ys[i] + 0.18), emu(2.2), emu(0.25), [Paragraph(titles[i], 1900, True, NAVY)]))
        sid += 1
        shapes.append(text_box(sid, f"StepDesc{i}", emu(3.0), emu(ys[i] + 0.18), emu(3.2), emu(0.32), [Paragraph(desc[i], 1550, False, MUTED)]))
        sid += 1
    shapes += [
        filled_box(40, "RightBox", emu(7.0), emu(2.15), emu(5.6), emu(4.15), "FBFCFF", LINE),
        text_box(41, "RightTitle", emu(7.35), emu(2.5), emu(4.6), emu(0.4), [Paragraph("Salida del sistema", 2200, True, BLUE)]),
        text_box(
            42,
            "RightBullets",
            emu(7.35),
            emu(3.1),
            emu(4.8),
            emu(2.4),
            [
                Paragraph("- oferta encontrada", 1800, False, TEXT),
                Paragraph("- score ATS", 1800, False, TEXT),
                Paragraph("- keywords encontradas y faltantes", 1800, False, TEXT),
                Paragraph("- cambios realizados", 1800, False, TEXT),
                Paragraph("- CV final optimizado", 1800, False, TEXT),
            ],
        ),
        *footer(4, "Idea Core"),
    ]
    return slide_xml(shapes)


def stack_slide() -> str:
    shapes = title_band("Stack Tecnologico", "ARQUITECTURA REAL")
    shapes += [
        filled_box(10, "Left", emu(0.7), emu(2.2), emu(5.8), emu(3.7), BOX_BG, LINE),
        filled_box(11, "Right", emu(7.0), emu(2.2), emu(5.6), emu(3.7), "F7FFFC", "D9F3EA"),
        text_box(12, "LeftTitle", emu(1.0), emu(2.55), emu(4.0), emu(0.4), [Paragraph("Backend e IA", 2200, True, BLUE)]),
        text_box(
            13,
            "LeftBullets",
            emu(1.0),
            emu(3.05),
            emu(5.0),
            emu(2.9),
            [
                Paragraph("- Python 3.9+", 1800, False, TEXT),
                Paragraph("- FastAPI para la API web", 1800, False, TEXT),
                Paragraph("- LangGraph para orquestar el flujo", 1800, False, TEXT),
                Paragraph("- ChromaDB para matching semantico", 1800, False, TEXT),
                Paragraph("- Ollama con qwen3:8b y nomic-embed-text", 1800, False, TEXT),
                Paragraph("- fpdf2 para exportar PDF", 1800, False, TEXT),
            ],
        ),
        text_box(14, "RightTitle", emu(7.35), emu(2.55), emu(4.0), emu(0.4), [Paragraph("Infraestructura y front", 2200, True, TEAL)]),
        text_box(
            15,
            "RightBullets",
            emu(7.35),
            emu(3.05),
            emu(4.8),
            emu(2.9),
            [
                Paragraph("- HTML, CSS y JavaScript", 1800, False, TEXT),
                Paragraph("- Docker y Docker Compose", 1800, False, TEXT),
                Paragraph("- Variables de entorno para Ollama", 1800, False, TEXT),
                Paragraph("- Chroma persistido en volumen local", 1800, False, TEXT),
                Paragraph("- Interfaz web + API REST en el mismo proyecto", 1800, False, TEXT),
            ],
        ),
        *footer(5, "Tecnologias"),
    ]
    return slide_xml(shapes)


def graph_slide() -> str:
    shapes = title_band("Grafo del Sistema", "ARQUITECTURA LANGGRAPH")
    shapes += [
        filled_box(10, "FlowBox", emu(1.2), emu(2.15), emu(10.1), emu(0.95), "F7FAFF", "DCE6F5"),
        text_box(11, "FlowText", emu(1.55), emu(2.42), emu(9.4), emu(0.35), [Paragraph("START  ->  match_offer  ->  review_cv  ->  END", 2200, True, NAVY)]),
        filled_box(12, "Node1", emu(1.2), emu(3.45), emu(4.75), emu(2.25), BOX_BG, LINE),
        filled_box(13, "Node2", emu(6.55), emu(3.45), emu(4.75), emu(2.25), "F7FFFC", "D9F3EA"),
        text_box(14, "Node1Title", emu(1.55), emu(3.75), emu(3.5), emu(0.3), [Paragraph("Nodo 1: match_offer", 2200, True, BLUE)]),
        text_box(
            15,
            "Node1Body",
            emu(1.55),
            emu(4.25),
            emu(3.9),
            emu(1.2),
            [
                Paragraph("- usa JobOfferStore", 1750, False, TEXT),
                Paragraph("- calcula similitud con embeddings", 1750, False, TEXT),
                Paragraph("- devuelve la mejor oferta compatible", 1750, False, TEXT),
            ],
        ),
        text_box(16, "Node2Title", emu(6.9), emu(3.75), emu(3.5), emu(0.3), [Paragraph("Nodo 2: review_cv", 2200, True, TEAL)]),
        text_box(
            17,
            "Node2Body",
            emu(6.9),
            emu(4.25),
            emu(3.9),
            emu(1.2),
            [
                Paragraph("- usa CVReviewerAgent", 1750, False, TEXT),
                Paragraph("- analiza oferta y CV en una sola llamada", 1750, False, TEXT),
                Paragraph("- genera score ATS, cambios y CV final", 1750, False, TEXT),
            ],
        ),
        *footer(6, "Grafo"),
    ]
    return slide_xml(shapes)


def real_agents_slide() -> str:
    shapes = title_band("Que Hace Cada Modulo", "ACLARACION TECNICA")
    shapes += [
        filled_box(10, "Top", emu(0.9), emu(2.05), emu(11.4), emu(0.8), "FFF8EF", "F7DFC2"),
        text_box(11, "TopText", emu(1.2), emu(2.28), emu(10.6), emu(0.3), [Paragraph("No tenemos 5 agentes independientes en codigo. Tenemos 2 nodos y 1 agente principal unificado.", 1800, True, NAVY)]),
        filled_box(12, "Left", emu(0.9), emu(3.15), emu(5.4), emu(2.55), BOX_BG, LINE),
        filled_box(13, "Right", emu(6.0), emu(3.15), emu(6.3), emu(2.55), "F7FFFC", "D9F3EA"),
        text_box(14, "LeftTitle", emu(1.2), emu(3.45), emu(3.5), emu(0.3), [Paragraph("Job Matcher", 2200, True, BLUE)]),
        text_box(
            15,
            "LeftBody",
            emu(1.2),
            emu(3.95),
            emu(4.5),
            emu(1.4),
            [
                Paragraph("- recibe el texto del CV", 1750, False, TEXT),
                Paragraph("- busca en ofertas indexadas", 1750, False, TEXT),
                Paragraph("- selecciona la mejor coincidencia", 1750, False, TEXT),
            ],
        ),
        text_box(16, "RightTitle", emu(6.3), emu(3.45), emu(4.8), emu(0.3), [Paragraph("CV Reviewer Agent", 2200, True, TEAL)]),
        text_box(
            17,
            "RightBody",
            emu(6.3),
            emu(3.95),
            emu(5.2),
            emu(1.4),
            [
                Paragraph("- analiza la oferta", 1750, False, TEXT),
                Paragraph("- analiza el CV", 1750, False, TEXT),
                Paragraph("- reescribe y optimiza el CV", 1750, False, TEXT),
                Paragraph("- evalua ATS y recomienda mejoras", 1750, False, TEXT),
            ],
        ),
        *footer(7, "Modulos"),
    ]
    return slide_xml(shapes)


def risks_slide() -> str:
    shapes = title_band("Riesgos Reales y Como los Resolvimos", "APRENDIZAJES")
    ys = [2.15, 3.0, 3.85, 4.7]
    rows = [
        ("Docker + Ollama", "Dentro del contenedor localhost no apuntaba al host. Lo resolvimos con variables de entorno y host.docker.internal."),
        ("Embeddings y ofertas vacias", "Si Ollama o nomic-embed-text no estaban accesibles, la lista salia vacia. Alineamos la URL de API y RAG."),
        ("Respuesta JSON del LLM", "El modelo podia devolver JSON roto. Añadimos reintentos y reparacion basica del JSON."),
        ("Tests mezclados", "Las pruebas con Ollama estaban mezcladas con unitarias. Marcamos integration para separarlas mejor."),
    ]
    sid = 10
    for idx, (risk, solution) in enumerate(rows):
        shapes.append(filled_box(sid, f"Risk{idx}", emu(0.9), emu(ys[idx]), emu(11.4), emu(0.68), "FBFCFF", LINE))
        sid += 1
        shapes.append(text_box(sid, f"RiskTitle{idx}", emu(1.15), emu(ys[idx] + 0.18), emu(2.7), emu(0.22), [Paragraph(risk, 1800, True, RED)]))
        sid += 1
        shapes.append(text_box(sid, f"RiskBody{idx}", emu(3.25), emu(ys[idx] + 0.16), emu(8.6), emu(0.28), [Paragraph(solution, 1500, False, TEXT)]))
        sid += 1
    shapes += footer(8, "Riesgos")
    return slide_xml(shapes)


def demo_slide() -> str:
    shapes = title_band("Demo en Vivo", "PASO A PASO")
    steps = [
        ("1", "Abrir la web", "Mostrar health y ofertas cargadas."),
        ("2", "Subir CV", "Cargar un PDF o TXT de ejemplo."),
        ("3", "Ver matching", "Enseñar la oferta encontrada automaticamente."),
        ("4", "Revisar ATS", "Mostrar score, keywords y cambios."),
        ("5", "Descargar PDF", "Exportar el CV final optimizado."),
    ]
    x_positions = [0.9, 3.2, 5.5, 7.8, 10.1]
    sid = 10
    shapes.append(line_box(sid, emu(1.25), emu(3.0), emu(10.0), emu(0.02), LINE))
    sid += 1
    for i, (num, title, desc) in enumerate(steps):
        x = x_positions[i]
        shapes.append(filled_box(sid, f"Circle{i}", emu(x), emu(2.72), emu(0.5), emu(0.5), "FFFFFF", BLUE, "ellipse"))
        sid += 1
        shapes.append(text_box(sid, f"Num{i}", emu(x + 0.16), emu(2.82), emu(0.2), emu(0.2), [Paragraph(num, 1600, True, NAVY)]))
        sid += 1
        shapes.append(text_box(sid, f"StepTitle{i}", emu(x - 0.25), emu(3.45), emu(1.6), emu(0.3), [Paragraph(title, 1650, True, NAVY)]))
        sid += 1
        shapes.append(text_box(sid, f"StepDesc{i}", emu(x - 0.35), emu(3.82), emu(1.8), emu(0.8), [Paragraph(desc, 1400, False, MUTED)]))
        sid += 1
    shapes += footer(9, "Demo")
    return slide_xml(shapes)


def team_slide() -> str:
    shapes = title_band("Reparto de la Presentacion", "EQUIPO DE 3")
    cards = [
        ("Persona 1", "Idea y problema", ["que hace el proyecto", "que problema resuelve", "flujo general del usuario"]),
        ("Persona 2", "Stack y arquitectura", ["tecnologias usadas", "por que FastAPI, LangGraph y Ollama", "grafo real del sistema"]),
        ("Persona 3", "Riesgos y demo", ["problemas tecnicos reales", "como se resolvieron", "demo final del sistema"]),
    ]
    xs = [0.8, 4.35, 7.9]
    sid = 10
    for i, (person, role, points) in enumerate(cards):
        shapes.append(filled_box(sid, f"Card{i}", emu(xs[i]), emu(2.2), emu(3.15), emu(3.3), BOX_BG if i != 2 else "F7FFFC", LINE if i != 2 else "D9F3EA"))
        sid += 1
        shapes.append(text_box(sid, f"Person{i}", emu(xs[i] + 0.22), emu(2.48), emu(2.1), emu(0.25), [Paragraph(person, 1800, True, BLUE if i != 2 else TEAL)]))
        sid += 1
        shapes.append(text_box(sid, f"Role{i}", emu(xs[i] + 0.22), emu(2.86), emu(2.5), emu(0.28), [Paragraph(role, 1950, True, NAVY)]))
        sid += 1
        shapes.append(text_box(sid, f"Points{i}", emu(xs[i] + 0.22), emu(3.35), emu(2.65), emu(1.6), [Paragraph("- " + p, 1500, False, TEXT) for p in points]))
        sid += 1
    shapes.append(text_box(30, "BottomNote", emu(1.0), emu(5.95), emu(10.8), emu(0.45), [Paragraph("Consejo: si preguntan algo tecnico profundo, responde quien programo esa parte y el resto apoya con contexto breve.", 1500, False, MUTED)]))
    shapes += footer(10, "Equipo")
    return slide_xml(shapes)


def closing_slide() -> str:
    shapes = [
        line_box(2, 0, 0, SLIDE_W, emu(0.06), BLUE),
        line_box(3, emu(11.6), 0, emu(1.73), emu(0.06), TEAL),
        text_box(4, "Main", emu(3.8), emu(2.3), emu(4.2), emu(0.8), [Paragraph("Preguntas", 3400, True, NAVY)]),
        text_box(5, "Sub", emu(2.4), emu(3.2), emu(7.0), emu(0.5), [Paragraph("Podemos ampliar la demo, el grafo o las decisiones tecnicas.", 1800, False, MUTED)]),
        text_box(6, "End", emu(4.2), emu(5.9), emu(3.5), emu(0.3), [Paragraph("Gracias", 1600, True, BLUE)]),
        *footer(11, "Cierre"),
    ]
    return slide_xml(shapes)


def rels_xml(slide_count: int) -> str:
    slide_rels = []
    for idx in range(slide_count):
        rel_id = idx + 2
        slide_rels.append(
            f'<Relationship Id="rId{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{idx + 1}.xml"/>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  {''.join(slide_rels)}
</Relationships>
"""


def presentation_xml(slide_count: int) -> str:
    sld_ids = []
    for idx in range(slide_count):
        rid = idx + 2
        sld_ids.append(f'<p:sldId id="{256 + idx}" r:id="rId{rid}"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                saveSubsetFonts="1" autoCompressPictures="0">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
    {''.join(sld_ids)}
  </p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>
"""


SLIDE_LAYOUT_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>
"""


SLIDE_LAYOUT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""


SLIDE_MASTER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="Office Theme">
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rId1"/>
  </p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle><a:lvl1pPr algn="l"/></p:titleStyle>
    <p:bodyStyle><a:lvl1pPr marL="0" indent="0"/></p:bodyStyle>
    <p:otherStyle><a:lvl1pPr marL="0" indent="0"/></p:otherStyle>
  </p:txStyles>
</p:sldMaster>
"""


SLIDE_MASTER_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""


THEME_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
  <a:themeElements>
    <a:clrScheme name="Office">
      <a:dk1><a:srgbClr val="000000"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F2937"/></a:dk2>
      <a:lt2><a:srgbClr val="F8FAFC"/></a:lt2>
      <a:accent1><a:srgbClr val="3D7BFF"/></a:accent1>
      <a:accent2><a:srgbClr val="21C7A8"/></a:accent2>
      <a:accent3><a:srgbClr val="12213D"/></a:accent3>
      <a:accent4><a:srgbClr val="E35D6A"/></a:accent4>
      <a:accent5><a:srgbClr val="6B7280"/></a:accent5>
      <a:accent6><a:srgbClr val="94A3B8"/></a:accent6>
      <a:hlink><a:srgbClr val="2563EB"/></a:hlink>
      <a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Office">
      <a:majorFont>
        <a:latin typeface="Aptos Display"/>
        <a:ea typeface=""/>
        <a:cs typeface=""/>
      </a:majorFont>
      <a:minorFont>
        <a:latin typeface="Aptos"/>
        <a:ea typeface=""/>
        <a:cs typeface=""/>
      </a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
        <a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="25400" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="38100" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
        <a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
  <a:objectDefaults/>
  <a:extraClrSchemeLst/>
</a:theme>
"""


CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
  <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
</Types>
"""


ROOT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


PRES_PROPS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                  xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>
"""


VIEW_PROPS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
          xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:normalViewPr/>
  <p:slideViewPr>
    <p:cSldViewPr snapToGrid="1" snapToObjects="1"/>
  </p:slideViewPr>
  <p:outlineViewPr/>
  <p:notesTextViewPr/>
  <p:gridSpacing cx="78028800" cy="78028800"/>
</p:viewPr>
"""


TABLE_STYLES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>
"""


def app_xml(slide_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office PowerPoint</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{slide_count}</Slides>
  <Notes>0</Notes>
  <HiddenSlides>0</HiddenSlides>
  <MMClips>0</MMClips>
  <ScaleCrop>false</ScaleCrop>
  <HeadingPairs>
    <vt:vector size="2" baseType="variant">
      <vt:variant><vt:lpstr>Slides</vt:lpstr></vt:variant>
      <vt:variant><vt:i4>{slide_count}</vt:i4></vt:variant>
    </vt:vector>
  </HeadingPairs>
  <TitlesOfParts>
    <vt:vector size="{slide_count}" baseType="lpstr">
      {''.join(f'<vt:lpstr>Slide {i}</vt:lpstr>' for i in range(1, slide_count + 1))}
    </vt:vector>
  </TitlesOfParts>
  <Company>OpenAI</Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>16.0000</AppVersion>
</Properties>
"""


def core_xml() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Optimizador de CV - Presentacion corregida</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


def slide_rel_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>
"""


def build_presentation(out_path: Path) -> None:
    slides = [
        cover_slide(),
        bullet_slide(
            2,
            "Problema y Solucion",
            "DESAFIO DEL MERCADO",
            "El problema",
            [
                "Muchos CV no superan filtros ATS.",
                "Faltan keywords y contexto de oferta.",
                "Adaptar un CV a mano lleva tiempo.",
            ],
            "La solucion",
            [
                "Matching automatico con ofertas reales.",
                "Revision contextual del CV con IA local.",
                "Salida final con score ATS y PDF descargable.",
            ],
            "Analisis",
        ),
        project_idea_slide(),
        stack_slide(),
        graph_slide(),
        real_agents_slide(),
        risks_slide(),
        demo_slide(),
        team_slide(),
        bullet_slide(
            10,
            "Resultados Actuales del Sistema",
            "SIN INFLAR METRICAS",
            "Lo que ya hace",
            [
                "Encuentra la oferta mas compatible.",
                "Devuelve score ATS y keywords.",
                "Genera un CV optimizado descargable.",
            ],
            "Lo que mostramos en la demo",
            [
                "Carga de CV en la web.",
                "Matching automatico de oferta.",
                "Analisis final y exportacion PDF.",
            ],
            "Resultados",
        ),
        closing_slide(),
    ]

    content_types = CONTENT_TYPES_XML.replace(
        "</Types>",
        "".join(
            f'\n  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            for i in range(1, len(slides) + 1)
        )
        + "\n</Types>",
    )

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", ROOT_RELS_XML)
        zf.writestr("docProps/app.xml", app_xml(len(slides)))
        zf.writestr("docProps/core.xml", core_xml())
        zf.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        zf.writestr("ppt/_rels/presentation.xml.rels", rels_xml(len(slides)))
        zf.writestr("ppt/presProps.xml", PRES_PROPS_XML)
        zf.writestr("ppt/viewProps.xml", VIEW_PROPS_XML)
        zf.writestr("ppt/tableStyles.xml", TABLE_STYLES_XML)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER_XML)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS_XML)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT_XML)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS_XML)
        zf.writestr("ppt/theme/theme1.xml", THEME_XML)

        for i, slide in enumerate(slides, start=1):
            zf.writestr(f"ppt/slides/slide{i}.xml", slide)
            zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rel_xml())


def main() -> None:
    out_dir = Path.cwd() / "docs"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "Optimizador_de_CV_corregido.pptx"
    build_presentation(out_path)
    print(out_path)


if __name__ == "__main__":
    main()
