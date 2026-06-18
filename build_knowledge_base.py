import chromadb
from chromadb.utils import embedding_functions

# Use sentence-transformers (downloads from HuggingFace, more reliable)
sentence_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="E:/Oishee/Thesis/chroma_db")

try:
    client.delete_collection("clinical_guidelines")
except:
    pass

collection = client.create_collection(
    "clinical_guidelines",
    embedding_function=sentence_ef
)

guidelines = [
    {"id": "sepsis_01", "condition": "sepsis", "hop": "diagnosis", "text": "Sepsis-3 Definition: Sepsis is life-threatening organ dysfunction caused by a dysregulated host response to infection. Organ dysfunction is identified as an acute increase of 2 or more points in the SOFA (Sequential Organ Failure Assessment) score, reflecting an overall mortality risk of approximately 10%."},
    {"id": "sepsis_02", "condition": "sepsis", "hop": "screening", "text": "qSOFA (quick SOFA) Screening Criteria: Used for rapid bedside identification of patients with suspected infection likely to have poor outcomes. Score 1 point each for: respiratory rate 22/min or greater, altered mentation (GCS less than 15), and systolic blood pressure 100 mmHg or less. A qSOFA score of 2 or more suggests higher risk of sepsis."},
    {"id": "sepsis_03", "condition": "sepsis", "hop": "septic_shock", "text": "Septic Shock Criteria: Septic shock is a subset of sepsis with circulatory and cellular metabolic dysfunction associated with higher mortality. Identified clinically by: persisting hypotension requiring vasopressors to maintain mean arterial pressure 65 mmHg or greater AND serum lactate greater than 2 mmol/L despite adequate volume resuscitation."},
    {"id": "sepsis_04", "condition": "sepsis", "hop": "treatment", "text": "Sepsis Initial Management (Hour-1 Bundle): Measure lactate level, obtain blood cultures before antibiotics, administer broad-spectrum antibiotics, begin rapid crystalloid fluid resuscitation 30 mL/kg for hypotension or lactate 4 mmol/L or greater, apply vasopressors if hypotensive during or after fluid resuscitation to maintain MAP 65 mmHg or greater."},
    {"id": "sepsis_05", "condition": "sepsis", "hop": "labs", "text": "Sepsis Laboratory Markers: Key markers include elevated white blood cell count (WBC greater than 12000) or low (less than 4000), elevated lactate (greater than 2 mmol/L indicates tissue hypoperfusion), elevated procalcitonin and C-reactive protein, thrombocytopenia, and elevated creatinine indicating renal involvement."},

    {"id": "pneumonia_01", "condition": "pneumonia", "hop": "diagnosis", "text": "Community-Acquired Pneumonia (CAP) Diagnosis per ATS/IDSA: Diagnosis requires demonstrable infiltrate on chest radiograph or other imaging, together with clinical features such as fever, cough, sputum production, dyspnea, and findings on auscultation like crackles or bronchial breath sounds."},
    {"id": "pneumonia_02", "condition": "pneumonia", "hop": "severity", "text": "CURB-65 Severity Score for Pneumonia: One point each for Confusion, Urea greater than 7 mmol/L (BUN greater than 19 mg/dL), Respiratory rate 30/min or greater, Blood pressure low (systolic less than 90 or diastolic 60 mmHg or less), and age 65 or older. Score 0-1 outpatient, 2 consider admission, 3 or more severe requiring hospitalization and possible ICU."},
    {"id": "pneumonia_03", "condition": "pneumonia", "hop": "icu", "text": "ATS/IDSA Criteria for Severe Pneumonia (ICU admission): Major criteria: septic shock requiring vasopressors, or respiratory failure requiring mechanical ventilation. Minor criteria (3 or more): respiratory rate 30/min or greater, PaO2/FiO2 ratio 250 or less, multilobar infiltrates, confusion, uremia, leukopenia, thrombocytopenia, hypothermia, hypotension requiring aggressive fluids."},
    {"id": "pneumonia_04", "condition": "pneumonia", "hop": "treatment", "text": "ATS/IDSA Pneumonia Empiric Antibiotic Treatment: For outpatients without comorbidities, amoxicillin or doxycycline or a macrolide. For inpatients (non-ICU), a respiratory fluoroquinolone or beta-lactam plus macrolide. For ICU patients, beta-lactam plus either macrolide or fluoroquinolone. Adjust based on local resistance and culture results."},
    {"id": "pneumonia_05", "condition": "pneumonia", "hop": "labs", "text": "Pneumonia Laboratory and Imaging Findings: Chest X-ray showing lobar consolidation, infiltrates, or interstitial pattern. Elevated WBC with left shift, elevated inflammatory markers (CRP, procalcitonin). Blood cultures, sputum gram stain and culture, and pulse oximetry showing hypoxemia in severe cases."},

    {"id": "aki_01", "condition": "aki", "hop": "diagnosis", "text": "KDIGO Acute Kidney Injury (AKI) Definition: AKI is diagnosed by any of the following: increase in serum creatinine by 0.3 mg/dL or more within 48 hours, increase in serum creatinine to 1.5 times baseline or more within the prior 7 days, or urine volume less than 0.5 mL/kg/h for 6 hours."},
    {"id": "aki_02", "condition": "aki", "hop": "staging", "text": "KDIGO AKI Staging: Stage 1 - creatinine 1.5 to 1.9 times baseline or increase 0.3 mg/dL or more, or urine output less than 0.5 mL/kg/h for 6 to 12 hours. Stage 2 - creatinine 2.0 to 2.9 times baseline, or urine output less than 0.5 mL/kg/h for 12 hours or more. Stage 3 - creatinine 3.0 times baseline or more, or 4.0 mg/dL or higher, or initiation of renal replacement therapy, or urine output less than 0.3 mL/kg/h for 24 hours or anuria for 12 hours."},
    {"id": "aki_03", "condition": "aki", "hop": "causes", "text": "AKI Etiology Categories: Prerenal (volume depletion, hypotension, sepsis, heart failure reducing renal perfusion), Intrinsic renal (acute tubular necrosis from ischemia or nephrotoxins, glomerulonephritis, interstitial nephritis), and Postrenal (urinary tract obstruction). Sepsis is a leading cause of AKI in hospitalized patients."},
    {"id": "aki_04", "condition": "aki", "hop": "treatment", "text": "KDIGO AKI Management: Treat underlying cause, optimize volume status and hemodynamics, maintain mean arterial pressure, discontinue nephrotoxic agents (NSAIDs, aminoglycosides, contrast), adjust drug dosing for renal function, monitor electrolytes and acid-base balance. Consider renal replacement therapy for refractory hyperkalemia, acidosis, fluid overload, or uremia."},
    {"id": "aki_05", "condition": "aki", "hop": "labs", "text": "AKI Laboratory Monitoring: Serial serum creatinine and BUN, urine output measurement, electrolytes especially potassium, urinalysis for casts and protein, fractional excretion of sodium (FENa less than 1% suggests prerenal, greater than 2% suggests intrinsic), and assessment of acid-base status for metabolic acidosis."},
]

collection.add(
    documents=[g["text"] for g in guidelines],
    metadatas=[{"condition": g["condition"], "hop": g["hop"]} for g in guidelines],
    ids=[g["id"] for g in guidelines]
)

print(f"Knowledge base built! {len(guidelines)} guideline chunks loaded.")
print("Stored in: E:/Oishee/Thesis/chroma_db")