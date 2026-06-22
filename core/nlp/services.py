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
- pastreaza structura trimisa mai departe catre quiz/documents
"""

import re

import spacy

try:
    from langdetect import detect
except Exception:
    detect = None

from nlp.concept_extractor import extract_keywords
from nlp.definition_extractor import extract_definitions
from nlp.text_cleaner import clean_text


# incarca in siguranta un model spaCy; daca modelul nu exista, folosim un model blank cu sentencizer

def load_spacy_model(model_name, lang_code):
    try:
        model = spacy.load(model_name)
    except Exception:
        model = spacy.blank(lang_code)

        if "sentencizer" not in model.pipe_names:
            model.add_pipe("sentencizer")

    # documentele pot fi lungi, deci marim limita implicita
    model.max_length = max(model.max_length, 3_000_000)

    return model


# incarcam modelele spaCy pentru romana si engleza
nlp_ro = load_spacy_model("ro_core_news_sm", "ro")
nlp_en = load_spacy_model("en_core_web_sm", "en")


# detecteaza limba textului si o reduce la ro sau en

def detect_language(text):
    text_lower = f" {str(text).lower()} "

    ro_markers = ["ă", "â", "î", "ș", "ț", " este ", " sunt ", " prin ", " pentru ", " în "]
    en_markers = [" is ", " are ", " the ", " of ", " to ", " refers to ", " means "]

    ro_score = sum(1 for marker in ro_markers if marker in text_lower)
    en_score = sum(1 for marker in en_markers if marker in text_lower)

    if detect is not None and len(text.split()) >= 5:
        try:
            lang = detect(text)
            if "ro" in lang:
                ro_score += 2
            elif "en" in lang:
                en_score += 2
        except Exception:
            pass

    return "ro" if ro_score >= en_score and ro_score > 0 else "en"


# normalizeaza spatiile multiple din text

def normalize_spaces(text):
    return re.sub(r"\s+", " ", str(text)).strip()


# verifica daca o linie pare titlu de sectiune/slide

def is_probable_heading(line):
    line = normalize_spaces(line)

    if not line:
        return False

    simplified = re.sub(r"^\d+(\.\d+)*\.?\s*", "", line).strip()
    words = simplified.split()

    if not words or len(words) > 12:
        return False

    has_definition_verb = re.search(
        r"\b(este|sunt|reprezintă|reprezinta|înseamnă|inseamna|is|are|means|refers)\b",
        simplified,
        flags=re.IGNORECASE,
    )

    if has_definition_verb:
        return False

    if simplified.endswith((".", "!", "?", ";")):
        return False

    if len(words) <= 4:
        return True

    letters = [char for char in simplified if char.isalpha()]
    uppercase_ratio = sum(char.isupper() for char in letters) / max(len(letters), 1)

    if uppercase_ratio > 0.65:
        return True

    return False


# construieste unitati de text mai mari, pentru a evita liniile foarte scurte de tip heading

def build_candidate_units(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    units = []
    current = []

    for line in lines:
        if is_probable_heading(line):
            if current:
                units.append(" ".join(current).strip())
                current = []
            continue

        current.append(line)

        # daca linia pare incheiata, inchidem unitatea curenta
        if line.endswith((".", "!", "?")):
            units.append(" ".join(current).strip())
            current = []

        # evitam unitati exagerat de mari
        elif sum(len(piece.split()) for piece in current) >= 90:
            units.append(" ".join(current).strip())
            current = []

    if current:
        units.append(" ".join(current).strip())

    return units


# imparte textul in propozitii folosind modelul corespunzator limbii detectate

def split_sentences_block(text, lang):
    text = normalize_spaces(text)

    if not text:
        return []

    try:
        doc = nlp_ro(text) if lang == "ro" else nlp_en(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

        if sentences:
            return sentences
    except Exception:
        pass

    # fallback simplu daca spaCy nu poate procesa textul
    return [piece.strip() for piece in re.split(r"(?<=[.!?])\s+", text) if piece.strip()]


# extrage un set moderat de keywords pentru ranking, fara sa proceseze tot documentul imens cu KeyBERT

def extract_ranking_keywords(text):
    # luam un esantion din inceput, mijloc si final; regula este generala pentru documente lungi
    text = normalize_spaces(text)

    if len(text) <= 12000:
        sample = text
    else:
        part = 4000
        middle_start = max((len(text) // 2) - (part // 2), 0)
        sample = text[:part] + " " + text[middle_start:middle_start + part] + " " + text[-part:]

    return extract_keywords(sample, top_n=40)


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

    keywords = extract_ranking_keywords(text)
    definitions = extract_definitions(all_sentences, keywords=keywords)

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
