from nlp.patterns import ROMANIAN_PATTERNS, ENGLISH_PATTERNS
from langdetect import detect


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

                # curatare simpla concept
                concept = clean_concept(concept)

                if len(concept) < 3 or len(definition) < 5:
                    continue

                definitions.append({
                    "concept": concept,
                    "definition": definition,
                    "pattern": pattern,
                    "language": lang,
                    "sentence": original_sentence
                })

                break

    return definitions


def clean_concept(text):
    # elimina numerotari si simboluri
    text = text.strip()

    prefixes = ["-", "•", "*"]
    for p in prefixes:
        if text.startswith(p):
            text = text[1:].strip()

    # elimina numerotari gen "1.2.3"
    while len(text) > 0 and (text[0].isdigit() or text[0] == "."):
        text = text[1:].strip()

    return text