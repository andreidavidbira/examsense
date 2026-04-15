import re
from nlp.patterns import ROMANIAN_PATTERNS, ENGLISH_PATTERNS


def extract_definitions(sentences):
    definitions = []

    for sent in sentences:
        text = sent.strip().lower()

        found = False

        # ROMANA
        for pattern in ROMANIAN_PATTERNS:
            pattern_regex = r'\b' + re.escape(pattern) + r'\b'
            if re.search(pattern_regex, text): # de exemplu pentru "is" sa fie detectat in interiorul altor cuvinte
                parts = text.split(pattern, 1)
                found = True
                break

        # ENGLEZA
        if not found:
            for pattern in ENGLISH_PATTERNS:
                pattern_regex = r'\b' + re.escape(pattern) + r'\b'
                if re.search(pattern_regex, text): # la fel ca mai sus
                    parts = text.split(pattern, 1)
                    found = True
                    break

        if not found:
            continue

        if len(parts) == 2:
            concept = parts[0].strip()
            definition = parts[1].strip()

            # filtrare
            if len(concept) > 2 and len(definition) > 5:
                definitions.append({
                    "concept": concept,
                    "definition": definition,
                    "pattern": pattern
                })

    return definitions