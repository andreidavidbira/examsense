"""
ExamSense+ - NLP Text Cleaner
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- curata textul brut extras din documente
- elimina simbolurile nedorite aparute dupa OCR sau parsarea PDF-urilor
- normalizeaza newline-urile si spatiile
- pregateste textul pentru etapele urmatoare din pipeline-ul NLP
"""

import re


# curata textul brut inainte de procesarea NLP
def clean_text(text):
    # eliminam simboluri parasite aparute frecvent dupa OCR sau extractie din PDF
    text = re.sub(r"[•●▪■►▼▲]", " ", text)

    # normalizam toate newline-urile la acelasi format
    text = text.replace("\r", "\n")

    # curatam fiecare linie separat
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # reducem spatiile multiple si eliminam spatiile dinaintea semnelor de punctuatie
        line = re.sub(r"\s+", " ", line)
        line = re.sub(r"\s+([.,!?;:])", r"\1", line)

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()