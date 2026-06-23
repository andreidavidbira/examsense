"""
ExamSense+ - NLP Services
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- orchestreaza fluxul NLP complet pentru documentele incarcate
- curata textul brut si construieste unitati candidate
- detecteaza rapid limba fara a incarca modele NLP grele la import
- imparte textul in propozitii prin reguli rapide si stabile
- intoarce definitiile finale folosite de generatorul NLP de intrebari
"""

import re
import time

try:
    from langdetect import detect
except Exception:
    detect = None

from nlp.definition_extractor import detect_sentence_language, extract_definitions, has_definition_signal
from nlp.text_cleaner import clean_text, is_probable_heading, normalize_spaces

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZĂÂÎȘȚ0-9])")


# detectam limba textului si o reducem la ro sau en
def detect_language(text):
    text = normalize_spaces(text)

    if not text:
        return "en"

    sample = text[:4000]
    lower = f" {sample.lower()} "

    ro_chars = len(re.findall(r"[ăâîșşțţĂÂÎȘŞȚŢ]", sample))
    ro_hits = sum(1 for word in (" este ", " sunt ", " care ", " pentru ", " prin ", " într", " intr", " poate ") if word in lower)
    en_hits = sum(1 for word in (" is ", " are ", " the ", " which ", " with ", " from ", " that ", " can ") if word in lower)

    if ro_chars or ro_hits > en_hits:
        return "ro"

    if en_hits > ro_hits:
        return "en"

    if detect:
        try:
            lang = detect(sample)
            return "ro" if lang == "ro" else "en"
        except Exception:
            pass

    return "en"


# impartim rapid textul in propozitii, fara sa pierdem partea de concept
# nu mai separam inainte de "este/is", deoarece se pierdea conceptul din stanga verbului
def split_sentences_block(text, lang=None):
    text = normalize_spaces(text)

    if not text:
        return []

    sentences = []

    for piece in _SENTENCE_SPLIT_RE.split(text):
        piece = normalize_spaces(piece)

        if len(piece.split()) < 4:
            continue

        if has_definition_signal(piece):
            sentences.append(piece)

    return sentences


# construim unitati de text mai mari, ca sa evitam headingurile si randurile rupte
def build_candidate_units(text):
    lines = [normalize_spaces(line) for line in text.split("\n") if normalize_spaces(line)]
    units = []
    current = []

    for line in lines:
        if is_probable_heading(line):
            if current:
                unit = " ".join(current).strip()

                if has_definition_signal(unit):
                    units.append(unit)

                current = []

            continue

        current.append(line)
        current_text = " ".join(current).strip()

        if line.endswith((".", "!", "?", ":")) or len(current_text.split()) >= 75:
            if has_definition_signal(current_text):
                units.append(current_text)

            current = []

    if current:
        unit = " ".join(current).strip()

        if has_definition_signal(unit):
            units.append(unit)

    return [unit for unit in units if len(unit.split()) >= 4]


# curatam textul, il impartim in propozitii si extragem definitiile finale
def process_text(text):
    start_time = time.perf_counter()
    text = clean_text(text)

    if not text or len(text) < 20:
        return {
            "definitions": [],
            "definitions_ro": [],
            "definitions_en": [],
        }

    lang = detect_language(text)
    units = build_candidate_units(text)
    all_sentences = []

    for unit in units:
        unit_lang = detect_sentence_language(unit[:800]) if len(unit) < 800 else lang
        all_sentences.extend(split_sentences_block(unit, unit_lang))

    definitions = extract_definitions(all_sentences)
    definitions_ro = [item for item in definitions if item.get("language") == "ro"]
    definitions_en = [item for item in definitions if item.get("language") == "en"]

    duration = time.perf_counter() - start_time
    print(
        f"[NLP PIPELINE] chars={len(text)}, units={len(units)}, "
        f"sentences={len(all_sentences)}, definitions={len(definitions)}, duration={duration:.4f}s"
    )

    return {
        "definitions": definitions,
        "definitions_ro": definitions_ro,
        "definitions_en": definitions_en,
    }


# extragem rapid doar lista de concepte/definitii rezultate din text
def extract_concepts(text):
    result = process_text(text)
    return result["definitions"]
