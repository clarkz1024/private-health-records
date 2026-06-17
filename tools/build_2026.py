# Generates bilingual (EN+ZH) category PDFs + PNG views from the 2026 Southwest Hospital check-up.
# Step 1 (this script, mode=html): write one HTML per category into BUILD dir.
# Step 2 (PowerShell): Chrome --print-to-pdf each HTML -> images/<name>.pdf
# Step 3 (this script, mode=render): each PDF -> tall PNG (images/<name>.png) + thumb (images/thumbs/<name>.png)
import sys, os, html

REPO = r"C:\Users\gogogo\source\repos\private-health-records"
BUILD = r"C:\Users\gogogo\AppData\Local\Temp\build2026"
SRC = r"C:\Users\gogogo\AppData\Local\Temp\pdfpages"   # rendered original pages
os.makedirs(BUILD, exist_ok=True)

PATIENT_META = ("Patient: Lei Zhu (Clark) &middot; Male &middot; DOB 1992-06-23 &nbsp;|&nbsp; "
    "Exam date: 2026-04-01 &nbsp;|&nbsp; Southwest Hospital Health Management Center, Chongqing &nbsp;|&nbsp; "
    "Check-up ID: 8002262907")

def esc(s): return html.escape(str(s))

def labtable(rows):
    # rows: (en, zh, value, ref, unit, flag)  flag in '', 'H', 'L'
    out = ['<table><thead><tr><th>Test</th><th>项目</th><th>Result</th><th>Reference</th><th>Unit</th><th>Flag</th></tr></thead><tbody>']
    for en, zh, val, ref, unit, flag in rows:
        fcls = 'flag' if flag == 'H' else ('flag low' if flag == 'L' else '')
        ftxt = {'H': 'High &uarr;', 'L': 'Low &darr;', '': ''}[flag]
        out.append(f'<tr><td>{esc(en)}</td><td class="zh">{esc(zh)}</td>'
                   f'<td class="{fcls}">{esc(val)}</td><td>{esc(ref)}</td><td>{esc(unit)}</td>'
                   f'<td class="{fcls}">{ftxt}</td></tr>')
    out.append('</tbody></table>')
    return '\n'.join(out)

def bipara(en, zh):
    return f'<p>{en}</p><p class="zh">{esc(zh)}</p>'

SRC_PDF = os.path.join(REPO, "images", "2026-examination reports.pdf")
def note_original():
    return ('<p class="note">The original examination image/waveform is appended on the following '
            'page(s). 原始检查图像/波形见后页。</p>')

CATS = []
def add(key, en_title, zh_title, category, test, result, notes, body, extra=None):
    # extra = list of 0-based source-PDF page indices to append (original scans/waveforms)
    CATS.append(dict(key=key, en=en_title, zh=zh_title, category=category, test=test,
                     result=result, notes=notes, body=body, extra=extra or []))

# ---------- 1. SUMMARY ----------
findings = [
 ("Mixed hyperlipidaemia", "混合型高脂血症",
  "Low-fat, low-calorie diet; limit animal fats, organ meats and seafood; abstain from alcohol; "
  "increase exercise; lipid-lowering medication under physician guidance if required; monitor blood lipids.",
  "建议：低脂、低热量饮食，限制动物油、动物内脏、海鲜等食物，忌酒，多运动，必要时在医师指导下服用降脂药物，随访血脂。"),
 ("Overweight (BMI = 25.5 kg/m&sup2;)", "体重超重（BMI=25.5kg/m²）",
  "Control diet (low salt / fat / sugar), eat more vegetables and fruit, exercise appropriately, "
  "and lose weight gradually (0.5&ndash;1.0 kg per month). Normal BMI is 18.5&ndash;23.9.",
  "建议：控制饮食，低盐、低脂和低糖饮食，多食蔬菜水果，适当活动，逐渐减轻体重（0.5－1.0kg/月）。"),
 ("Liver steatosis &mdash; CAP elevated (&ge;292, SEVERE)", "肝脂肪变测定CAP值偏高（≥292）（重度）",
  "CAP &ge;292 dB/m suggests hepatic fat &ge;67%. Abstain from alcohol, increase activity, control weight, "
  "reduce fatty/high-cholesterol foods, eat more vegetables, fruit and fibre; follow up with liver "
  "ultrasound and liver function tests.",
  "建议：忌酒，多活动，控制体重，少吃含脂肪及胆固醇较高的食物，多吃蔬菜、水果和富含纤维素的食物，随访肝脏B超及肝功能。"),
 ("Elevated ALT and AST (liver enzymes)", "谷丙转氨酶(ALT)偏高；天门冬氨酸氨基转移酶(AST)偏高",
  "Abstain from alcohol, avoid over-exertion, low-fat diet, follow up liver function; "
  "hepatoprotective treatment if needed.",
  "建议：忌酒，避免过分劳累，低脂饮食，随访肝功，必要时保肝治疗。"),
]
body = ['<h2 class="sec">Key Findings &amp; Recommendations / 主要问题与建议</h2>']
for i,(en,zh,adv_en,adv_zh) in enumerate(findings,1):
    body.append(f'<div class="finding"><div class="badge">{i}</div> <span class="ftitle">{en}</span> '
                f'<span class="zh">（{esc(zh)}）</span>'
                f'<p><b>Advice:</b> {adv_en}</p><p class="zh">{esc(adv_zh)}</p></div>')
add("Summary","Master Summary Report","主检报告","Summary","Annual check-up summary",
    "4 findings: hyperlipidaemia, overweight, severe hepatic steatosis, elevated ALT/AST",
    "Overall summary of the 2026 annual health check-up with the four flagged findings and lifestyle advice.",
    '\n'.join(body))

# ---------- 2. BLOOD TESTS ----------
cbc = [
 ("WBC","白细胞数目",8.01,"3.5-9.5","10^9/L",""),
 ("RBC","红细胞数目",5.68,"4.3-5.8","10^12/L",""),
 ("Haemoglobin (HGB)","血红蛋白",171,"130-175","g/L",""),
 ("Haematocrit (HCT)","红细胞压积",50.30,"40-50","%","H"),
 ("MCV","平均红细胞体积",88.50,"82-100","fL",""),
 ("MCH","平均血红蛋白含量",30.00,"27-34","pg",""),
 ("MCHC","平均血红蛋白浓度",340,"316-354","g/L",""),
 ("Platelets (PLT)","血小板数目",280,"125-350","10^9/L",""),
 ("Neutrophils #","中性粒细胞数目",4.04,"1.8-6.3","10^9/L",""),
 ("Lymphocytes #","淋巴细胞数目",3.00,"1.1-3.2","10^9/L",""),
 ("Monocytes #","单核细胞数目",0.66,"0.1-0.6","10^9/L","H"),
 ("Eosinophils #","嗜酸性粒细胞数目",0.28,"0.02-0.52","10^9/L",""),
 ("Basophils #","嗜碱性粒细胞数目",0.03,"0-0.06","10^9/L",""),
 ("Neutrophils %","中性粒细胞百分比",50.30,"40-75","%",""),
 ("Lymphocytes %","淋巴细胞百分比",37.50,"20-50","%",""),
 ("Monocytes %","单核细胞百分比",8.30,"3-10","%",""),
 ("Eosinophils %","嗜酸性粒细胞百分比",3.50,"0.4-8","%",""),
 ("Basophils %","嗜碱性粒细胞百分比",0.40,"0-1","%",""),
 ("RDW-CV","红细胞体积分布宽度CV",13.20,"11-16","%",""),
 ("RDW-SD","红细胞体积分布宽度SD",42.20,"37-54","fL",""),
 ("MPV","平均血小板体积",10.20,"9-13","fL",""),
 ("PDW","血小板分布宽度",16.40,"9-17","%",""),
 ("Plateletcrit (PCT)","血小板压积",0.29,"0.108-0.282","%","H"),
 ("Large platelet ratio (P-LCR)","大血小板比率",27.80,"13-43","%",""),
]
liver = [
 ("Total protein (TP)","总蛋白",73.50,"66-83","g/L",""),
 ("Albumin (Alb)","白蛋白",44.60,"38-51","g/L",""),
 ("Globulin (G)","球蛋白",28.9,"25-38","g/L",""),
 ("A/G ratio","白球比值",1.5,"1.2-2.5","",""),
 ("ALT","谷丙转氨酶",85.60,"0-42","IU/L","H"),
 ("AST","天门冬氨酸氨基转移酶",53.90,"0-42","IU/L","H"),
 ("GGT","谷氨酰转肽酶",49.50,"4-50","IU/L",""),
 ("ALP","碱性磷酸酶",97.50,"45-125","IU/L",""),
 ("Total bilirubin (TBIL)","总胆红素",13.90,"6-21","umol/L",""),
 ("Direct bilirubin (DBIL)","直接胆红素",2.50,"0-6","umol/L",""),
 ("Indirect bilirubin (IBIL)","间接胆红素",11.40,"3-16","umol/L",""),
 ("FIB-4 fibrosis index","肝纤维化指数",0.69,"<1.3 low risk","",""),
]
lipids = [
 ("Total cholesterol (TC)","总胆固醇",5.52,"3.1-5.7","mmol/L",""),
 ("Triglycerides (TG)","甘油三酯",1.83,"0.4-1.73","mmol/L","H"),
 ("HDL-C","高密度脂蛋白胆固醇",1.52,"0.9-2","mmol/L",""),
 ("LDL-C","低密度脂蛋白胆固醇",3.38,"healthy 2.07-3.1; <2.6 high CV risk","mmol/L",""),
]
kidney = [
 ("Urea (UN)","血尿素",5.88,"1.7-8.3","mmol/L",""),
 ("Uric acid (UA)","血尿酸",372.80,"155-428","umol/L",""),
 ("Creatinine (Cr)","血肌酐",85.60,"59-104","umol/L",""),
 ("Glucose (fasting)","血糖",5.27,"3.9-6.1","mmol/L",""),
 ("Cystatin C","胱抑素C",0.85,"0.3-1.05","mg/L",""),
 ("eGFR","估算肾小球滤过率",89.32,"80-120","mL/min/1.73m2",""),
]
coag = [
 ("Thrombin time (TT)","凝血酶时间",18.50,"14-21","sec",""),
 ("PT-INR","PT-INR",0.94,"0.85-1.21","",""),
 ("PT activity %","PT%",95.70,"65-130","%",""),
 ("Prothrombin time (PT)","凝血酶原时间",10.60,"9.8-13.7","sec",""),
 ("APTT","活化部分凝血活酶时间",25.70,"24.8-33.8","sec",""),
 ("APTT-Ratio","APTT比值",0.95,"0.92-1.25","",""),
 ("Fibrinogen (Fib)","纤维蛋白原",2.32,"1.8-3.7","g/L",""),
]
tumor = [
 ("AFP","甲胎蛋白",5.44,"0-20","ng/ml",""),
 ("CEA","癌胚抗原",0.73,"0-5","ng/ml",""),
 ("PSA","前列腺特异性抗原",0.64,"0-4","ng/ml",""),
 ("CA125","糖类抗原125",4.28,"0-35","U/ml",""),
 ("CA19-9","糖类抗原19-9",7.90,"0-37","U/ml",""),
 ("CA15-3","糖类抗原15-3",2.75,"0-28","U/ml",""),
]
other = [
 ("HbA1c","糖化血红蛋白",5.4,"4.0-6.0","%",""),
 ("Thymidine kinase 1 (TK1)","胸苷激酶",0.87,"0-2","pM",""),
 ("5-HIAA","5-羟吲哚乙酸","Negative","Negative","",""),
 ("Adiponectin","脂联素",6.35,">=4","ug/mL",""),
]
b = []
b.append('<h2 class="sec">Complete Blood Count / 血常规</h2>'+labtable(cbc))
b.append('<h2 class="sec">Liver Function (8) / 肝功8项</h2>'+labtable(liver))
b.append('<h2 class="sec">Lipid Panel (4) / 血脂4项</h2>'+labtable(lipids))
b.append('<h2 class="sec">Renal Function + Glucose + Cystatin C / 肾功3项+血糖+胱抑素C</h2>'+labtable(kidney))
b.append('<h2 class="sec">Coagulation (4) / 凝血四项</h2>'+labtable(coag))
b.append('<h2 class="sec">Tumour Markers (6) / 肿瘤标志物（6项）</h2>'+labtable(tumor))
b.append('<h2 class="sec">Other / 其他</h2>'+labtable(other))
add("Blood-Tests","Blood &amp; Laboratory Tests","检验报告（血液）","Blood Test","Full blood panel",
    "ALT 85.6 H, AST 53.9 H, TG 1.83 H, HCT 50.3 H; tumour markers, HbA1c, coagulation all normal",
    "All blood panels from the check-up. Flagged: ALT, AST (liver enzymes), triglycerides, haematocrit, monocytes. Tumour markers, glucose/HbA1c, kidney function and coagulation normal.",
    '\n'.join(b))

# ---------- 3. URINALYSIS ----------
urine = [
 ("Specific gravity (SG)","尿比重",1.020,"1.003-1.03","",""),
 ("Protein (dipstick)","尿蛋白","Neg","Negative","",""),
 ("Glucose (GLU)","尿糖定性","Neg","Negative","mmol/L",""),
 ("pH","尿PH值",6.50,"4.6-8.0","",""),
 ("Bilirubin (BIL)","尿胆红素","Neg","Negative","umol/L",""),
 ("Urobilinogen (Uro)","尿胆原","Normal","Normal","umol/L",""),
 ("Ketones (KET)","尿酮体","Neg","Negative","mmol/L",""),
 ("Leukocyte esterase","尿白细胞酯酶","Neg","Negative","",""),
 ("Occult blood","尿潜血","Neg","Negative","",""),
 ("Nitrite (NIT)","尿亚硝酸盐","Neg","Negative","",""),
 ("Microalbumin","尿微量白蛋白","Neg","0-0","",""),
 ("Vitamin C","尿维生素C",0.0,"0-0","",""),
 ("Colour","尿色","Light yellow","Light yellow","",""),
 ("Clarity","尿液透明度","Clear","Clear","",""),
 ("Protein (quant.)","尿蛋白定性","Neg","Negative","",""),
 ("Leukocytes (LEU)","尿白细胞","Neg","Negative","/HPF",""),
 ("Erythrocytes (ERY)","尿红细胞","Neg","Negative","/HPF",""),
 ("Pus cells","尿脓细胞","Neg","Negative","/HPF",""),
 ("Mucus threads","尿粘液丝","Neg","Negative","/HPF",""),
 ("Casts","尿管型","Neg","Negative","/HPF",""),
 ("Epithelial cells","尿上皮细胞","Neg","Negative","/HPF",""),
]
add("Urinalysis","Urinalysis + Microalbumin","尿常规+分析+微量白蛋白","Urinalysis","Urine routine + microalbumin",
    "All parameters normal / negative",
    "Complete urinalysis including microalbumin. All values within normal limits / negative.",
    '<h2 class="sec">Urinalysis / 尿常规分析</h2>'+labtable(urine))

# ---------- 4. PHYSICAL EXAM ----------
phys = [
 ("Systolic BP","收缩压",117,"90-139","mmHg",""),
 ("Diastolic BP","舒张压",68,"60-89","mmHg",""),
 ("Pulse","脉搏",84,"-","/min",""),
 ("Height","身高",172.5,"-","cm",""),
 ("Weight","体重",76.0,"-","kg",""),
 ("BMI","体重指数",25.5,"18.5-23.9","kg/m2","H"),
]
add("Physical-Exam","Physical Examination (Vitals)","体格检查","Physical Exam","Vital signs & anthropometry",
    "BP 117/68, pulse 84; BMI 25.5 (overweight)",
    "Vital signs and body measurements. Blood pressure and pulse normal; BMI 25.5 (overweight).",
    '<h2 class="sec">Vital Signs &amp; Measurements / 体格检查</h2>'+labtable(phys))

# ---------- 5. ECG ----------
ecg_tbl = [
 ("Rhythm","心律","Sinus / 窦性","-","",""),
 ("Ventricular rate","室率",78,"60-100","bpm",""),
 ("Atrial rate","房率",78,"-","bpm",""),
 ("P wave duration","P波时限",90,"-","ms",""),
 ("P-R interval","P-R间期",123,"120-200","ms",""),
 ("QRS duration","QRS时限",98,"<120","ms",""),
 ("QRS axis","QRS电轴",11,"-30 to 90","deg",""),
 ("QT / QTc","QT/QTc","340 / 389","-","ms",""),
 ("RV5 + SV1","RV5+SV1",2.16,"-","mV",""),
]
ecgbody = ['<h2 class="sec">12-Lead ECG / 12导心电图</h2>',
 '<p><b>Diagnosis:</b> Sinus arrhythmia <span class="zh">（诊断：窦性心律不齐）</span></p>',
 labtable(ecg_tbl),
 '<p class="note">Sinus arrhythmia is a normal variant of the heart rhythm and is usually of no clinical concern.</p>',
 note_original()]
add("ECG","12-Lead Electrocardiogram (ECG)","12导心电图","ECG","12-lead ECG",
    "Sinus arrhythmia (normal variant); rate 78 bpm, intervals normal",
    "12-lead ECG. Diagnosis: sinus arrhythmia (a normal rhythm variant). All intervals and axis within normal limits. Original trace included.",
    '\n'.join(ecgbody), extra=[10])

# ---------- 6. CHEST X-RAY ----------
cxr = ['<h2 class="sec">PA Chest Radiograph / 胸部正位片</h2>',
 '<h3>Findings / 检查所见</h3>',
 bipara("Both lungs show clear markings with no abnormal density. Hilar structures are normal bilaterally. "
        "The heart is not enlarged and the mediastinum is central. Both hemidiaphragms are smooth, both "
        "costophrenic angles are sharp, and the ribs above the diaphragm show no abnormality.",
        "双肺纹理清晰，肺内未见异常密度影，双肺门影结构正常，心影不大，纵隔居中，双侧膈面光整，双侧肋膈角锐利，膈上肋骨未见异常。"),
 '<h3>Impression / 印象</h3>',
 bipara("PA chest radiograph &mdash; no abnormality.", "胸部正位片摄片未见异常。")]
add("Chest-Xray","Chest X-ray (PA)","胸部正位片","Chest X-ray","PA chest radiograph",
    "No abnormality",
    "Posterior-anterior chest radiograph reported as normal.",
    '\n'.join(cxr))

# ---------- 7. ABDOMINAL ULTRASOUND ----------
us = ['<h2 class="sec">Abdominal Ultrasound / 彩超（肝胆胰脾+双肾+门静脉）</h2>',
 '<h3>Findings / 检查所见</h3>',
 bipara("<b>Liver:</b> left lobe AP diameter 55 mm, right lobe oblique diameter 115 mm. Normal shape, smooth "
        "capsule, clear vascular markings, homogeneous parenchymal echogenicity, no far-field attenuation. "
        "Portal vein 10 mm with good flow filling; right-branch velocity 16 cm/s.",
        "左肝前后径55mm，右肝斜径115mm。肝切面形态正常，包膜光整，血管纹理显示清晰，肝实质回声均质，远场声衰无。门静脉内径10mm。门脉血流充盈好，右支流速16cm/s。"),
 bipara("<b>Gallbladder:</b> normal shape and size, thin uniform wall, clear lumen, no abnormal echo. "
        "Common bile duct 5 mm; no intrahepatic duct dilatation. <b>Pancreas:</b> normal, homogeneous echo, "
        "main duct not dilated. <b>Spleen:</b> thickness 28 mm, fine homogeneous echo, no abnormality.",
        "胆囊切面形态大小正常，壁薄均匀，内部液区清晰，腔内未见明显异常回声。胆总管内径5mm。肝内胆管无明显扩张。胰腺切面形态正常，回声均匀，主胰管不扩张。脾厚28mm，回声细小均匀，其内未见异常。"),
 bipara("<b>Both kidneys:</b> normal shape and size, smooth capsule, homogeneous parenchyma, clear "
        "cortico-medullary differentiation, no stones / hydronephrosis / mass. CDFI: good renal blood flow "
        "in a tree-like distribution.",
        "双肾形态大小正常，包膜光整，实质回声均匀，内部结构层次清晰，其内未见明显结石、积水、占位。CDFI：双肾血流充盈好，呈树型分布。"),
 '<h3>Impression / 印象</h3>',
 bipara("Liver, gallbladder, pancreas, spleen and both kidneys &mdash; no significant abnormality on ultrasound.",
        "肝、胆、胰、脾、双肾超声未见明显异常。"),
 '<p class="note">Note: greyscale ultrasound did not flag fatty liver here, but the FibroScan CAP value (311 dB/m) indicates severe steatosis &mdash; see the Liver FibroScan report.</p>']
add("Abdominal-Ultrasound","Abdominal Ultrasound","腹部彩超","Ultrasound","Liver/GB/pancreas/spleen/kidneys + portal vein",
    "Liver, gallbladder, pancreas, spleen, both kidneys — no significant abnormality",
    "Colour Doppler ultrasound of liver, gallbladder, pancreas, spleen, both kidneys and portal vein. No significant abnormality.",
    '\n'.join(us))

# ---------- 8. PULMONARY FUNCTION ----------
pft = [
 ("FVC (% predicted)","用力肺活量",108.39,">=80","%",""),
 ("FEV1 (% predicted)","一秒用力呼气量",106.27,">=80","%",""),
 ("FEV1/FVC","一秒率",97.96,">=70","%",""),
]
add("Pulmonary-Function","Pulmonary Function (Spirometry)","肺通气功能检查","Pulmonary Function","Spirometry",
    "Normal ventilatory function",
    "Spirometry. FVC, FEV1 and FEV1/FVC all normal — normal ventilatory function.",
    '<h2 class="sec">Spirometry / 肺通气功能</h2>'+labtable(pft)+
    bipara("Conclusion: normal ventilatory function; no significant abnormality.",
           "肺通气功能正常；未见明显异常。"))

# ---------- 9. TCD ----------
tcd = ['<h2 class="sec">Transcranial Doppler (TCD) / 经颅多普勒</h2>',
 '<h3>Impression / 印象</h3>',
 bipara("Pulsatility index normal. Flow velocities of the bilateral middle cerebral, internal carotid and "
        "posterior cerebral arteries and the vertebro-basilar arteries show no significant abnormality. "
        "Cerebral blood-flow study &mdash; no significant abnormality.",
        "PI值正常，双侧大脑中动脉、双侧颈内动脉、双侧大脑后动脉、椎-基底动脉血流速度未见明显异常。脑血流图未见明显异常。"),
 note_original()]
add("Transcranial-Doppler","Transcranial Doppler (TCD)","经颅多普勒","Transcranial Doppler","Cerebral blood flow",
    "No significant abnormality",
    "Transcranial Doppler of cerebral arteries. Normal pulsatility and flow velocities; no significant abnormality. Original waveforms included.",
    '\n'.join(tcd), extra=[9])

# ---------- 10. FIBROSCAN ----------
fs = ['<h2 class="sec">Liver Transient Elastography (FibroScan) / 肝纤维瞬时弹性+脂肪变测定</h2>',
 labtable([
   ("CAP (steatosis)","脂肪变 CAP",311,">=292 severe (>=67% fat)","dB/m","H"),
   ("E (stiffness)","硬度 E",5.2,"<7.3 normal (F0-F1)","kPa",""),
   ("Valid / total measurements","有效/总测量","12 / 12","-","",""),
   ("CAP IQR","CAP四分位距",34,"-","dB/m",""),
   ("E IQR / median","E离散度",21,"<30","%",""),
 ]),
 '<h3>Interpretation / 解读</h3>',
 bipara("<b>CAP 311 dB/m &mdash; severe hepatic steatosis</b> (fatty liver, &ge;67% of hepatocytes). "
        "<b>E 5.2 kPa &mdash; normal liver stiffness</b> (no significant fibrosis, stage F0&ndash;F1). "
        "Probe M, device 502TOUCH.",
        "CAP 311 dB/m 提示重度脂肪肝（≥67%）。E 5.2 kPa 提示肝脏硬度正常（无明显纤维化，F0–F1）。"),
 note_original()]
add("Liver-FibroScan","Liver FibroScan (Elastography)","肝纤维瞬时弹性+脂肪变","Liver FibroScan","CAP + stiffness (E)",
    "CAP 311 dB/m — severe steatosis; E 5.2 kPa — no fibrosis",
    "Transient elastography. CAP 311 dB/m indicates severe fatty liver; liver stiffness E 5.2 kPa is normal (no significant fibrosis).",
    '\n'.join(fs), extra=[11])

CSS = """
@page { size: A4; margin: 13mm 13mm 14mm; }
*{box-sizing:border-box}
body{font-family:'Segoe UI','Microsoft YaHei',Arial,sans-serif;color:#0f2230;font-size:12px;margin:0}
.head{border-bottom:3px solid #0d8e8a;padding-bottom:9px;margin-bottom:14px}
.head h1{margin:0;font-size:21px;color:#0a6f6c;letter-spacing:-.2px}
.head .sub{color:#5b7080;font-size:13px;margin-top:2px}
.head .meta{font-size:10.5px;color:#5b7080;margin-top:7px;line-height:1.5}
h2.sec{font-size:14px;margin:16px 0 7px;color:#0a6f6c;border-left:4px solid #0d8e8a;padding-left:8px}
h3{font-size:12.5px;margin:10px 0 4px;color:#0f2230}
table{width:100%;border-collapse:collapse;margin:4px 0 8px;font-size:11px}
th{background:#eef5f5;text-align:left;padding:6px 8px;border-bottom:2px solid #d5e3e3;color:#0a6f6c;font-size:10.5px}
td{padding:5px 8px;border-bottom:1px solid #eef2f4;vertical-align:top}
td.zh,.zh{color:#5b7080}
td.zh{font-size:10px}
.flag{color:#c0392b;font-weight:700}
.flag.low{color:#2563eb}
p{margin:5px 0;line-height:1.5}
p.zh{font-size:10.5px;margin-top:1px}
.finding{margin:9px 0;padding:9px 11px;background:#f7fafa;border:1px solid #e3eded;border-radius:8px}
.finding .badge{display:inline-block;background:#e07b39;color:#fff;width:20px;height:20px;line-height:20px;text-align:center;border-radius:50%;font-weight:700;font-size:12px}
.finding .ftitle{font-weight:700;font-size:13px}
.note{font-size:10.5px;color:#7a8a94;font-style:italic}
img.scan{max-width:100%;border:1px solid #ddd;border-radius:4px;margin-top:6px;page-break-inside:avoid}
.foot{margin-top:18px;font-size:9px;color:#90a4b0;border-top:1px solid #eee;padding-top:6px;line-height:1.4}
"""

def page_html(c):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><div class="head"><h1>{c['en']}</h1><div class="sub">{esc(c['zh'])}</div>
<div class="meta">{PATIENT_META}</div></div>
{c['body']}
<div class="foot">English translation prepared for clinical reference (bilingual). Source: Southwest Hospital / Army Medical University First Affiliated Hospital, Chongqing, China &mdash; annual health check-up 2026-04-01. Values transcribed from the original Chinese report; if any discrepancy arises, the original report prevails.</div>
</body></html>"""

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "html"
    base = "2026-04-01_SouthwestHospital_"
    if mode == "html":
        manifest_rows = []
        for c in CATS:
            fn = base + c['key']
            with open(os.path.join(BUILD, fn + ".html"), "w", encoding="utf-8") as f:
                f.write(page_html(c))
            manifest_rows.append((fn, c['category'], c['test'], c['result'], c['notes']))
        # emit manifest helper json
        import json
        with open(os.path.join(BUILD, "_cats.json"), "w", encoding="utf-8") as f:
            json.dump([{"newName":fn+".png","pdf":"images/"+fn+".pdf","category":cat,"test":t,
                        "result":r,"notes":n} for fn,cat,t,r,n in manifest_rows], f, ensure_ascii=False, indent=2)
        print("wrote", len(CATS), "html files to", BUILD)
    elif mode == "render":
        import fitz
        from PIL import Image
        imgdir = os.path.join(REPO, "images"); thumbdir = os.path.join(imgdir, "thumbs")
        srcdoc = fitz.open(SRC_PDF)
        for c in CATS:
            fn = base + c['key']; pdf = os.path.join(imgdir, fn + ".pdf")
            doc = fitz.open(pdf)
            # append original scan pages to the downloadable PDF
            for pi in c['extra']:
                doc.insert_pdf(srcdoc, from_page=pi, to_page=pi)
            doc.saveIncr() if False else doc.save(pdf + ".tmp"); doc.close()
            os.replace(pdf + ".tmp", pdf)
            doc = fitz.open(pdf)
            # render pages -> PIL images, skip near-blank text pages (keep scan pages)
            imgs = []
            npages = doc.page_count
            for idx, p in enumerate(doc):
                is_scan = idx >= npages - len(c['extra'])
                pm = p.get_pixmap(dpi=150 if not is_scan else 170)
                im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
                if not is_scan:
                    ex = im.convert("L").getextrema()
                    hist = im.convert("L").histogram()
                    nonwhite = sum(hist[:248])
                    if nonwhite / (im.width*im.height) < 0.003:
                        continue
                imgs.append(im)
            doc.close()
            W = max(i.width for i in imgs); H = sum(i.height for i in imgs)
            canvas = Image.new("RGB", (W, H), "white"); y=0
            for im in imgs:
                canvas.paste(im, ((W-im.width)//2, y)); y+=im.height
            canvas.save(os.path.join(imgdir, fn + ".png"))
            sc = min(700/W, 700/H, 1.0)
            canvas.resize((int(W*sc), int(H*sc)), Image.LANCZOS).save(os.path.join(thumbdir, fn + ".png"))
            print("rendered", fn, f"{W}x{H}", "pages:", len(imgs))
