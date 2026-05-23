from nlp.patterns import ROMANIAN_PATTERNS, ENGLISH_PATTERNS
from langdetect import detect
import re


def detect_language(text):
    try:
        lang = detect(text)
        return "ro" if "ro" in lang else "en"
    except:
        return "en"


def extract_definitions(sentences):
    definitions = []

    for sentence in sentences:
        original_sentence = sentence.strip()
        sentence_lower = original_sentence.lower()

        # ignoram propozitii prea scurte
        if len(sentence_lower) < 10:
            continue

        lang = detect_language(sentence_lower)

        patterns = ROMANIAN_PATTERNS if lang == "ro" else ENGLISH_PATTERNS

        for pattern in patterns:
            if pattern in sentence_lower:

                parts = sentence_lower.split(pattern)

                if len(parts) < 2:
                    continue

                concept = parts[0].strip()
                definition = parts[1].strip()

                # curatare concept
                concept = clean_concept(concept)

                # filtrare concept slab
                if not concept or len(concept) < 3:
                    continue

                # filtrare definitii slabe
                if len(definition.split()) < 3:
                    continue

                if definition.startswith(("si", "sau", "iar", "and", "or")):
                    continue

                definitions.append({
                    "concept": concept,
                    "definition": definition,
                    "pattern": pattern,
                    "language": lang,
                    "sentence": original_sentence
                })

                break

    # eliminare duplicate
    unique = []
    seen = set()

    for d in definitions:
        key = (d["concept"], d["definition"])

        if key not in seen:
            seen.add(key)
            unique.append(d)

    # sortare dupa calitate (definitii mai lungi = mai bune)
    unique = sorted(
        unique,
        key=lambda x: len(x["definition"]),
        reverse=True
    )

    return unique


def clean_concept(text):
    text = text.strip().lower()

    # elimina bullet-uri si simboluri
    text = re.sub(r"^[\-\•\*\–\—\s]+", "", text)

    # elimina numerotari (1., 1.2, 1.2.3)
    text = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)

    # elimina caractere non-litera la inceput
    text = re.sub(r"^[^a-zA-ZăâîșțĂÂÎȘȚ]+", "", text)

    # elimina articole
    articles = ["un ", "o ", "the ", "a ", "an "]

    for art in articles:
        if text.startswith(art):
            text = text[len(art):]

    # elimina concepte inutile
    stop_words = [
        "si", "sau", "iar", "dar",
        "care", "ce", "la", "in", "cu",
        "pentru", "asupra", "de"
    ]

    if text in stop_words:
        return ""

    # prea scurt = inutil
    if len(text) < 3:
        return ""

    return text.strip()