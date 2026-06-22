"""
ExamSense+ - NLP Services
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- implementeaza logica principala de procesare NLP pentru extragerea definitiilor
- detecteaza limba textului si selecteaza pattern-urile potrivite
- curata si valideaza conceptele extrase din propozitii
- filtreaza rezultatele slabe si ordoneaza definitiile dupa calitate
- produce lista finala de definitii candidate folosita ulterior in aplicatie
- foloseste reguli generale, nu reguli dependente de un anumit document de test
"""

import re
import unicodedata

try:
    from langdetect import detect
except Exception:
    detect = None

from nlp.patterns import (
    ENGLISH_PATTERNS,
    ROMANIAN_PATTERNS,
    PATTERN_WEIGHTS,
    STRONG_ENGLISH_PATTERNS,
    STRONG_ROMANIAN_PATTERNS,
    WEAK_ENGLISH_PATTERNS,
    WEAK_ROMANIAN_PATTERNS,
)


WORD_CHARS = "A-Za-zĂÂÎȘȚăâîșț0-9_"

ROMANIAN_FUNCTION_WORDS = {
    "este", "sunt", "prin", "pentru", "care", "în", "in", "se", "un", "o", "unei",
    "unui", "aceasta", "acest", "aceste", "dintre", "între", "intre", "sau", "și", "si",
    "reprezintă", "reprezinta", "înseamnă", "inseamna", "utilizat", "folosit", "alcătuit",
}

ENGLISH_FUNCTION_WORDS = {
    "is", "are", "the", "a", "an", "of", "to", "for", "and", "or", "which", "that",
    "refers", "means", "consists", "used", "composed", "defined", "represents",
}

DISCOURSE_STARTS = {
    # romana
    "astfel", "așadar", "asadar", "deci", "prin", "pentru", "deoarece", "fiindca",
    "fiindcă", "daca", "dacă", "cand", "când", "unde", "care", "ce", "în", "in",
    "la", "din", "acesta", "aceasta", "această", "acestea", "acest", "acești", "acesti",
    "fiecare", "orice", "urmatorul", "următorul", "apoi", "dupa",
    "după", "exemplu", "observatie", "observație", "teorema", "lema", "demonstratie",
    "demonstrație", "procedura", "algoritm", "algoritmul", "pseudocod", "altfel", "pasul", "primul", "prima", "doilea", "doua", "două", "abia", "numai", "doar", "cum", "practic", "deși", "deşi", "desi",
    # engleza
    "therefore", "thus", "because", "when", "where", "which", "this", "that", "these",
    "those", "each", "every", "example", "note", "theorem", "lemma", "proof", "procedure",
    "algorithm", "step",
}

GENERIC_METADATA_WORDS = {
    "isbn", "issn", "doi", "copyright", "edition", "vol", "volume", "journal", "press",
    "publisher", "bibliografie", "bibliography", "references", "referinte", "referințe",
}

PROCEDURAL_VERBS_RO = {
    "calculeaza", "calculează", "determina", "determină", "obtine", "obține", "executa",
    "execută", "trimite", "primeste", "primește", "actualizeaza", "actualizează",
    "initializeaza", "inițializează", "seteaza", "setează", "returneaza", "returnează",
}

PROCEDURAL_VERBS_EN = {
    "calculate", "compute", "determine", "execute", "send", "receive", "update", "initialize",
    "set", "return", "repeat", "iterate", "print", "read", "write",
}


# detecteaza limba textului si o reduce la ro sau en

def detect_language(text):
    text_lower = f" {str(text).lower()} "
    tokens = re.findall(r"[a-zăâîșț]+", text_lower, flags=re.IGNORECASE)

    ro_score = 0
    en_score = 0

    if re.search(r"[ăâîșț]", text_lower):
        ro_score += 4

    ro_score += sum(1 for token in tokens if token in ROMANIAN_FUNCTION_WORDS)
    en_score += sum(1 for token in tokens if token in ENGLISH_FUNCTION_WORDS)

    # langdetect ajuta pe paragrafe mai lungi, dar pe propozitii scurte poate gresi
    if len(tokens) >= 5 and detect is not None:
        try:
            lang = detect(text)
            if "ro" in lang:
                ro_score += 3
            elif "en" in lang:
                en_score += 3
        except Exception:
            pass

    return "ro" if ro_score >= en_score and ro_score > 0 else "en"


# normalizeaza spatiile multiple din text

def normalize_spaces(text):
    return re.sub(r"\s+", " ", str(text)).strip()


# elimina diacriticele pentru comparatii mai robuste

def strip_diacritics(text):
    text = unicodedata.normalize("NFD", str(text))
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text


# construieste o cheie normalizata pentru comparatii si deduplicare

def normalize_key(text):
    text = strip_diacritics(str(text).lower())
    text = re.sub(r"[^a-z0-9_\-/ ]+", " ", text)
    return normalize_spaces(text)


# verifica daca textul contine multe simboluri matematice sau de cod

def symbol_density(text):
    if not text:
        return 0

    symbols = set("=+*/\\{}[]<>|∈⊕≤≥√∑∂Δθλ→←↔^~")
    return sum(1 for char in text if char in symbols) / max(len(text), 1)


# detecteaza tokeni lipiti sau foarte artificiali aparuti in PDF-uri
def suspicious_token_ratio(text):
    tokens = re.findall(r"\S+", str(text))

    if not tokens:
        return 0

    suspicious = 0

    for token in tokens:
        clean = token.strip(".,:;!?()[]{}")

        if not clean:
            continue

        # tokeni lungi fara separatori, cu multe schimbari litera/cifra, apar des in formule/pseudocod lipit
        if len(clean) >= 18 and not re.search(r"[-/]", clean):
            suspicious += 1
            continue

        if re.search(r"[A-Za-zĂÂÎȘȚăâîșț]{3,}\d", clean) and not re.fullmatch(r"[A-Z]{2,}\d+", clean):
            suspicious += 1
            continue

        if re.search(r"[a-zăâîșț][A-ZĂÂÎȘȚ]", clean):
            suspicious += 1
            continue

    return suspicious / max(len(tokens), 1)


# detecteaza fragmente bibliografice sau metadate academice in mod general

def is_metadata_like(text):
    lower = normalize_key(text)

    if any(word in lower.split() for word in GENERIC_METADATA_WORDS):
        return True

    patterns = [
        r"\bISBN(?:-1[03])?:?\s*[0-9Xx\- ]{8,}\b",
        r"\bISSN:?\s*[0-9Xx\- ]{7,}\b",
        r"\bdoi\s*[:/]\s*10\.\d+/.+",
        r"\bpp\.?\s*\d+\s*[-–]\s*\d+\b",
        r"\bvol\.?\s*\d+\b",
        r"\b\d+(st|nd|rd|th)\s+edition\b",
    ]

    for pattern in patterns:
        if re.search(pattern, str(text), flags=re.IGNORECASE):
            return True

    return False


# detecteaza linii de pseudocod, formule sau tabele, fara cuvinte specifice unui document

def is_formula_or_code_like(text):
    text = normalize_spaces(text)

    if not text:
        return True

    digit_ratio = sum(char.isdigit() for char in text) / max(len(text), 1)
    if digit_ratio > 0.35:
        return True

    if symbol_density(text) > 0.10:
        return True

    # simbolurile matematice rare sunt aproape intotdeauna formule sau notatii, nu definitii naturale
    if re.search(r"[∈⊕≤≥√∑∂Δθλ→←↔]", text):
        return True

    # egalul, plus/minus intre variabile si notatia O(...) indica formule/pseudocod
    if re.search(r"[A-Za-z0-9]\s*[=+]\s*[A-Za-z0-9]", text):
        return True

    if re.search(r"\bO\s*\(", text):
        return True

    if suspicious_token_ratio(text) > 0.10:
        return True

    # multe variabile scurte si operatori indica formula/pseudocod, nu definitie naturala
    tokens = text.split()
    short_tokens = [token for token in tokens if re.fullmatch(r"[A-Za-z][A-Za-z]?\d*", token)]
    if len(tokens) >= 5 and len(short_tokens) / len(tokens) > 0.55 and symbol_density(text) > 0.04:
        return True

    # structuri comune de pseudocod
    code_patterns = [
        r"\b(for|while|if|else|return|procedure|function|begin|end)\b",
        r"\b(pentru|daca|dacă|altfel|procedura|functie|funcție)\b",
        r"^\d+\s*:\s*",
        r"\b[A-Za-z_]\w*\s*←\s*",
        r"\b[A-Za-z_]\w*\s*=\s*[^.]+$",
    ]

    matches = 0
    for pattern in code_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            matches += 1

    if matches >= 2:
        return True

    return False


# detecteaza instructiuni/proceduri; ele pot contine pattern-uri, dar nu sunt definitii bune

def is_procedural_like(text):
    lower = strip_diacritics(text.lower())
    tokens = set(re.findall(r"[a-zăâîșț]+", lower, flags=re.IGNORECASE))

    if tokens & {strip_diacritics(word) for word in PROCEDURAL_VERBS_RO}:
        # daca incepe cu pas/etapa/faza sau contine numerotare, e foarte probabil instructiune
        if re.search(r"\b(pasul|pas|etapa|faza|iteratia|iterația)\b", lower):
            return True

    if tokens & PROCEDURAL_VERBS_EN:
        if re.search(r"\b(step|phase|iteration)\b", lower):
            return True

    return False


# verifica daca textul seamana mai degraba cu un titlu decat cu o definitie

def is_heading_like(text):
    text = normalize_spaces(text)

    if not text:
        return True

    words = text.split()

    if len(words) <= 2:
        return True

    has_definition_verb = re.search(
        r"\b(este|sunt|reprezintă|reprezinta|înseamnă|inseamna|is|are|means|refers)\b",
        text,
        flags=re.IGNORECASE,
    )

    if text.endswith(":") and len(words) <= 10 and not has_definition_verb:
        return True

    # titlurile scurte au frecvent doar litere/cifre/separatoare si nu au verb
    if re.fullmatch(r"[\d.\-–—/:A-Za-zĂÂÎȘȚăâîșț ]+", text) and len(words) <= 6 and not has_definition_verb:
        return True

    return False


# filtreaza propozitiile care nu sunt potrivite pentru extractia definitiilor

def is_valid_sentence(sentence):
    sentence = normalize_spaces(sentence)

    if len(sentence) < 12:
        return False

    if len(sentence.split()) < 3:
        return False

    if is_heading_like(sentence):
        return False

    if is_metadata_like(sentence):
        return False

    if is_formula_or_code_like(sentence):
        return False

    if is_procedural_like(sentence):
        return False

    return True


# imparte o propozitie in fragmente independente; un rand poate contine doua definitii separate prin ;

def split_definition_clauses(sentence):
    sentence = normalize_spaces(sentence)

    # separam doar la ; sau la punct urmat de o propozitie noua cu majuscula
    pieces = re.split(r"\s*;\s*|(?<=[.!?])\s+(?=[A-ZĂÂÎȘȚ])", sentence)

    result = []

    for piece in pieces:
        piece = normalize_spaces(piece)

        if piece:
            result.append(piece)

    return result


# ia ultima parte relevanta din contextul din stanga al unei definitii

def split_left_context(raw_concept):
    raw_concept = normalize_spaces(raw_concept)

    if not raw_concept:
        return ""

    # daca partea dinaintea virgulei este doar marcator discursiv, pastram partea relevanta
    # exemplu general: "În general, conceptul este ..." -> "conceptul"
    if "," in raw_concept:
        left, right = raw_concept.split(",", 1)
        left_words = [word.lower() for word in left.split()]
        if left_words and all(word in DISCOURSE_STARTS for word in left_words):
            raw_concept = right.strip()

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


# incearca sa extraga tinta reala in expresii de tipul "rolul ..." sau "the role of ..."

def extract_role_target(text, lang):
    text = normalize_spaces(text)
    lower = text.lower()

    if lang == "en":
        patterns = [
            r"(?:the\s+role\s+of\s+the|the\s+role\s+of|role\s+of)\s+(.+)$",
            r"(?:the\s+term|term)\s+(.+)$",
        ]
    else:
        patterns = [
            r"rolul\s+(.+)$",
            r"(?:termenul|conceptul|noțiunea|notiunea)\s+(?:de\s+)?(.+)$",
        ]

    for pattern in patterns:
        match = re.search(pattern, lower)

        if match:
            start, end = match.span(1)
            target = normalize_spaces(text[start:end])

            if normalize_key(target) not in {"sau", "sa", "sau", "sau", "sau"}:
                return target

    return text


# extrage conceptul cand definitia este introdusa de un autor: "X definea conceptul ca fiind..."

def extract_concept_after_definition_verb(text):
    text = normalize_spaces(text)

    verb_patterns = [
        r"(?:definea|defineau|definește|defineste|defines|defined|define)\s+(.+)$",
        r"(?:numit|numită|numita|called|named)\s+(.+)$",
    ]

    for pattern in verb_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            return normalize_spaces(match.group(1))

    return text


# elimina prefixele slabe din concept, dar pastreaza literele mari din acronime

def remove_concept_prefixes(text):
    text = normalize_spaces(text)

    removable_prefixes = [
        "un ", "o ", "unei ", "unui ", "a ", "an ", "the ",
        "termenul de ", "termenul ", "conceptul de ", "conceptul ",
        "noțiunea de ", "notiunea de ", "noțiunea ", "notiunea ",
        "the term ", "term ",
        "definiții ", "definitii ", "definition ", "definitions ",
    ]

    changed = True

    while changed:
        changed = False
        lower = text.lower()

        for prefix in removable_prefixes:
            if lower.startswith(prefix):
                text = text[len(prefix):].strip()
                changed = True
                break

    return normalize_spaces(text)


# curata partea de concept inainte sa fie salvata

def extract_concept_smart(raw_concept, lang):
    raw_concept = split_left_context(raw_concept)
    raw_concept = extract_role_target(raw_concept, lang)
    raw_concept = extract_concept_after_definition_verb(raw_concept)
    raw_concept = normalize_spaces(raw_concept)

    if not raw_concept:
        return ""

    # eliminam citari si paranteze explicative din partea de concept
    raw_concept = re.sub(r"\[[^\]]+\]", " ", raw_concept)
    raw_concept = re.sub(r"\([^)]*\)", " ", raw_concept)
    raw_concept = normalize_spaces(raw_concept)

    # caz general: "Concept in/în context este ..." -> conceptul probabil este partea scurta din fata
    context_split = re.split(r"\s+(?:în|in)\s+", raw_concept, maxsplit=1, flags=re.IGNORECASE)

    if len(context_split) == 2:
        left = remove_concept_prefixes(context_split[0])
        right = context_split[1]

        if 1 <= len(left.split()) <= 5 and len(right.split()) >= 2:
            raw_concept = left

    raw_concept = remove_concept_prefixes(raw_concept)

    if not raw_concept:
        return ""

    words = raw_concept.split()

    # daca partea stanga este lunga, pastram coada cea mai probabila a sintagmei
    if len(words) > 8:
        words = words[-6:]

    return " ".join(words)


# curata si normalizeaza conceptul extras

def clean_concept(text):
    text = normalize_spaces(text)

    if not text:
        return ""

    text = re.sub(r"^[\-\•\*\–\—\s]+", "", text)
    text = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)
    text = re.sub(r"^[^\wĂÂÎȘȚăâîșț]+", "", text)
    text = re.sub(r"\[[^\]]+\]", " ", text)
    text = re.sub(r"\([^)]*\)", " ", text)
    text = normalize_spaces(text)

    text = remove_concept_prefixes(text)

    if not text:
        return ""

    # eliminam resturi finale de punctuatie
    text = text.strip(" .,:;!?-–—")

    if any(char in text for char in ['"', "“", "”", ";", ",", "(", ")"]):
        return ""

    return normalize_spaces(text)


# verifica daca forma finala a conceptului este suficient de buna

def is_valid_concept(concept):
    concept = normalize_spaces(concept)
    words = concept.split()

    if not words:
        return False

    if len(words) > 7:
        return False

    if len(concept) < 2 or len(concept) > 80:
        return False

    concept_key = normalize_key(concept)

    bad_exact = {
        "fi", "nu", "sau", "si", "iar", "dar", "ce", "care", "unde", "cand", "când",
        "daca", "dacă", "it", "this", "that", "documentul", "scopul", "rolul", "acesta",
        "aceasta", "această", "metoda", "metodă", "algoritmul", "termenul", "descriere", "ideea",
        "deosebirile", "observatii", "observații", "comentarii",
        "conceptul", "definition", "definitions",
    }

    if concept_key in bad_exact:
        return False

    if words[0].lower() in DISCOURSE_STARTS:
        return False

    if words[-1].lower() in {"de", "of", "the", "a", "an", "și", "si", "and", "or", "în", "in"}:
        return False

    if any(word.lower() in {"care", "ce", "which", "that", "și", "si", "and", "or", "sau", "nu"} for word in words):
        return False

    if any(word.lower() in {"fiecare", "each", "orice", "every", "altfel"} for word in words):
        return False

    if any(word.lower().strip(".:") in {"figura", "figure", "tabelul", "table", "grafic", "graph"} for word in words):
        return False

    if concept.lower().endswith(" e"):
        return False

    if re.search(r"[{}\[\]⊕∈≤≥√=+*/\\]", concept):
        return False

    if suspicious_token_ratio(concept) > 0:
        return False

    if is_metadata_like(concept):
        return False

    # un singur cuvant foarte scurt este de obicei variabila extrasa din formule, nu concept
    if len(words) == 1 and len(concept) <= 3 and not concept.isupper():
        return False

    # excludem identificatori de tip variabila+index, dar pastram acronimele curate
    if re.fullmatch(r"[A-Za-zĂÂÎȘȚăâîșț]+\d+", concept):
        letters = re.sub(r"[^A-Za-zĂÂÎȘȚăâîșț]", "", concept)
        if len(letters) < 2 or not concept.isupper():
            return False

    # evitam concepte care contin deja verbul de definitie
    bad_inside = {" este ", " sunt ", " is ", " are ", " se ", " reprezinta ", " înseamnă "}
    padded = f" {concept.lower()} "

    if any(value in padded for value in bad_inside):
        return False

    # daca toate cuvintele sunt foarte scurte, e mai degraba notatie
    if all(len(word) <= 2 for word in words) and not concept.isupper():
        return False

    return True


# curata partea de definitie extrasa dupa pattern

def clean_definition(text):
    text = normalize_spaces(text)

    if not text:
        return ""

    text = re.sub(r"^[\-\–\—:,\s]+", "", text)
    text = re.sub(r"\[[^\]]+\]", " ", text)
    text = normalize_spaces(text)

    # eliminam resturi de figuri/tabele atasate de definitie, regula generala pentru documente academice
    text = re.split(r"\s+(?:Figura|Fig\.|Tabelul|Table|Figure)\s+\d+", text, maxsplit=1, flags=re.IGNORECASE)[0]
    text = normalize_spaces(text)

    # daca definitia contine o noua eticheta de sectiune, o taiem acolo
    text = re.split(r"\s+\d+(\.\d+)+\.?\s+", text, maxsplit=1)[0]
    text = normalize_spaces(text)

    text = text.strip(" .")
    text = re.sub(r"\b(i\.e|e\.g|engl|ex)$", "", text, flags=re.IGNORECASE).strip(" .,;:")
    return text


# valideaza propozitiile cu pattern-uri slabe de tip "este/is"

def accepts_weak_pattern(concept, definition, pattern, lang):
    weak_patterns = WEAK_ROMANIAN_PATTERNS if lang == "ro" else WEAK_ENGLISH_PATTERNS

    if pattern not in weak_patterns:
        return True

    concept_words = len(concept.split())
    definition_words = len(definition.split())

    if concept_words > 5:
        return False

    if not (4 <= definition_words <= 35):
        return False

    # definitia trebuie sa arate ca o explicatie, nu ca o instructiune sau fragment tehnic
    if is_formula_or_code_like(definition) or is_procedural_like(definition):
        return False

    if definition.lower().split()[0] in DISCOURSE_STARTS:
        return False

    return True


# mai filtreaza o data definitiile dupa cateva reguli simple de calitate

def is_good_definition(item):
    definition = item["definition"].strip()
    concept = item["concept"].strip()

    word_count = len(definition.split())

    if word_count < 3:
        return False

    if word_count > 60:
        return False

    if definition.lower().startswith(("si ", "și ", "iar ", "dar ", "and ", "or ")):
        return False

    if not is_valid_concept(concept):
        return False

    if is_metadata_like(definition):
        return False

    if is_formula_or_code_like(definition):
        return False

    if suspicious_token_ratio(definition) > 0.05:
        return False

    if is_procedural_like(definition):
        return False

    if re.search(r"\b(Algoritmul|Algorithm|Teorema|Theorem|Lema|Lemma|Figura|Figure|Tabelul|Table)\b", definition):
        return False

    digit_ratio = sum(char.isdigit() for char in definition) / max(len(definition), 1)
    if digit_ratio > 0.25:
        return False

    return True


# construieste un regex robust pentru un pattern textual

def build_pattern_regex(pattern):
    escaped = re.escape(pattern)
    escaped = escaped.replace(r"\ ", r"\s+")
    return rf"(?<![{WORD_CHARS}]){escaped}(?![{WORD_CHARS}])"


# cauta primul pattern valid dintr-un fragment

def find_pattern_match(text, patterns):
    for pattern in patterns:
        regex = build_pattern_regex(pattern)
        match = re.search(regex, text, flags=re.IGNORECASE)

        if match:
            return pattern, match

    return None, None


# verifica daca un concept apare si in lista de cuvinte cheie

def keyword_boost(concept, keywords):
    if not keywords:
        return 0

    concept_key = normalize_key(concept)

    for keyword in keywords:
        keyword_key = normalize_key(keyword)

        if not keyword_key:
            continue

        if concept_key == keyword_key:
            return 3

        if concept_key in keyword_key or keyword_key in concept_key:
            return 1

    return 0


# calculeaza un scor simplu pentru a ordona definitiile mai bune in fata

def score_definition(item, keywords=None):
    score = 0

    concept = item["concept"]
    definition = item["definition"]
    pattern = item["pattern"]
    lang = item.get("language", "en")

    concept_words = len(concept.split())
    definition_words = len(definition.split())

    if 1 <= concept_words <= 4:
        score += 4
    elif 5 <= concept_words <= 7:
        score += 2
    else:
        score -= 4

    if 4 <= definition_words <= 25:
        score += 4
    elif 26 <= definition_words <= 45:
        score += 2
    else:
        score -= 3

    score += PATTERN_WEIGHTS.get(pattern, 1)

    strong_patterns = STRONG_ROMANIAN_PATTERNS if lang == "ro" else STRONG_ENGLISH_PATTERNS
    if pattern in strong_patterns:
        score += 2

    weak_patterns = WEAK_ROMANIAN_PATTERNS if lang == "ro" else WEAK_ENGLISH_PATTERNS
    if pattern in weak_patterns:
        score -= 1

    if symbol_density(definition) > 0.05:
        score -= 3

    digit_ratio = sum(char.isdigit() for char in definition) / max(len(definition), 1)
    if digit_ratio > 0.15:
        score -= 2

    # acronimele si termenii tehnici sunt importanti in cursuri, daca sunt curate
    if re.fullmatch(r"[A-ZĂÂÎȘȚ0-9]{2,}([-/][A-ZĂÂÎȘȚ0-9]+)?", concept):
        score += 2

    score += keyword_boost(concept, keywords)

    return score


# creeaza un item standard, compatibil cu fluxul existent din aplicatie

def build_definition_item(concept, definition, pattern, lang, sentence, keywords=None):
    item = {
        "concept": concept,
        "definition": definition,
        "pattern": pattern,
        "language": lang,
        "sentence": sentence,
    }

    item["_score"] = score_definition(item, keywords=keywords)

    return item


# incearca sa extraga definitii din forme de tipul "Concept - definitie: ..."

def extract_labeled_definition(sentence, keywords=None):
    sentence = normalize_spaces(sentence)

    patterns = [
        r"^(?P<concept>.+?)\s*[:\-–—]\s*(?:definiție|definitie|definition)\s*[:\-–—]\s*(?P<definition>.+)$",
        r"^(?:definiție|definitie|definition)\s*[:\-–—]\s*(?P<concept>.+?)\s+(?:este|is)\s+(?P<definition>.+)$",
    ]

    result = []

    for pattern in patterns:
        match = re.search(pattern, sentence, flags=re.IGNORECASE)

        if not match:
            continue

        lang = detect_language(sentence)
        concept = clean_concept(extract_concept_smart(match.group("concept"), lang))
        definition = clean_definition(match.group("definition"))

        if concept and definition and is_valid_concept(concept) and is_good_definition({
            "concept": concept,
            "definition": definition,
        }):
            result.append(build_definition_item(
                concept,
                definition,
                "definitie:",
                lang,
                sentence,
                keywords=keywords,
            ))

    return result


# extrage definitii dintr-o singura clauza

def extract_from_clause(clause, original_sentence, keywords=None):
    lang = detect_language(clause)
    patterns = ROMANIAN_PATTERNS if lang == "ro" else ENGLISH_PATTERNS

    pattern, match = find_pattern_match(clause, patterns)

    if not match:
        # propozitiile mixte romana/engleza pot fi detectate gresit; incercam si cealalta lista
        alternative_lang = "en" if lang == "ro" else "ro"
        alternative_patterns = ENGLISH_PATTERNS if alternative_lang == "en" else ROMANIAN_PATTERNS
        pattern, match = find_pattern_match(clause, alternative_patterns)

        if match:
            lang = alternative_lang

    if not match:
        return None

    raw_concept = clause[:match.start()].strip()
    raw_definition = clause[match.end():].strip()

    concept = extract_concept_smart(raw_concept, lang)
    concept = clean_concept(concept)
    definition = clean_definition(raw_definition)

    if not concept or not is_valid_concept(concept):
        return None

    if not definition or len(definition.split()) < 3:
        return None

    if not accepts_weak_pattern(concept, definition, pattern, lang):
        return None

    item = build_definition_item(
        concept=concept,
        definition=definition,
        pattern=pattern,
        lang=lang,
        sentence=original_sentence,
        keywords=keywords,
    )

    if not is_good_definition(item):
        return None

    return item


# extrage toate definitiile candidate din lista de propozitii

def extract_definitions(sentences, keywords=None):
    keywords = keywords or []
    definitions = []

    for sentence in sentences:
        if not is_valid_sentence(sentence):
            continue

        original_sentence = normalize_spaces(sentence)

        # tratam separat formele explicite de tip "Concept: Definitie: ..."
        definitions.extend(extract_labeled_definition(original_sentence, keywords=keywords))

        for clause in split_definition_clauses(original_sentence):
            if not is_valid_sentence(clause):
                continue

            item = extract_from_clause(clause, original_sentence, keywords=keywords)

            if item is not None:
                definitions.append(item)

    # eliminam duplicatele exacte
    unique = []
    seen = set()

    for item in definitions:
        key = (
            normalize_key(item["concept"]),
            normalize_key(item["definition"]),
            item["language"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    # ordonam definitiile in functie de scor
    unique = sorted(unique, key=lambda value: value.get("_score", 0), reverse=True)

    # pastram doar item-urile peste un prag minim general, ca sa nu ajunga zgomot in quiz
    filtered = [item for item in unique if is_good_definition(item) and item.get("_score", 0) >= 5]

    if not filtered:
        filtered = [item for item in unique if is_good_definition(item)]

    # pastram o singura definitie finala pentru fiecare concept si limba
    final = []
    seen_keys = set()

    for item in filtered:
        key = (normalize_key(item["concept"]), item["language"])

        if key in seen_keys:
            continue

        seen_keys.add(key)

        # nu trimitem mai departe campuri interne
        public_item = {
            "concept": item["concept"],
            "definition": item["definition"],
            "pattern": item["pattern"],
            "language": item["language"],
            "sentence": item["sentence"],
        }

        final.append(public_item)

    return final[:80]
