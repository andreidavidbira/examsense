import re

from langdetect import detect

from nlp.patterns import ENGLISH_PATTERNS, ROMANIAN_PATTERNS


# detectam limba textului si o reducem la ro sau en
def detect_language(text):
    try:
        lang = detect(text)
        return "ro" if "ro" in lang else "en"
    except Exception:
        return "en"


# normalizam spatiile multiple din text
def normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


# verificam daca textul seamana mai degraba cu un titlu decat cu o definitie
def is_heading_like(text):
    text = normalize_spaces(text)

    if not text:
        return True

    if len(text.split()) <= 2:
        return True

    if re.fullmatch(r"[\d.\-–—/:A-Za-zĂÂÎȘȚăâîșț ]+", text) and len(text.split()) <= 4:
        return True

    return False


# filtram propozitiile care nu sunt potrivite pentru extractia definitiilor
def is_valid_sentence(sentence):
    sentence = normalize_spaces(sentence)
    sentence_lower = sentence.lower()

    if len(sentence) < 12:
        return False

    if is_heading_like(sentence):
        return False

    digit_ratio = sum(char.isdigit() for char in sentence) / max(len(sentence), 1)
    if digit_ratio > 0.45:
        return False

    math_symbols = ["=", "+", "*", "/", "Δ", "∑", "θ", "∂"]
    if sum(sentence.count(symbol) for symbol in math_symbols) > 3:
        return False

    bad_phrases = [
        "se calculeaza",
        "se determina",
        "se obtine",
        "actualizarea ponderilor",
        "corectiile ponderilor",
        "gradientul erorii",
        "presupunem ca rata",
    ]

    if any(phrase in sentence_lower for phrase in bad_phrases):
        return False

    return True


# luam ultima parte relevanta din contextul din stanga al unei definitii
def split_left_context(raw_concept):
    raw_concept = normalize_spaces(raw_concept)

    if not raw_concept:
        return ""

    separators = [".", ":", ";", " - ", " – ", " — "]
    parts = [raw_concept]

    for separator in separators:
        new_parts = []

        for part in parts:
            split_parts = [piece.strip() for piece in part.split(separator) if piece.strip()]
            new_parts.extend(split_parts)

        parts = new_parts

    if parts:
        return parts[-1]

    return raw_concept


# incercam sa extragem tinta reala in expresii de tipul "rolul ..."
def extract_role_target(text, lang):
    text = normalize_spaces(text)
    lower = text.lower()

    if lang == "en":
        patterns = [
            r"(?:the\s+role\s+of|role\s+of)\s+(.+)$",
            r"(?:the\s+role\s+of\s+the)\s+(.+)$",
        ]
    else:
        patterns = [
            r"rolul\s+(.+)$",
        ]

    for pattern in patterns:
        match = re.search(pattern, lower)

        if match:
            target = normalize_spaces(match.group(1))

            # excludem cateva potriviri foarte slabe
            if target not in {"său", "sau", "să"}:
                return target

    return text


# curatam partea de concept inainte sa o salvam
def extract_concept_smart(raw_concept, lang):
    raw_concept = split_left_context(raw_concept)
    raw_concept = extract_role_target(raw_concept, lang)
    raw_concept = normalize_spaces(raw_concept)

    if not raw_concept:
        return ""

    words = raw_concept.split()

    stop_starts = {"in", "la", "din", "pentru", "unde", "the", "a", "an"}

    while words and words[0].lower() in stop_starts:
        words.pop(0)

    if not words:
        return ""

    if len(words) > 6:
        words = words[-4:]

    return " ".join(words)


# curatam si normalizam conceptul extras
def clean_concept(text):
    text = normalize_spaces(text.lower())

    if not text:
        return ""

    text = re.sub(r"^[\-\•\*\–\—\s]+", "", text)
    text = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)
    text = re.sub(r"^[^\wăâîșț]+", "", text)
    text = normalize_spaces(text)

    if not text:
        return ""

    removable_prefixes = [
        "un ", "o ", "a ", "an ", "the ",
        "este ", "sunt ", "unde ", "cand ", "daca ",
        "english ", "definitions ", "definition ",
        "română ", "romana ", "definiții ", "definitii ",
        "set suplimentar de ",
        "generarea întrebărilor ",
        "generarea intrebarilor ",
    ]

    changed = True

    while changed:
        changed = False

        for prefix in removable_prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                changed = True

    text = normalize_spaces(text)

    if not text:
        return ""

    text = re.sub(r"^[a-z]\s+(definitions?|definiții|definitii)\s+", "", text)
    text = normalize_spaces(text)

    # excludem expresii care par a fi metadate bibliografice
    if any(value in text for value in ["edition", "isbn", "vol", "pp", "wesley"]):
        return ""

    if any(char in text for char in ["(", ")", "\"", "“", "”", ",", ";"]):
        return ""

    return text


# verificam daca forma finala a conceptului este suficient de buna
def is_valid_concept(concept):
    words = concept.split()

    if not words:
        return False

    if len(words) > 4:
        return False

    bad_words = {
        "si", "sau", "iar", "dar", "ce", "care", "unde", "cand", "daca", "nu",
        "english", "definitions", "definition", "română", "romana",
        "engl", "său", "sau",
    }

    if any(word in bad_words for word in words):
        return False

    if any(len(word) < 2 for word in words):
        return False

    return True


# mai filtram o data definitiile dupa cateva reguli simple de calitate
def is_good_definition(item):
    definition = item["definition"].strip().lower()
    concept = item["concept"].strip().lower()

    if len(definition.split()) < 3:
        return False

    if len(definition.split()) > 35:
        return False

    if definition.startswith(("si", "iar", "dar", "and", "or")):
        return False

    if concept in {"fi", "nu", "engl", "său", "sau"}:
        return False

    return True


# calculam un scor simplu pentru a ordona definitiile mai bune in fata
def score_definition(item):
    score = 0

    concept = item["concept"]
    definition = item["definition"]
    pattern = item["pattern"]

    if 1 <= len(concept.split()) <= 4:
        score += 3

    if 4 <= len(definition.split()) <= 20:
        score += 3
    elif 21 <= len(definition.split()) <= 30:
        score += 1
    else:
        score -= 2

    digit_ratio = sum(char.isdigit() for char in definition) / max(len(definition), 1)
    if digit_ratio > 0.2:
        score -= 3

    if any(symbol in definition for symbol in ["=", "+", "Δ", "∑", "θ"]):
        score -= 3

    strong_patterns = [
        "este", "reprezinta", "reprezintă",
        "is", "means", "represents",
        "este definit ca", "este definită ca",
        "is defined as", "can be defined as",
    ]

    if pattern in strong_patterns:
        score += 2

    return score


# extragem toate definitiile candidate din lista de propozitii
def extract_definitions(sentences):
    definitions = []

    for sentence in sentences:
        if not is_valid_sentence(sentence):
            continue

        original_sentence = normalize_spaces(sentence)
        sentence_lower = original_sentence.lower()

        lang = detect_language(sentence_lower)
        patterns = ROMANIAN_PATTERNS if lang == "ro" else ENGLISH_PATTERNS

        for pattern in patterns:
            if pattern not in sentence_lower:
                continue

            parts = sentence_lower.split(pattern, 1)

            if len(parts) < 2:
                continue

            raw_concept = parts[0].strip()
            definition = normalize_spaces(parts[1].strip())

            concept = extract_concept_smart(raw_concept, lang)
            concept = clean_concept(concept)

            if not concept or not is_valid_concept(concept):
                continue

            if len(definition.split()) < 3:
                continue

            definitions.append({
                "concept": concept,
                "definition": definition,
                "pattern": pattern,
                "language": lang,
                "sentence": original_sentence,
            })

            break

    # eliminam duplicatele exacte
    unique = []
    seen = set()

    for item in definitions:
        key = (item["concept"], item["definition"], item["language"])

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    # ordonam definitiile in functie de scor
    unique = sorted(unique, key=score_definition, reverse=True)

    filtered = [item for item in unique if is_good_definition(item)]
    if not filtered:
        filtered = unique

    # pastram o singura definitie finala pentru fiecare concept si limba
    final = []
    seen_keys = set()

    for item in filtered:
        key = (item["concept"], item["language"])

        if key in seen_keys:
            continue

        seen_keys.add(key)
        final.append(item)

    return final[:50]