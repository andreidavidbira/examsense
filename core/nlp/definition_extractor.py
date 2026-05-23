from langdetect import detect
import re

from nlp.patterns import ROMANIAN_PATTERNS, ENGLISH_PATTERNS


def detect_language(text):
    try:
        lang = detect(text)
        return "ro" if "ro" in lang else "en"
    except:
        return "en"


def normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


def is_heading_like(text):
    text = normalize_spaces(text)

    if not text:
        return True

    if len(text.split()) <= 2:
        return True

    if re.fullmatch(r"[\d.\-–—/:A-Za-zĂÂÎȘȚăâîșț ]+", text) and len(text.split()) <= 4:
        return True

    return False


def is_valid_sentence(sentence):
    sentence = normalize_spaces(sentence)
    sentence_lower = sentence.lower()

    if len(sentence) < 12:
        return False

    if is_heading_like(sentence):
        return False

    digit_ratio = sum(c.isdigit() for c in sentence) / max(len(sentence), 1)
    if digit_ratio > 0.45:
        return False

    math_symbols = ["=", "+", "*", "/", "Δ", "∑", "θ", "∂"]
    if sum(sentence.count(s) for s in math_symbols) > 3:
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

    if any(p in sentence_lower for p in bad_phrases):
        return False

    return True


def split_left_context(raw_concept):
    raw_concept = normalize_spaces(raw_concept)

    if not raw_concept:
        return ""

    separators = [".", ":", ";", " - ", " – ", " — "]
    parts = [raw_concept]

    for sep in separators:
        new_parts = []
        for part in parts:
            split_parts = [p.strip() for p in part.split(sep) if p.strip()]
            new_parts.extend(split_parts)
        parts = new_parts

    if parts:
        return parts[-1]

    return raw_concept


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

            # excludem cazuri precum "său"
            if target not in {"său", "sau", "să"}:
                return target

    return text


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

    if any(x in text for x in ["edition", "isbn", "vol", "pp", "wesley"]):
        return ""

    if any(c in text for c in ["(", ")", "\"", "“", "”", ",", ";"]):
        return ""

    return text


def is_valid_concept(concept):
    words = concept.split()

    if not words:
        return False

    if len(words) > 4:
        return False

    bad_words = {
        "si", "sau", "iar", "dar", "ce", "care", "unde", "cand", "daca", "nu",
        "english", "definitions", "definition", "română", "romana",
        "engl", "său", "sau"
    }

    if any(w in bad_words for w in words):
        return False

    if any(len(w) < 2 for w in words):
        return False

    return True


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

    digit_ratio = sum(c.isdigit() for c in definition) / max(len(definition), 1)
    if digit_ratio > 0.2:
        score -= 3

    if any(x in definition for x in ["=", "+", "Δ", "∑", "θ"]):
        score -= 3

    strong_patterns = [
        "este", "reprezinta", "reprezintă",
        "is", "means", "represents",
        "este definit ca", "este definită ca",
        "is defined as", "can be defined as"
    ]

    if pattern in strong_patterns:
        score += 2

    return score


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
                "sentence": original_sentence
            })

            break

    unique = []
    seen = set()

    for item in definitions:
        key = (item["concept"], item["definition"], item["language"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    unique = sorted(unique, key=score_definition, reverse=True)

    filtered = [item for item in unique if is_good_definition(item)]
    if not filtered:
        filtered = unique

    final = []
    seen_keys = set()

    for item in filtered:
        key = (item["concept"], item["language"])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        final.append(item)

    return final[:50]