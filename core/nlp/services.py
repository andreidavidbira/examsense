import spacy
from langdetect import detect

from nlp.text_cleaner import clean_text
from nlp.definition_extractor import extract_definitions


nlp_ro = spacy.load("ro_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")


def detect_language(text):
    try:
        lang = detect(text)
        return "ro" if "ro" in lang else "en"
    except:
        return "en"


def split_sentences_block(text, lang):
    try:
        doc = nlp_ro(text) if lang == "ro" else nlp_en(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    except Exception:
        return [x.strip() for x in text.split(".") if x.strip()]


def build_candidate_units(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    units = []
    current = []

    for line in lines:
        # linii foarte scurte => cel mai probabil heading / eticheta
        if len(line.split()) <= 2:
            if current:
                units.append(" ".join(current).strip())
                current = []
            continue

        current.append(line)

        # daca linia pare incheiata, inchidem unitatea
        if line.endswith((".", "!", "?", ":")):
            units.append(" ".join(current).strip())
            current = []

    if current:
        units.append(" ".join(current).strip())

    return units


def process_text(text):
    text = clean_text(text)

    if not text or len(text) < 20:
        return {
            "definitions": [],
            "definitions_ro": [],
            "definitions_en": []
        }

    units = build_candidate_units(text)

    all_sentences = []

    for unit in units:
        lang = detect_language(unit)
        sentences = split_sentences_block(unit, lang)
        all_sentences.extend(sentences)

    definitions = extract_definitions(all_sentences)

    definitions_ro = [d for d in definitions if d.get("language") == "ro"]
    definitions_en = [d for d in definitions if d.get("language") == "en"]

    return {
        "definitions": definitions,
        "definitions_ro": definitions_ro,
        "definitions_en": definitions_en
    }


def extract_concepts(text):
    result = process_text(text)
    return result["definitions"]