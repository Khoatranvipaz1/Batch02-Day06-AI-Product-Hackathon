from __future__ import annotations

import html
import zipfile
from pathlib import Path


OUT = Path(__file__).resolve().parents[1] / "ShopeeFood_AI_SPEC_Flow_Deck.pptx"

SLIDES = [
    {
        "kicker": "AI Product Hackathon",
        "title": "ShopeeFood AI Chatbot",
        "subtitle": "SPEC + flow demo cho chatbot goi y mon an Quan 1",
        "claim": "Một lát cắt nhỏ nhưng chứng minh được AI chạy thật: hiểu nhu cầu, lấy dữ liệu món, và trả lời có kiểm soát.",
        "bullets": [
            "Track: Food & Local Delivery",
            "Prototype: React frontend + FastAPI backend",
            "AI flow: parser prompt -> retrieval -> final answer prompt",
        ],
        "placeholder": "ẢNH GIAO DIỆN\nHome / Chat screen",
    },
    {
        "kicker": "SPEC | Problem",
        "title": "Người dùng mất thời gian để chọn món đúng ngữ cảnh",
        "subtitle": "Pain point được chọn cho lát cắt build",
        "claim": "Khi đói, người dùng thường không muốn lọc thủ công theo giá, tốc độ giao, khẩu vị, dị ứng và món phù hợp.",
        "bullets": [
            "Nhu cầu thật thường là câu tự nhiên: “dưới 50k”, “giao nhanh”, “không hải sản”.",
            "Filter truyền thống bắt người dùng tự dịch nhu cầu thành nhiều thao tác.",
            "AI có thể biến câu nói thành intent/filter rồi chỉ đề xuất món trong dữ liệu.",
        ],
        "placeholder": "ẢNH GIAO DIỆN\nBefore / pain point",
    },
    {
        "kicker": "SPEC | Build Slice",
        "title": "Lát cắt demo: một người dùng, một câu hỏi, một danh sách món",
        "subtitle": "Scope rõ để build nhanh và kiểm chứng được",
        "claim": "Prototype không cố làm toàn bộ app giao đồ ăn; chỉ chứng minh flow gợi ý món từ chat.",
        "bullets": [
            "User: người đang chọn món ở Quận 1.",
            "Job: nói nhu cầu bằng tiếng Việt tự nhiên.",
            "AI decision: parse intent, entity, filter, ranking.",
            "Output: 1-3 món phù hợp, lý do chọn, cảnh báo nếu chỉ gần đúng.",
        ],
        "placeholder": "ẢNH GIAO DIỆN\nChat result / cards",
    },
    {
        "kicker": "AI Flow",
        "title": "Luồng AI có kiểm soát, không trả lời tự do",
        "subtitle": "Pipeline hiện tại trong code",
        "claim": "Bot đi qua dữ liệu có cấu trúc trước khi trả lời, giúp giảm bịa món, giá, quán.",
        "flow": [
            "User message",
            "NLU prompt\nfood_task.v1",
            "SQLite retrieval\nmock data",
            "Final answer prompt",
            "Chat response",
        ],
        "bullets": [
            "Prompt 1 tạo JSON task: intent, filters, entities, ranking.",
            "Retriever chỉ lấy món trong mock data ShopeeFood Q1.",
            "Prompt 2 trả lời ngắn gọn, không bịa dữ liệu ngoài retrieved_data.",
        ],
        "placeholder": "ẢNH GIAO DIỆN\nAI debug / response",
    },
    {
        "kicker": "Trust & Scope",
        "title": "Ngoài scope thì hỏi lại, không trả lời lan man",
        "subtitle": "Thiết kế cho đường lỗi và câu hỏi nhiễu",
        "claim": "Nếu người dùng hỏi ngoài phạm vi món ăn, bot chuyển sang clarify thay vì cố trả lời.",
        "bullets": [
            "Input ngoài scope: “Hôm nay thời tiết thế nào?”",
            "Task: intent=unknown, task_type=clarify_food_need.",
            "Response: “Bạn muốn mình gợi ý món theo tiêu chí nào: giá, món, độ cay, healthy hay giao nhanh?”",
            "Không query món ăn khi nhu cầu chưa rõ.",
        ],
        "placeholder": "ẢNH GIAO DIỆN\nOut-of-scope state",
    },
    {
        "kicker": "Evidence",
        "title": "Eval prompt: 6/6 case pass offline",
        "subtitle": "Bằng chứng demo cho SPEC và AI flow",
        "claim": "Bộ eval kiểm tra cả happy path và error recovery: budget, allergen, healthy, spicy, group order, ngoài scope.",
        "bullets": [
            "Eval cases nằm ở codebase/evals/eval_cases.json.",
            "Script chạy: codebase/evals/run_eval.py.",
            "Kết quả hiện tại: 6/6 passed với parser rules + template answer.",
            "Khi có API key có thể chạy lại parse-mode api + answer-mode api.",
        ],
        "placeholder": "ẢNH GIAO DIỆN\nEval result / terminal",
    },
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        write_content_types(z)
        write_rels(z)
        write_presentation(z)
        write_theme(z)
        write_slide_master(z)
        write_slide_layout(z)
        for idx, slide in enumerate(SLIDES, start=1):
            z.writestr(f"ppt/slides/slide{idx}.xml", slide_xml(idx, slide))
            z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide_rels())
    print(OUT)


def write_content_types(z: zipfile.ZipFile) -> None:
    overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, len(SLIDES) + 1)
    )
    z.writestr(
        "[Content_Types].xml",
        f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {overrides}
</Types>''',
    )


def write_rels(z: zipfile.ZipFile) -> None:
    z.writestr(
        "_rels/.rels",
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>''',
    )
    slide_rels_xml = "\n".join(
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, len(SLIDES) + 1)
    )
    z.writestr(
        "ppt/_rels/presentation.xml.rels",
        f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {slide_rels_xml}
  <Relationship Id="rId{len(SLIDES) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId{len(SLIDES) + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>''',
    )
    z.writestr(
        "ppt/slideMasters/_rels/slideMaster1.xml.rels",
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>''',
    )
    z.writestr(
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels",
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>''',
    )
    z.writestr(
        "docProps/core.xml",
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>ShopeeFood AI SPEC Flow Deck</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
</cp:coreProperties>''',
    )
    z.writestr(
        "docProps/app.xml",
        f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft PowerPoint</Application>
  <PresentationFormat>Widescreen</PresentationFormat>
  <Slides>{len(SLIDES)}</Slides>
</Properties>''',
    )


def write_presentation(z: zipfile.ZipFile) -> None:
    slide_ids = "\n".join(
        f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, len(SLIDES) + 1)
    )
    z.writestr(
        "ppt/presentation.xml",
        f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{len(SLIDES) + 1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>''',
    )


def write_theme(z: zipfile.ZipFile) -> None:
    z.writestr(
        "ppt/theme/theme1.xml",
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Spec Flow">
  <a:themeElements>
    <a:clrScheme name="Spec Flow">
      <a:dk1><a:srgbClr val="111827"/></a:dk1><a:lt1><a:srgbClr val="F8FAFC"/></a:lt1>
      <a:dk2><a:srgbClr val="2F4858"/></a:dk2><a:lt2><a:srgbClr val="EEF2F7"/></a:lt2>
      <a:accent1><a:srgbClr val="0F766E"/></a:accent1><a:accent2><a:srgbClr val="F59E0B"/></a:accent2>
      <a:accent3><a:srgbClr val="E11D48"/></a:accent3><a:accent4><a:srgbClr val="2563EB"/></a:accent4>
      <a:accent5><a:srgbClr val="64748B"/></a:accent5><a:accent6><a:srgbClr val="22C55E"/></a:accent6>
      <a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="Spec Flow"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>
  </a:themeElements>
</a:theme>''',
    )


def write_slide_master(z: zipfile.ZipFile) -> None:
    z.writestr(
        "ppt/slideMasters/slideMaster1.xml",
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>''',
    )


def write_slide_layout(z: zipfile.ZipFile) -> None:
    z.writestr(
        "ppt/slideLayouts/slideLayout1.xml",
        '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
</p:sldLayout>''',
    )


def slide_rels() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>'''


def slide_xml(idx: int, slide: dict[str, object]) -> str:
    shapes = [
        rect(0, 0, 12192000, 6858000, "F8FAFC", None, 2),
        rect(0, 0, 305000, 6858000, "0F766E", None, 3),
        text_box(610000, 360000, 2200000, 240000, str(slide["kicker"]).upper(), 1200, "0F766E", 4, bold=True),
        text_box(610000, 760000, 5600000, 960000, str(slide["title"]), 3000, "111827", 5, bold=True),
        text_box(610000, 1730000, 5400000, 360000, str(slide["subtitle"]), 1300, "475569", 6),
        text_box(610000, 2280000, 5200000, 760000, str(slide["claim"]), 1650, "1F2937", 7, bold=True),
        bullet_box(800000, 3300000, 5200000, 2200000, list(slide.get("bullets", [])), 8),
        placeholder_box(7000000, 900000, 4450000, 4200000, str(slide["placeholder"]), 20),
        text_box(9800000, 6220000, 1350000, 220000, f"{idx:02d} / {len(SLIDES):02d}", 900, "64748B", 30),
    ]
    if "flow" in slide:
        shapes.extend(flow_shapes(list(slide["flow"])))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>
    {''.join(shapes)}
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def flow_shapes(items: list[str]) -> list[str]:
    shapes: list[str] = []
    x = 690000
    y = 5750000
    w = 1700000
    h = 460000
    gap = 210000
    for i, item in enumerate(items):
        sid = 100 + i
        shapes.append(rect(x + i * (w + gap), y, w, h, "FFFFFF", "0F766E", sid, radius=True))
        shapes.append(text_box(x + i * (w + gap) + 120000, y + 85000, w - 240000, h - 90000, item, 920, "0F172A", sid + 10, bold=True))
        if i < len(items) - 1:
            ax = x + i * (w + gap) + w + 40000
            shapes.append(text_box(ax, y + 120000, 130000, 160000, ">", 1200, "F59E0B", sid + 20, bold=True))
    return shapes


def rect(x: int, y: int, w: int, h: int, fill: str, line: str | None, sid: int, radius: bool = False) -> str:
    preset = "roundRect" if radius else "rect"
    line_xml = "<a:ln><a:noFill/></a:ln>" if line is None else f'<a:ln w="19050"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
    return f'''<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Rectangle {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="{preset}"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>{line_xml}</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>'''


def placeholder_box(x: int, y: int, w: int, h: int, text: str, sid: int) -> str:
    return f'''<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Picture Placeholder"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="EEF2F7"/></a:solidFill><a:ln w="28575"><a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill><a:prstDash val="dash"/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" anchor="ctr"/><a:lstStyle/><a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="vi-VN" sz="1800" b="1"><a:solidFill><a:srgbClr val="64748B"/></a:solidFill></a:rPr><a:t>{esc(text)}</a:t></a:r></a:p><a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="vi-VN" sz="950"><a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill></a:rPr><a:t>Thay khung này bằng screenshot sau</a:t></a:r></a:p></p:txBody></p:sp>'''


def text_box(x: int, y: int, w: int, h: int, text: str, size: int, color: str, sid: int, bold: bool = False) -> str:
    paras = "".join(
        f'<a:p><a:r><a:rPr lang="vi-VN" sz="{size}"{" b=\"1\"" if bold else ""}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{esc(line)}</a:t></a:r></a:p>'
        for line in text.split("\n")
    )
    return f'''<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Text {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{paras}</p:txBody></p:sp>'''


def bullet_box(x: int, y: int, w: int, h: int, bullets: list[str], sid: int) -> str:
    paras = ""
    for bullet in bullets:
        paras += f'''<a:p><a:pPr marL="285750" indent="-171450"><a:buChar char="•"/></a:pPr><a:r><a:rPr lang="vi-VN" sz="1280"><a:solidFill><a:srgbClr val="334155"/></a:solidFill></a:rPr><a:t>{esc(bullet)}</a:t></a:r></a:p>'''
    return f'''<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Bullets {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{paras}</p:txBody></p:sp>'''


def esc(value: str) -> str:
    return html.escape(value, quote=False)


if __name__ == "__main__":
    main()
