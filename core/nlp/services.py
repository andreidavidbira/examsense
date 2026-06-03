"""
ExamSense+ - NLP Pipeline Services
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- implementeaza fluxul principal de procesare NLP pentru documente
- detecteaza limba textului si alege modelul spaCy potrivit
- imparte textul in unitati si propozitii relevante
- extrage definitiile finale folosind componentele de curatare si extractie
- expune functii simple pentru procesarea textului si extragerea conceptelor
"""

import spacy
from langdetect import detect

from nlp.definition_extractor import extract_definitions
from nlp.text_cleaner import clean_text


# incarcam modelele spaCy pentru romana si engleza
nlp_ro = spacy.load("ro_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")


# detecteaza limba textului si o reduce la ro sau en
def detect_language(text):
    try:
        lang = detect(text)
        return "ro" if "ro" in lang else "en"
    except Exception:
        return "en"


# imparte textul in propozitii folosind modelul corespunzator limbii detectate
def split_sentences_block(text, lang):
    try:
        doc = nlp_ro(text) if lang == "ro" else nlp_en(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    except Exception:
        return [piece.strip() for piece in text.split(".") if piece.strip()]


# construieste unitati de text mai mari, pentru a evita liniile foarte scurte de tip heading
def build_candidate_units(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    units = []
    current = []

    for line in lines:
        # liniile foarte scurte sunt de obicei headinguri sau etichete
        if len(line.split()) <= 2:
            if current:
                units.append(" ".join(current).strip())
                current = []
            continue

        current.append(line)

        # daca linia pare incheiata, inchidem unitatea curenta
        if line.endswith((".", "!", "?", ":")):
            units.append(" ".join(current).strip())
            current = []

    if current:
        units.append(" ".join(current).strip())

    return units


# curata textul, il imparte in propozitii si extrage definitiile finale
def process_text(text):
    text = clean_text(text)

    if not text or len(text) < 20:
        return {
            "definitions": [],
            "definitions_ro": [],
            "definitions_en": [],
        }

    units = build_candidate_units(text)
    all_sentences = []

    for unit in units:
        lang = detect_language(unit)
        sentences = split_sentences_block(unit, lang)
        all_sentences.extend(sentences)

    definitions = extract_definitions(all_sentences)

    definitions_ro = [item for item in definitions if item.get("language") == "ro"]
    definitions_en = [item for item in definitions if item.get("language") == "en"]

    return {
        "definitions": definitions,
        "definitions_ro": definitions_ro,
        "definitions_en": definitions_en,
    }


# extrage rapid doar lista finala de concepte si definitii din text
def extract_concepts(text):
    result = process_text(text)
    return result["definitions"]