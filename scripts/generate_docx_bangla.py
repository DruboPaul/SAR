import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_heading_styled(doc, text, level):
    h = doc.add_heading(text, level=level)
    run = h.runs[0]
    run.font.name = 'Calibri'
    run.font.size = Pt(16 if level == 1 else 13)
    run.font.bold = True
    run.font.color.rgb = RGBColor(31, 78, 121)
    h.paragraph_format.space_before = Pt(18)
    h.paragraph_format.space_after = Pt(6)
    return h

def add_para(doc, text, bold_prefix=None, space_after=10):
    p = doc.add_paragraph()
    if bold_prefix:
        run_b = p.add_run(bold_prefix)
        run_b.bold = True
        run_b.font.size = Pt(11)
    p.add_run(text).font.size = Pt(11)
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_table_from_data(doc, headers, data, header_bg="1F4E79"):
    table = doc.add_table(rows=1 + len(data), cols=len(headers))
    table.style = 'Light Shading Accent 1'
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        set_cell_background(hdr[i], header_bg)
        set_cell_margins(hdr[i])
        for run in hdr[i].paragraphs[0].runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)
    for ri, row_data in enumerate(data):
        row = table.rows[ri + 1].cells
        bg = "F2F2F2" if ri % 2 == 1 else "FFFFFF"
        for ci, val in enumerate(row_data):
            row[ci].text = str(val)
            set_cell_background(row[ci], bg)
            set_cell_margins(row[ci])
            for run in row[ci].paragraphs[0].runs:
                run.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return table

def add_file_list(doc, title, files):
    p = doc.add_paragraph()
    run_t = p.add_run(title)
    run_t.bold = True
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(31, 78, 121)
    for f in files:
        bp = doc.add_paragraph(style='List Bullet')
        run_f = bp.add_run(f)
        run_f.font.size = Pt(10)
        run_f.font.color.rgb = RGBColor(80, 80, 80)
        bp.paragraph_format.space_after = Pt(2)

def main():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor(51, 51, 51)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("পদ্ধতিগত সংশোধন এবং প্রযুক্তিগত ন্যায্যতা")
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = RGBColor(31, 78, 121)
    title.paragraph_format.space_after = Pt(6)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = subtitle.add_run("HydroSAR-BD: স্পেশিও-টেম্পোরালি অ্যাডাপটিভ SAR ওয়াটার ডিটেকশন ফ্রেমওয়ার্ক")
    r2.font.size = Pt(12)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(100, 100, 100)
    subtitle.paragraph_format.space_after = Pt(24)

    # =========================================================
    # ISSUE 1
    # =========================================================
    add_heading_styled(doc, "ইস্যু ১: গ্রাউন্ড ট্রুথিং এবং একুরেসি অ্যাসেসমেন্ট (৪,৩১০ পয়েন্ট)", level=1)

    add_para(doc,
        "আত্মনির্ভরশীল মানদণ্ডের (self-referential benchmarks) উপর নির্ভর না করে শ্রেণিবিভাগের "
        "নির্ভুলতা কঠোরভাবে যাচাই করতে, ১১ বছরের বেসলাইন (২০১৫-২০২৫) জুড়ে একটি সম্ভাব্যতা-ভিত্তিক "
        "স্তরীকৃত র‍্যান্ডম স্যাম্পলিং ডিজাইন ব্যবহার করা হয়েছে।",
        bold_prefix="উদ্দেশ্য: ")

    add_heading_styled(doc, "১.১ পদ্ধতি ১: ৪,৩১০টি গ্রাউন্ড ট্রুথ পয়েন্ট কীভাবে সংগ্রহ করা হয়েছে?", level=2)
    add_para(doc,
        "একটি মিশ্র পদ্ধতি (Mixed Method) ব্যবহার করা হয়েছে যেখানে মাঠ পরিদর্শন এবং রিমোট ভিজ্যুয়াল "
        "ইন্টারপ্রিটেশন একত্রিত করা হয়েছে:\n"
        "• ধাপ ১ – স্থানিক স্যাম্পলিং ডিজাইন: বাংলাদেশের সকল ভূ-প্রাকৃতিক অঞ্চল জুড়ে ঐতিহাসিক পানির "
        "স্থায়িত্ব শ্রেণি অনুযায়ী ৫০০টি ভৌগোলিক টার্গেট হাব সমানভাবে বিতরণ করা হয়েছে।\n"
        "• ধাপ ২ – মাঠ পর্যায়ে GPS সার্ভে: প্রতিটি প্রবেশযোগ্য হাবে হ্যান্ডহেল্ড GPS রিসিভার ব্যবহার করে "
        "সরাসরি মাঠে গিয়ে স্থানাঙ্ক (coordinates) এবং বাইনারি পানির উপস্থিতি/অনুপস্থিতি (W ∈ {0, 1}) রেকর্ড "
        "করা হয়েছে। ২০২৫ সালে শুষ্ক মৌসুম এবং বর্ষা মৌসুম উভয় সময়ে একাধিক ফিল্ড ক্যাম্পেইনে এটি করা হয়েছে।\n"
        "• ধাপ ৩ – রিমোট ভিজ্যুয়াল ভেরিফিকেশন: দুর্গম বা প্রত্যন্ত অঞ্চলের জন্য সেন্টিনেল-২ এবং "
        "ল্যান্ডস্যাটের উচ্চ-রেজোলিউশন, মেঘমুক্ত অপটিক্যাল ইমেজ ব্যবহার করে ভ্যালিডেশন করা হয়েছে এবং "
        "Google Earth Pro দিয়ে ক্রস-রেফারেন্সিং করা হয়েছে।")

    add_heading_styled(doc, "১.২ ডেটা: শ্রেণিভিত্তিক পয়েন্ট বিতরণ (কোঅর্ডিনেট, বছর, মাস সহ)", level=2)
    add_para(doc,
        "৪,৩১০টি মাঠ-যাচাইকৃত স্থানাঙ্ক JRC Global Surface Water (GSW) Occurrence frequency layer "
        "ব্যবহার করে পোস্ট-স্ট্র্যাটিফাই করা হয়েছে। সকল পয়েন্ট JRC occurrence অনুযায়ী "
        "অবরোহ ক্রমে (descending, stable sort) সাজানো হয়েছে এবং ইনডেক্স স্লাইসিংয়ের মাধ্যমে ৪টি "
        "হাইড্রোপিরিয়ড শ্রেণিতে ভাগ করা হয়েছে। ডেটায় প্রাপ্ত প্রকৃত JRC occurrence রেঞ্জগুলো হলো:")

    add_table_from_data(doc,
        ["হাইড্রোপিরিয়ড শ্রেণি", "নমুনা সংখ্যা (N)", "JRC Occurrence রেঞ্জ", "বিবরণ"],
        [
            ["স্থায়ী (Permanent)", "৭০০", "৬৯% – ১০০%", "নদী, গভীর বিল, বারোমাসি হ্রদ"],
            ["আধা-স্থায়ী (Semi-perm.)", "৭০০", "৩৬% – ৬৯%", "মৌসুমি প্লাবনভূমি, ঘের"],
            ["ক্ষণস্থায়ী (Ephemeral)", "৫২৮", "১০% – ৩৬%", "আকস্মিক বন্যা, চর, ক্ষণস্থায়ী প্লাবন"],
            ["অ-জলাভূমি (Non-water)", "২,৩৮২", "০% – ১০%", "বন, বসতি, শুষ্ক কৃষিজমি, মাটি"]
        ])

    add_para(doc,
        "গুরুত্বপূর্ণ বিষয়: শ্রেণির সীমানা কঠিন শতাংশ থ্রেশহোল্ড দ্বারা নয়, বরং ইনডেক্স স্লাইসিং "
        "(অবস্থান ৭০০, ১৪০০, ১৯২৮) দ্বারা নির্ধারিত হয়। এটি নিশ্চিত করে যে প্রতিটি স্তরে নির্দিষ্ট, "
        "প্রতিনিধিত্বমূলক নমুনা আকার বজায় থাকে।",
        bold_prefix="দ্রষ্টব্য: ")

    add_para(doc,
        "৪,৩১০টি পয়েন্টের সম্পূর্ণ তালিকা (অক্ষাংশ, দ্রাঘিমাংশ, মাস, বছর, JRC Occurrence %, "
        "ফিল্ড ট্রুথ, ST-GMM প্রেডিকশন সহ) সাপ্লিমেন্টারি CSV ফাইলে দেওয়া আছে: "
        "Supplementary_Table_Validation_Points.csv",
        bold_prefix="সাপ্লিমেন্টারি ডেটা: ")

    add_heading_styled(doc, "১.৩ পদ্ধতি ২: একুরেসি টেস্ট কীভাবে পরিচালনা করা হয়েছে?", level=2)
    add_para(doc,
        "একুরেসি অ্যাসেসমেন্ট Spatial Confusion Matrix পদ্ধতিতে পরিচালিত হয়েছে:\n"
        "• প্রতিটি হাইড্রোপিরিয়ড শ্রেণির জন্য ST-GMM প্রেডিকশন এবং মাঠ-যাচাইকৃত গ্রাউন্ড ট্রুথের "
        "মধ্যে একটি বাইনারি কনফিউশন ম্যাট্রিক্স তৈরি করা হয়েছে।\n"
        "• প্রতিটি ম্যাট্রিক্স থেকে True Positives (TP), False Positives (FP), False Negatives (FN), "
        "এবং True Negatives (TN) বের করা হয়েছে।\n"
        "• User's Accuracy (UA = TP/(TP+FP)), Producer's Accuracy (PA = TP/(TP+FN)), এবং Overall Accuracy "
        "(OA = (TP+TN)/N) প্রতিটি শ্রেণির জন্য হিসাব করা হয়েছে।\n"
        "• সমগ্র ৪,৩১০-পয়েন্ট ডেটাসেটের জন্য Cohen's Kappa (κ) হিসাব করা হয়েছে।\n"
        "• প্রস্তাবিত ST-GMM পদ্ধতি এবং প্রচলিত Otsu থ্রেশহোল্ডিং-এর পরিসংখ্যানগত তুলনার জন্য "
        "McNemar's Chi-Square Test (χ²) প্রয়োগ করা হয়েছে।")

    add_heading_styled(doc, "১.৪ ফলাফল: বিস্তারিত একুরেসি মেট্রিক্স", level=2)

    add_table_from_data(doc,
        ["শ্রেণি", "N", "TP", "FP", "FN", "TN", "UA (%)", "PA (%)", "OA (%)"],
        [
            ["স্থায়ী (Permanent)", "৭০০", "৪৩৫", "৮০", "৯", "১৭৬", "৮৪.৪৭", "৯৭.৯৭", "৮৭.২৯"],
            ["আধা-স্থায়ী (Semi-perm.)", "৭০০", "৩৮৫", "৬১", "১১", "২৪৩", "৮৬.৩২", "৯৭.২২", "৮৯.৭১"],
            ["ক্ষণস্থায়ী (Ephemeral)", "৫২৮", "২৪০", "৩৬", "৬", "২৪৬", "৮৬.৯৬", "৯৭.৫৬", "৯২.০৫"],
            ["অ-জলাভূমি (Non-water)", "২,৩৮২", "৮০৬", "৮২", "৩৬", "১,৪৫৮", "৯০.৭৭", "৯৫.৭২", "৯৫.০৫"]
        ])

    add_para(doc,
        "• সামগ্রিক নির্ভুলতা (Overall Accuracy, OA): ৯২.৫৫%\n"
        "• কোহেনের কাপ্পা (Cohen's Kappa, κ): ০.৮৫০৮\n"
        "• ম্যাকনেমারের χ² (ST-GMM বনাম Otsu): ১৪২.৭৬ (p < 0.001) — এটি নিশ্চিত করে যে ST-GMM "
        "প্রচলিত Otsu থ্রেশহোল্ডিংয়ের চেয়ে পরিসংখ্যানগতভাবে উল্লেখযোগ্যভাবে উন্নত।\n"
        "• ভারসাম্যপূর্ণ নির্ভুলতা (Balanced Accuracy): ৯১.২% (নিশ্চিত করে যে উচ্চ OA শ্রেণি "
        "ভারসাম্যহীনতার কারণে নয়)।",
        bold_prefix="সামগ্রিক মেট্রিক্স:\n")

    add_file_list(doc, "সংশ্লিষ্ট ডেটা ফাইলসমূহ:", [
        "Sub_issue1/Supplementary_Table_Validation_Points.csv (৪,৩১০ পয়েন্টের সম্পূর্ণ তালিকা)",
        "Sub_issue1/per_class_accuracy.csv (শ্রেণিভিত্তিক একুরেসি মেট্রিক্স)",
        "Sub_issue1/overall_validation_metrics.csv (সামগ্রিক OA, Kappa, McNemar's test)"
    ])
    add_file_list(doc, "ব্যবহৃত কোড:", [
        "python_scripts/10_calculate_detailed_validation_metrics.py"
    ])

    doc.add_page_break()

    # =========================================================
    # ISSUE 2
    # =========================================================
    add_heading_styled(doc, "ইস্যু ২: সেন্টিনেল-২ NDWI এর বিপরীতে ক্রস-সেন্সর স্থানিক বেঞ্চমার্কিং", level=1)

    add_para(doc,
        "বর্ষা মৌসুমে প্রস্তাবিত রাডার-ভিত্তিক ST-GMM মডেলের স্থানিক বিশ্বস্ততা (spatial fidelity) "
        "যাচাই করার জন্য, অপটিক্যাল ইমেজের বিপরীতে একটি স্বাধীন পিক্সেল-পর্যায়ের ক্রস-সেন্সর "
        "বেঞ্চমার্কিং পরীক্ষা পরিচালনা করা হয়েছে।",
        bold_prefix="উদ্দেশ্য: ")

    add_heading_styled(doc, "২.১ প্রয়োগকৃত প্রক্রিয়া", level=2)
    add_para(doc,
        "১. অপটিক্যাল রেফারেন্স মাস্ক: গাজীপুর জেলার ওপর একটি মেঘমুক্ত সেন্টিনেল-২ MSI কম্পোজিট "
        "সংগ্রহ করা হয়েছে (সেপ্টেম্বর ২০২০)। Green (Band 3) এবং Near-Infrared (Band 8) ব্যান্ড ব্যবহার "
        "করে Normalized Difference Water Index (NDWI) হিসাব করা হয়েছে:\n"
        "    NDWI = (Green − NIR) / (Green + NIR)\n"
        "একটি স্ট্যান্ডার্ড থ্রেশহোল্ড (NDWI > 0.0) প্রয়োগ করে বাইনারি অপটিক্যাল রেফারেন্স ওয়াটার মাস্ক "
        "তৈরি করা হয়েছে।\n\n"
        "২. SAR প্রস্তাবিত মাস্ক: একই এলাকা ও সময়ের সেন্টিনেল-১ SAR VV-ব্যাকস্ক্যাটার ইমেজ "
        "প্রস্তাবিত ST-GMM অ্যাডাপটিভ থ্রেশহোল্ড ব্যবহার করে প্রসেস করা হয়েছে।\n\n"
        "৩. পিক্সেল-পর্যায়ের তুলনা: উভয় মাস্ক একটি সাধারণ ১০-মিটার স্থানিক গ্রিডে সারিবদ্ধ করে "
        "হুবহু পিক্সেল-বাই-পিক্সেল তুলনা করা হয়েছে।")

    add_heading_styled(doc, "২.২ ফলাফলের বিবরণ", level=2)
    add_para(doc,
        "• পিক্সেল-পর্যায়ের সম্মতি (Pixel-level Agreement): ৯৭.৯%\n"
        "  উভয় সেন্সর কতশতাংশ পিক্সেলে একই শ্রেণিবিভাগ (উভয়ই পানি বা উভয়ই স্থল) করেছে তার শতাংশ:\n"
        "  Agreement = (TP + TN) / Total Pixels = ০.৯৭৯\n\n"
        "• ইন্টারসেকশন ওভার ইউনিয়ন (IoU): ০.৮৯৬\n"
        "  শুধুমাত্র শনাক্তকৃত জলাশয়ের স্থানিক ওভারল্যাপ পরিমাপ করে:\n"
        "  IoU = |A ∩ B| / |A ∪ B| = TP / (TP + FP + FN) = ০.৮৯৬\n\n"
        "০.৮৯৬ IoU নিশ্চিত করে যে প্রস্তাবিত রাডার পদ্ধতি 'মিসিং মনসুন' সমস্যার সমাধান করে — "
        "যেখানে সেন্টিনেল-২ এবং ল্যান্ডস্যাট মেঘের কারণে সম্পূর্ণ অকার্যকর হয়ে পড়ে।",
        bold_prefix="ক্রস-সেন্সর বেঞ্চমার্কিং মেট্রিক্স:\n")

    add_heading_styled(doc, "২.৩ তুলনামূলক মডেল বেঞ্চমার্কিং", level=2)
    add_para(doc,
        "তিনটি বিকল্প পদ্ধতির বিপরীতে একটি পদ্ধতিগত বেঞ্চমার্কিং পরীক্ষা পরিচালনা করা হয়েছে:")

    add_table_from_data(doc,
        ["পদ্ধতি", "OA (%)", "κ", "F1", "CE (%)", "OE (%)", "ভিত্তি"],
        [
            ["Random Forest (RF)", "৯৩.৮০", "০.৮৭", "০.৯৪", "১০.৮", "৩.৫", "সুপারভাইজড (GEE)"],
            ["ST-GMM (এই গবেষণা)", "৯২.৫৫", "০.৮৫", "০.৯২", "১২.২", "৩.২", "প্রোবাবিলিস্টিক EM"],
            ["Otsu থ্রেশহোল্ডিং", "৮৬.৯০", "০.৭৪", "০.৮৫", "১৭.৬", "৫.৯", "আনকনস্ট্রেইন্ড"]
        ])

    add_para(doc,
        "CE = কমিশন ত্রুটি (FP/(TP+FP)); OE = ওমিশন ত্রুটি (FN/(TP+FN))।\n"
        "ST-GMM উল্লেখযোগ্যভাবে Otsu পদ্ধতিকে ছাড়িয়ে গেছে (χ² = ১৪২.৮, p < 0.001)। "
        "সুপারভাইজড RF সামান্য বেশি একুরেসি দিলেও (৯৩.৮০%), ST-GMM ML বেসলাইনের ১.৩%-এর মধ্যে "
        "থেকে সম্পূর্ণ ভৌতিক ব্যাখ্যাযোগ্যতা (physical interpretability) বজায় রেখেছে।",
        bold_prefix="দ্রষ্টব্য: ")

    add_file_list(doc, "সংশ্লিষ্ট ডেটা ফাইলসমূহ:", [
        "Sub_issue2/Figure_5Panel_Comparative_Map.png (৫-প্যানেল তুলনামূলক ম্যাপ)",
        "data/Task1_Rasters/ (মূল GeoTIFF রাস্টার ফাইলসমূহ)"
    ])
    add_file_list(doc, "ব্যবহৃত কোড:", [
        "python_scripts/05_plot_comparative_map.py",
        "Reviewer_Revisions/Task1_5Panel_Map/GEE_Task1_Export_Script.js"
    ])

    doc.add_page_break()

    # =========================================================
    # ISSUE 3
    # =========================================================
    add_heading_styled(doc, "ইস্যু ৩: স্বাধীন মূল্যায়ন — JRC Occurrence এবং ফিল্ড পয়েন্ট ক্রস-বেঞ্চমার্কিং", level=1)

    add_para(doc,
        "মাঠ পর্যবেক্ষণ এবং JRC ডেটা কীভাবে পারস্পরিকভাবে সম্পর্কিত, এবং occurrence শতাংশ "
        "কীভাবে প্রতি-শ্রেণি হাইড্রোপিরিয়ড ক্যাটাগরিতে রূপান্তরিত হয়েছে তা স্পষ্ট করা।",
        bold_prefix="উদ্দেশ্য: ")

    add_heading_styled(doc, "৩.১ স্পষ্টীকরণ: একটিই ভ্যালিডেশন ডেটাসেট আছে", level=2)
    add_para(doc,
        "দুটি পৃথক ভৌত ডেটাসেট নেই। ভ্যালিডেশন ওয়ার্কফ্লো একটি একক সমন্বিত প্রক্রিয়া:\n"
        "• ৪,৩১০টি স্থানিক স্থানাঙ্ক এবং গ্রাউন্ড-ট্রুথ মান (পানি বনাম স্থল) ২০২৫ সালে মাঠ পর্যায়ে "
        "সংগ্রহ করা হয়েছে।\n"
        "• এরপর JRC Global Surface Water Occurrence frequency (১৯৮৪-২০২১) প্রতিটি পয়েন্টের স্থানাঙ্কে "
        "একটি ঐতিহাসিক বৈশিষ্ট্য (historical attribute) হিসেবে এক্সট্র্যাক্ট করা হয়েছে। এই occurrence "
        "মান (০% থেকে ১০০%) নির্দেশ করে যে ল্যান্ডস্যাট দ্বারা বহু-দশকীয় বেসলাইনে কতবার একটি নির্দিষ্ট "
        "পিক্সেল পানি হিসেবে পর্যবেক্ষিত হয়েছে।\n"
        "• সুতরাং, ২০২৫ ফিল্ড পয়েন্ট হলো স্থানিক রেফারেন্স (কোথায় এবং কী), এবং JRC occurrence হলো "
        "ঐতিহাসিক স্তরীকরণ বৈশিষ্ট্য (সেখানে ঐতিহাসিকভাবে কতবার পানি ছিল)।")

    add_heading_styled(doc, "৩.২ JRC Occurrence শতাংশ থেকে হাইড্রোপিরিয়ড শ্রেণিতে রূপান্তর", level=2)
    add_para(doc,
        "৪,৩১০টি পয়েন্ট JRC occurrence অনুযায়ী অবরোহ ক্রমে সাজানো হয়েছে (stable sort: mergesort)। "
        "এরপর সাজানো তালিকাটি নির্দিষ্ট ইনডেক্স অবস্থানে (৭০০, ১৪০০, ১৯২৮) কেটে ৪টি গ্রুপে ভাগ করা হয়েছে:\n\n"
        "• শীর্ষ ৭০০ পয়েন্ট → স্থায়ী পানি (ডেটায় প্রকৃত JRC রেঞ্জ: ৬৯% – ১০০%)\n"
        "• পরবর্তী ৭০০ পয়েন্ট → আধা-স্থায়ী পানি (প্রকৃত JRC রেঞ্জ: ৩৬% – ৬৯%)\n"
        "• পরবর্তী ৫২৮ পয়েন্ট → ক্ষণস্থায়ী পানি (প্রকৃত JRC রেঞ্জ: ১০% – ৩৬%)\n"
        "• অবশিষ্ট ২,৩৮২ পয়েন্ট → অ-জলাভূমি (প্রকৃত JRC রেঞ্জ: ০% – ১০%)\n\n"
        "এই ইনডেক্স-স্লাইসিং পদ্ধতি (কঠিন শতাংশ থ্রেশহোল্ডের পরিবর্তে) ব্যবহার করা হয় কারণ "
        "ভ্যালিডেশনের লক্ষ্য হলো প্রতিটি হাইড্রোপিরিয়ড স্তরে নির্দিষ্ট, প্রতিনিধিত্বমূলক নমুনা আকার "
        "নিশ্চিত করা — যাতে সামগ্রিক নির্ভুলতা সহজে শ্রেণিবিভাগযোগ্য শুষ্ক ভূমি বা স্থায়ী মুক্ত পানি "
        "দ্বারা প্রভাবিত না হয়।",
        bold_prefix="বিস্তারিত প্রক্রিয়া:\n")

    add_file_list(doc, "সংশ্লিষ্ট ডেটা ফাইলসমূহ:", [
        "Sub_issue1/Supplementary_Table_Validation_Points.csv (৪,৩১০ পয়েন্টের প্রতিটির JRC occurrence % সহ)"
    ])
    add_file_list(doc, "ব্যবহৃত কোড:", [
        "gee_scripts/04_extract_jrc_occurrence.js (GEE এক্সট্রাকশন স্ক্রিপ্ট)",
        "python_scripts/10_calculate_detailed_validation_metrics.py (sort-and-slice স্ট্র্যাটিফিকেশন)"
    ])

    doc.add_page_break()

    # =========================================================
    # ISSUE 4
    # =========================================================
    add_heading_styled(doc, "ইস্যু ৪: জেলাভিত্তিক অ্যাডাপটিভ GMM থ্রেশহোল্ড এবং ক্যালিব্রেটেড পানির এলাকা টাইম-সিরিজ", level=1)

    add_para(doc,
        "ST-GMM ফ্রেমওয়ার্কের সম্পূর্ণ মধ্যবর্তী ফলাফল একটি প্রতিলিপিযোগ্য (replicable) ডেটাসেট "
        "হিসেবে প্রদান করা।",
        bold_prefix="উদ্দেশ্য: ")

    add_heading_styled(doc, "৪.১ GMM থ্রেশহোল্ড লুকআপ টেবিল", level=2)
    add_para(doc,
        "৭,৮৯১টি সেন্টিনেল-১ IW-মোড VV দৃশ্য থেকে স্থানিকভাবে সমষ্টিগত VV ব্যাকস্ক্যাটার হিস্টোগ্রাম "
        "সকল ৬৪টি জেলা এবং ১২ ক্যালেন্ডার মাস জুড়ে প্রসেস করা হয়েছে। প্রতিটি জেলা-মাস হিস্টোগ্রামে "
        "একটি ২-কম্পোনেন্ট Gaussian Mixture Model (GMM) EM অ্যালগরিদম ব্যবহার করে ফিট করা হয়েছে। "
        "সিদ্ধান্ত থ্রেশহোল্ড (τ) ফিটেড ভূমি এবং পানি গাউসিয়ান বক্ররেখার ছেদবিন্দু হিসেবে সংজ্ঞায়িত। "
        "এটি মোট ৭৬৮টি জেলা-মাস অ্যাডাপটিভ থ্রেশহোল্ড (৬৪ জেলা × ১২ মাস) তৈরি করেছে।\n\n"
        "সম্পূর্ণ লুকআপ টেবিল Master_GMM_Thresholds_BD.csv-এ সংরক্ষিত:\n"
        "• Month_Num, Month_Name: সময়গত কী (১-১২)\n"
        "• Area_Name: জেলার নাম (৬৪ জেলা)\n"
        "• GMM_Threshold_dB: গণনাকৃত অ্যাডাপটিভ থ্রেশহোল্ড (ডেসিবেলে)")

    add_heading_styled(doc, "৪.২ জেলাভিত্তিক মাসিক পানির এলাকা টাইম-সিরিজ (২০১৫-২০২৫)", level=2)
    add_para(doc,
        "প্রতিটি জেলা, বছর এবং মাসের জন্য, জেলার নির্দিষ্ট GMM থ্রেশহোল্ড ব্যবহার করে পানির পিক্সেল "
        "গণনা করা হয়েছে এবং km²-এ রূপান্তর করা হয়েছে। district_monthly_water_area_2015_2025.csv-এর কলামসমূহ:\n\n"
        "• year, month, month_name: সময়গত কী\n"
        "• district: জেলার নাম (৬৪ জেলা)\n"
        "• division: প্রশাসনিক বিভাগ\n"
        "• water_area_km2: অক্যালিব্রেটেড পানির এলাকা\n"
        "• water_area_calibrated_km2: চূড়ান্ত ক্যালিব্রেটেড পানির এলাকা (ম্যানুস্ক্রিপ্টে ব্যবহৃত)\n"
        "• season: জলবিজ্ঞানিক মৌসুম\n\n"
        "ক্যালিব্রেশন: পিক্সেল-ভিত্তিক GEE রিডাকশন এবং হিস্টোগ্রাম-ভিত্তিক এলাকার মধ্যে স্কেল পার্থক্য "
        "মেটাতে ০.৪৯৪৯ গুণগত ক্যালিব্রেশন অনুপাত প্রয়োগ করা হয়েছে।\n"
        "ডেটা গ্যাপ (যেমন: জানুয়ারি ২০১৬) সংলগ্ন মাসগুলোর মধ্যে রৈখিক ইন্টারপোলেশন দিয়ে পূরণ করা হয়েছে।")

    add_file_list(doc, "সংশ্লিষ্ট ডেটা ফাইলসমূহ:", [
        "Sub_issue4/Master_GMM_Thresholds_BD.csv (৭৬৮ জেলা-মাস থ্রেশহোল্ড, dB-তে)",
        "Sub_issue4/district_monthly_water_area_2015_2025.csv (৬৪ জেলা × ১৩২ মাস = ৮,৪৪৮ সারি)",
        "Sub_issue4/national_monthly_water_area_2015_2025.csv (জাতীয় মাসিক সমষ্টি, ১৩২ সারি)"
    ])
    add_file_list(doc, "ব্যবহৃত কোড:", [
        "python_scripts/01_batch_gmm_processor.py (VV হিস্টোগ্রাম থেকে GMM থ্রেশহোল্ড গণনা)",
        "python_scripts/02_compute_water_area.py (পানির এলাকা গণনা, ক্যালিব্রেশন, গ্যাপ পূরণ)"
    ])

    doc.add_page_break()

    # =========================================================
    # ISSUE 5
    # =========================================================
    add_heading_styled(doc, "ইস্যু ৫: ভূপৃষ্ঠ পানির পরিবর্তন সনাক্তকরণ — বৃদ্ধি/ক্ষতি বিশ্লেষণ (২০১৫-২০২৫)", level=1)

    add_para(doc,
        "১১ বছরের বেসলাইন জুড়ে বছর-থেকে-বছর এবং মৌসুম-থেকে-মৌসুম পানির পরিমাণ কীভাবে পরিবর্তিত "
        "হয়েছে তা পরিমাণগতভাবে নির্ধারণ করা এবং এই পরিবর্তনগুলি নথিভুক্ত করে CSV ডেটাসেট তৈরি করা।",
        bold_prefix="উদ্দেশ্য: ")

    add_heading_styled(doc, "৫.১ বছর-ভিত্তিক মাসিক পরিবর্তন সনাক্তকরণ", level=2)
    add_para(doc,
        "১২টি ক্যালেন্ডার মাসের প্রতিটির জন্য, ক্যালিব্রেটেড জাতীয় পানির এলাকা পরপর বছরের মধ্যে "
        "(২০১৫→২০১৬, ২০১৬→২০১৭, ..., ২০২৪→২০২৫) তুলনা করা হয়েছে। km²-এ পরিবর্তন এবং শতাংশ পরিবর্তন "
        "রেকর্ড করা হয়েছে। এটি ১২০ সারি (১২ মাস × ১০ বছর-জোড়া) তৈরি করে।\n\n"
        "উদাহরণ (জুলাই বর্ষাকালীন শীর্ষ):\n"
        "• জুলাই ২০১৫: ১৭,৩৩১.৯ km² → জুলাই ২০১৬: ২৪,২০৫.২ km² (পরিবর্তন: +৬,৮৭৩.৩ km², +৩৯.৬৬%)\n"
        "• জুলাই ২০১৯: ২৩,২৬৭.৮ km² → জুলাই ২০২০: ২৪,৯৩৭.৮ km² (পরিবর্তন: +১,৬৭০.০ km², +৭.১৮%)\n"
        "• জুলাই ২০২৪: ২১,৪৯৫.১ km² → জুলাই ২০২৫: ১৮,৩২৪.৮ km² (পরিবর্তন: −৩,১৭০.৩ km², −১৪.৭৫%)\n\n"
        "আউটপুট ফাইল: year_to_year_monthly_change.csv\n"
        "কলামসমূহ: from_year, to_year, month, month_name, water_area_from_km2, water_area_to_km2, "
        "change_km2, change_percent")

    add_heading_styled(doc, "৫.২ মৌসুম-ভিত্তিক পরিবর্তন সনাক্তকরণ", level=2)
    add_para(doc,
        "মৌসুমী গড় পানির এলাকা (শীতকালীন শুষ্ক, প্রাক-বর্ষা, বর্ষা, বর্ষা-পরবর্তী) প্রতিটি মৌসুমের জন্য "
        "পরপর বছরের মধ্যে তুলনা করা হয়েছে। এটি ৪০ সারি (৪ মৌসুম × ১০ বছর-জোড়া) তৈরি করে।\n\n"
        "আউটপুট ফাইল: season_to_season_change.csv\n"
        "কলামসমূহ: from_year, to_year, season, mean_water_from_km2, mean_water_to_km2, change_km2, "
        "change_percent")

    add_heading_styled(doc, "৫.৩ দশকীয় পিক্সেল-পর্যায়ের পরিবর্তন সারসংক্ষেপ (জুলাই ২০১৫ বনাম জুলাই ২০২৫)", level=2)
    add_para(doc,
        "• স্থিতিশীল পানি (উভয় বছরেই পানি): ১৫,২৭০.৯ km² (৫২.০%)\n"
        "• বৃদ্ধিপ্রাপ্ত পানি (২০১৫-তে স্থল → ২০২৫-এ পানি): ৬,৩০৫.০ km² (২১.৫%)\n"
        "• ক্ষতিগ্রস্ত পানি (২০১৫-তে পানি → ২০২৫-এ স্থল): ৭,৭৮৪.০ km² (২৬.৫%)\n\n"
        "এটি নিশ্চিত করে যে বাংলাদেশের ভূপৃষ্ঠের পানি ভৌগোলিক পুনর্বন্টনের মধ্য দিয়ে যাচ্ছে — "
        "বিশেষত নিম্ন মেঘনার সক্রিয় মোহনা এলাকা এবং দক্ষিণ-পশ্চিমের উপকূলীয় বেল্টে — "
        "সমগ্র জাতীয় পর্যায়ে সমানভাবে সম্প্রসারণ বা সংকোচনের পরিবর্তে।",
        bold_prefix="মূল অনুসন্ধান: ")

    add_file_list(doc, "সংশ্লিষ্ট ডেটা ফাইলসমূহ:", [
        "Sub_issue5/year_to_year_monthly_change.csv (১২০ সারি: প্রতিটি মাসের বছরভিত্তিক পরিবর্তন)",
        "Sub_issue5/season_to_season_change.csv (৪০ সারি: মৌসুমভিত্তিক পরিবর্তন)",
        "Sub_issue5/table4_monthly_water_stats.csv (১১ বছরের মাসিক min/max/mean/std পরিসংখ্যান)",
        "Sub_issue5/table5_seasonal_water_area.csv (বছর অনুযায়ী মৌসুমী মোট ও গড়)",
        "Sub_issue5/division_july_water_area_2015_2025.csv (বিভাগ-পর্যায়ে জুলাই শীর্ষ পানির এলাকা)"
    ])
    add_file_list(doc, "ব্যবহৃত কোড:", [
        "python_scripts/08_verify_manuscript_claims.py (২১.৫% বৃদ্ধিপ্রাপ্ত পানি সহ দাবি যাচাই)",
        "python_scripts/03_generate_core_figures.py (প্রকাশনা ফিগার তৈরি)"
    ])

    # Save
    out_path = "/Users/drubothedon/Documents/Project/SAR/SAR Analysis GMM/5_issues/Methodological_Explanations_Bangla.docx"
    doc.save(out_path)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
