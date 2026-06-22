"""
ExamSense+ - Quiz Generation Services
Copyright (c) Bira Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- genereaza intrebari de quiz pe baza definitiilor extrase
- construieste intrebari in romana si engleza
- alege tipul potrivit de intrebare in functie de dificultate si continut
- produce variante mai naturale de formulare pentru fiecare concept
- selecteaza distractori si construieste optiuni valide pentru quiz
- filtreaza definitiile zgomotoase inainte de generarea intrebarilor
- pastreaza formatul de iesire folosit deja de aplicatie
"""

import random
import re


# pattern-uri considerate mai puternice pentru intrebari directe de definitie
STRONG_DEFINITION_PATTERNS = {
    "este definit ca",
    "este definita ca",
    "este definita drept",
    "este definită ca",
    "este definită drept",
    "poate fi definit ca",
    "poate fi definita ca",
    "poate fi definită ca",
    "se defineste ca",
    "se definește ca",
    "se poate defini ca",
    "reprezinta",
    "reprezintă",
    "inseamna",
    "înseamnă",
    "is defined as",
    "can be defined as",
    "is commonly defined as",
    "is generally defined as",
    "means",
    "represents",
}


# pattern-uri care indica rolul, utilizarea, structura sau referinta unui concept
ROLE_PATTERNS = {
    "are rolul de",
    "are scopul de",
    "serveste la",
    "servește la",
    "serves to",
    "serves as",
    "is intended to",
    "is designed to",
}

USAGE_PATTERNS = {
    "este utilizat pentru",
    "este utilizata pentru",
    "este utilizată pentru",
    "este folosit pentru",
    "este folosita pentru",
    "este folosită pentru",
    "este utilizat in",
    "este utilizata in",
    "este utilizată în",
    "este folosit in",
    "este folosita in",
    "este folosită în",
    "is used for",
    "is used to",
    "is utilized for",
    "is utilized to",
    "is applied in",
    "is used in",
    "is implemented in",
}

STRUCTURE_PATTERNS = {
    "este format din",
    "este formata din",
    "este formată din",
    "este alcatuit din",
    "este alcatuita din",
    "este alcătuit din",
    "este alcătuită din",
    "consists of",
    "is composed of",
    "is made up of",
    "is built from",
    "is constructed from",
}

REFERENCE_PATTERNS = {
    "se refera la",
    "se referă la",
    "face referire la",
    "relates to",
    "refers to",
    "corresponds to",
    "is associated with",
    "is connected to",
}

PROCESS_PATTERNS = {
    "consta in",
    "constă în",
    "is based on",
    "is derived from",
    "involves",
    "includes",
}


# cuvinte foarte generale care nu ar trebui sa devina concepte de quiz
BAD_CONCEPTS = {
    "acesta", "aceasta", "acest", "aceeasi", "aceeași", "ele", "ei", "ea", "el",
    "care", "unde", "cand", "când", "daca", "dacă", "nu", "sau", "său", "sau",
    "engl", "english", "definition", "definitions", "definitie", "definitii", "definiții",
    "figura", "tabel", "exemplu", "observatie", "observație", "premise", "notatii", "notații",
}


# expresii care indica, de obicei, zgomot extras din PDF-uri, cod, formule sau bibliografie
NOISE_MARKERS = [
    "isbn",
    "copyright",
    "all rights reserved",
    "academic press",
    "addison wesley",
    "edition",
    "vol.",
    "http://",
    "https://",
]


# expresii care sunt zgomot doar daca apar la inceputul fragmentului
# nu le cautam oriunde, deoarece termeni legitimi pot contine cuvinte ca "figure" sau "table"
NOISE_STARTS = (
    "pagina ",
    "page ",
    "figura ",
    "figure ",
    "tabelul ",
    "table ",
    "algoritm ",
    "algorithm ",
    "pseudocod ",
    "pseudocode ",
    "exemplu de calcul",
)


# normalizeaza spatiile dintr-un text
# aceasta functie este folosita des, pentru a pastra aceeasi forma in intrebari si optiuni
def normalize_spaces(text):
    text = str(text or "")
    return re.sub(r"\s+", " ", text).strip()


# normalizeaza conceptul inainte de a fi folosit intr-o intrebare
# spre deosebire de varianta veche, nu transformam totul in lowercase,
# deoarece acronimele si termenii tehnici trebuie pastrati: API, HTTP, PRAM, H.264 etc.
def normalize_concept_for_question(concept):
    concept = normalize_spaces(concept)

    if not concept:
        return ""

    concept = re.sub(r"^[\-\•\*\–\—\s]+", "", concept)
    concept = re.sub(r"^\d+(\.\d+)*\.?\s*", "", concept)
    concept = normalize_spaces(concept)

    # eliminam articolele doar daca au ramas accidental in concept
    # extractorul NLP le elimina de obicei, dar pastram verificarea ca siguranta
    removable_prefixes = ["un ", "o ", "a ", "an ", "the "]
    lower = concept.lower()

    for prefix in removable_prefixes:
        if lower.startswith(prefix) and len(concept.split()) > 1:
            concept = concept[len(prefix):].strip()
            break

    return normalize_spaces(concept)


# curata definitia pentru afisare in optiuni
# nu schimbam sensul definitiei, doar eliminam punctuatie si spatii inutile de la capete
def normalize_definition_for_option(definition):
    definition = normalize_spaces(definition)
    definition = definition.strip(" .;:-")
    definition = normalize_spaces(definition)
    return definition


# intoarce o forma canonica, utila pentru comparatii si deduplicare
def canonical_text(text):
    text = normalize_spaces(text).lower()
    text = re.sub(r"[\"'“”„.,;:!?()\[\]{}]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# calculeaza o similaritate simpla intre doua texte, fara dependinte externe
# este folosita pentru a evita distractori aproape identici cu raspunsul corect
def token_similarity(text_a, text_b):
    tokens_a = set(re.findall(r"[a-zA-ZăâîșțĂÂÎȘȚ0-9]+", canonical_text(text_a)))
    tokens_b = set(re.findall(r"[a-zA-ZăâîșțĂÂÎȘȚ0-9]+", canonical_text(text_b)))

    if not tokens_a or not tokens_b:
        return 0

    return len(tokens_a & tokens_b) / max(len(tokens_a | tokens_b), 1)


# verifica daca textul pare formula, cod, pseudocod sau linie de tabel
# regula este generala, nu dependenta de un anumit curs/document
def looks_like_noise(text):
    text = normalize_spaces(text)
    lower = text.lower()

    if not text:
        return True

    if any(marker in lower for marker in NOISE_MARKERS):
        return True

    if lower.startswith(NOISE_STARTS):
        return True

    # detectie generala pentru fragmente de pseudocod
    if re.search(r"^(for|while|if|else|return)\b", lower):
        return True

    if re.search(r"\bthen\b", lower) and re.search(r"\b(if|else)\b", lower):
        return True

    digit_ratio = sum(char.isdigit() for char in text) / max(len(text), 1)
    if digit_ratio > 0.28:
        return True

    math_symbols = ["=", "+", "*", "/", "Δ", "∑", "θ", "∂", "←", "→", "≤", "≥", "⊕"]
    math_count = sum(text.count(symbol) for symbol in math_symbols)
    if math_count >= 4:
        return True

    # expresii de forma x = y sau A[i] <- ceva apar frecvent in formule/pseudocod
    if re.search(r"\b[a-zA-Z][a-zA-Z0-9_\[\]]*\s*(=|<-|←)\s*", text):
        return True

    # linii cu multe separatoare sunt adesea tabele sau formule rupte din PDF
    separator_count = sum(text.count(symbol) for symbol in ["|", "\\", ";", "&&"])
    if separator_count >= 3:
        return True

    return False


# verifica daca un concept extras este potrivit pentru o intrebare
# aici filtram general concepte prea scurte, prea lungi sau prea vagi
def is_valid_concept_for_quiz(concept):
    concept = normalize_concept_for_question(concept)
    concept_lower = canonical_text(concept)
    words = concept.split()

    if not concept:
        return False

    if concept_lower in BAD_CONCEPTS:
        return False

    if len(words) > 8:
        return False

    # conceptele formate dintr-un singur caracter sunt aproape intotdeauna zgomot
    if len(words) == 1 and len(concept) < 2:
        return False

    # conceptele foarte lungi cu multe simboluri sunt, de obicei, bucati de formula
    allowed_symbols = set("-/._+ #")
    symbol_count = sum(1 for char in concept if not char.isalnum() and char not in "ăâîșțĂÂÎȘȚ" and char not in allowed_symbols)
    if symbol_count > 2:
        return False

    if looks_like_noise(concept):
        return False

    return True


# verifica daca o definitie este suficient de buna pentru generarea unei intrebari
# scopul este sa nu trimitem mai departe formule, heading-uri sau explicatii rupte din context
def is_good_quiz_item(item):
    concept = normalize_concept_for_question(item.get("concept", ""))
    definition = normalize_definition_for_option(item.get("definition", ""))

    if not concept or not definition:
        return False

    if not is_valid_concept_for_quiz(concept):
        return False

    definition_words = definition.split()

    if len(definition_words) < 3:
        return False

    if len(definition_words) > 45:
        return False

    if looks_like_noise(definition):
        return False

    lower_definition = definition.lower()
    bad_starts = (
        "si ", "și ", "iar ", "dar ", "and ", "or ",
        "pasul ", "step ", "exemplu ", "example ",
    )

    if lower_definition.startswith(bad_starts):
        return False

    return True


# detecteaza intentia principala a unei definitii
# intentia este folosita pentru a formula intrebari mai naturale
def detect_intent(item):
    definition = normalize_spaces(item.get("definition", "")).lower()
    pattern = normalize_spaces(item.get("pattern", "")).lower()

    if pattern in ROLE_PATTERNS:
        return "role"

    if pattern in USAGE_PATTERNS:
        return "usage"

    if pattern in STRUCTURE_PATTERNS:
        return "structure"

    if pattern in REFERENCE_PATTERNS:
        return "reference"

    if pattern in PROCESS_PATTERNS:
        return "process"

    # fallback pe continutul definitiei, pentru cazurile in care pattern-ul lipseste sau e generic
    if any(value in definition for value in ["rolul", "scopul", "role", "purpose"]):
        return "role"

    if any(value in definition for value in ["folosit", "utilizat", "utilizata", "utilizată", "used", "utilized"]):
        return "usage"

    if any(value in definition for value in ["format din", "alcatuit din", "alcătuit din", "consists of", "composed of", "made up of"]):
        return "structure"

    if any(value in definition for value in ["se refera", "se referă", "refers to", "relates to"]):
        return "reference"

    if any(value in definition for value in ["proces", "succesiune", "based on", "involves"]):
        return "process"

    return "definition"


# calculeaza un scor de calitate pentru un item de quiz
# scorul este folosit la ordonare si la alegerea celor mai bune concepte pentru intrebari
def score_quiz_item(item):
    concept = normalize_concept_for_question(item.get("concept", ""))
    definition = normalize_definition_for_option(item.get("definition", ""))
    pattern = normalize_spaces(item.get("pattern", "")).lower()

    score = 0
    concept_words = concept.split()
    definition_words = definition.split()

    if 1 <= len(concept_words) <= 5:
        score += 4
    elif 6 <= len(concept_words) <= 8:
        score += 1
    else:
        score -= 3

    if 5 <= len(definition_words) <= 26:
        score += 5
    elif 27 <= len(definition_words) <= 38:
        score += 2
    else:
        score -= 2

    if pattern in STRONG_DEFINITION_PATTERNS:
        score += 3

    if pattern in ROLE_PATTERNS or pattern in USAGE_PATTERNS or pattern in STRUCTURE_PATTERNS:
        score += 2

    # acronimele si termenii tehnici scurti sunt adesea concepte bune
    if re.fullmatch(r"[A-ZĂÂÎȘȚ0-9][A-ZĂÂÎȘȚ0-9.\-/+]{1,12}", concept):
        score += 2

    if looks_like_noise(definition) or looks_like_noise(concept):
        score -= 8

    return score


# elimina duplicatele si pastreaza cea mai buna definitie pentru fiecare concept + limba
# astfel evitam quiz-uri cu aceeasi intrebare formulata de mai multe ori
def prepare_quiz_items(definitions):
    best_items = {}

    for item in definitions:
        if not is_good_quiz_item(item):
            continue

        concept = normalize_concept_for_question(item.get("concept", ""))
        definition = normalize_definition_for_option(item.get("definition", ""))
        language = item.get("language", "ro") or "ro"

        clean_item = dict(item)
        clean_item["concept"] = concept
        clean_item["definition"] = definition
        clean_item["language"] = "ro" if language == "ro" else "en"
        clean_item["intent"] = detect_intent(clean_item)
        clean_item["quiz_score"] = score_quiz_item(clean_item)

        key = (canonical_text(concept), clean_item["language"])
        existing = best_items.get(key)

        if not existing or clean_item["quiz_score"] > existing["quiz_score"]:
            best_items[key] = clean_item

    items = list(best_items.values())
    items = sorted(items, key=lambda value: value.get("quiz_score", 0), reverse=True)
    return items


# genereaza mai multe formulari posibile pentru aceeasi intrebare
# folosim ghilimele in jurul conceptului pentru a evita problemele de gen/articol in romana
def generate_question_variants(concept, intent, lang):
    concept = normalize_concept_for_question(concept)

    if lang == "ro":
        strategies = {
            "definition": [
                f"Ce este \"{concept}\"?",
                f"Cum poate fi definit conceptul \"{concept}\"?",
                f"Ce reprezinta \"{concept}\"?",
            ],
            "role": [
                f"Care este rolul conceptului \"{concept}\"?",
                f"Ce rol are \"{concept}\"?",
            ],
            "usage": [
                f"Pentru ce este utilizat conceptul \"{concept}\"?",
                f"La ce este folosit \"{concept}\"?",
            ],
            "structure": [
                f"Din ce este alcatuit conceptul \"{concept}\"?",
                f"Ce componente are \"{concept}\"?",
            ],
            "process": [
                f"In ce consta \"{concept}\"?",
                f"Ce proces descrie \"{concept}\"?",
            ],
            "reference": [
                f"La ce se refera \"{concept}\"?",
                f"Ce descrie conceptul \"{concept}\"?",
            ],
        }
    else:
        strategies = {
            "definition": [
                f"What is \"{concept}\"?",
                f"How can \"{concept}\" be defined?",
                f"What does \"{concept}\" mean?",
            ],
            "role": [
                f"What is the role of \"{concept}\"?",
                f"What purpose does \"{concept}\" serve?",
            ],
            "usage": [
                f"What is \"{concept}\" used for?",
                f"When is \"{concept}\" used?",
            ],
            "structure": [
                f"What does \"{concept}\" consist of?",
                f"What are the components of \"{concept}\"?",
            ],
            "process": [
                f"How does \"{concept}\" work?",
                f"What process is associated with \"{concept}\"?",
            ],
            "reference": [
                f"What does \"{concept}\" refer to?",
                f"What is \"{concept}\" related to?",
            ],
        }

    return strategies.get(intent, strategies["definition"])


# calculeaza un scor simplu pentru a alege formularea cea mai naturala
def score_question(question):
    score = 0
    question_lower = question.lower()
    word_count = len(question.split())

    if "ce este" in question_lower or "what is" in question_lower:
        score += 2

    if "care este" in question_lower or "what does" in question_lower:
        score += 2

    if 4 <= word_count <= 11:
        score += 2

    if word_count > 14:
        score -= 2

    return score


# alege una dintre cele mai bune variante de intrebare
# pastram un mic element random pentru ca regenerarea sa nu produca mereu aceleasi texte
def select_human_like_question(variants):
    if not variants:
        return ""

    scored = [(question, score_question(question)) for question in variants]
    scored = sorted(scored, key=lambda item: item[1], reverse=True)
    top = [item[0] for item in scored[:2]]
    return random.choice(top)


# construieste un enunt pentru intrebarile true/false
# folosim pattern-ul original atunci cand exista, ca propozitia sa fie mai naturala
def build_true_false_statement(item, chosen_definition):
    concept = normalize_concept_for_question(item.get("concept", ""))
    pattern = normalize_spaces(item.get("pattern", "")).lower()
    lang = item.get("language", "ro")
    definition = normalize_definition_for_option(chosen_definition)

    if lang == "ro":
        if pattern in ROLE_PATTERNS:
            statement = f"{concept} are rolul de {definition}."
        elif pattern in USAGE_PATTERNS:
            statement = f"{concept} este utilizat pentru {definition}."
        elif pattern in STRUCTURE_PATTERNS:
            statement = f"{concept} este alcatuit din {definition}."
        elif pattern in REFERENCE_PATTERNS:
            statement = f"{concept} se refera la {definition}."
        elif pattern in PROCESS_PATTERNS:
            statement = f"{concept} consta in {definition}."
        else:
            statement = f"{concept} este {definition}."

        return f"Afirmatia urmatoare este adevarata sau falsa? {statement}"

    if pattern in ROLE_PATTERNS:
        statement = f"{concept} serves to {definition}."
    elif pattern in USAGE_PATTERNS:
        statement = f"{concept} is used for {definition}."
    elif pattern in STRUCTURE_PATTERNS:
        statement = f"{concept} consists of {definition}."
    elif pattern in REFERENCE_PATTERNS:
        statement = f"{concept} refers to {definition}."
    elif pattern in PROCESS_PATTERNS:
        statement = f"{concept} involves {definition}."
    else:
        statement = f"{concept} is {definition}."

    return f"Is the following statement true or false? {statement}"


# verifica daca un distractor este suficient de diferit de raspunsul corect
def is_valid_definition_distractor(correct_definition, candidate_definition):
    correct_definition = normalize_definition_for_option(correct_definition)
    candidate_definition = normalize_definition_for_option(candidate_definition)

    if not candidate_definition:
        return False

    if canonical_text(correct_definition) == canonical_text(candidate_definition):
        return False

    if token_similarity(correct_definition, candidate_definition) > 0.62:
        return False

    if looks_like_noise(candidate_definition):
        return False

    return True


# alege distractori pentru intrebarile cu variante de definitie
# prioritizam aceeasi limba si acelasi tip de intentie, dar evitam definitiile prea similare
def choose_definition_distractors(correct_item, items, max_count=3):
    correct_definition = correct_item.get("definition", "")
    correct_concept = canonical_text(correct_item.get("concept", ""))
    correct_language = correct_item.get("language", "ro")
    correct_intent = correct_item.get("intent", detect_intent(correct_item))

    candidates = []

    for item in items:
        if item is correct_item:
            continue

        if item.get("language") != correct_language:
            continue

        if canonical_text(item.get("concept", "")) == correct_concept:
            continue

        candidate_definition = normalize_definition_for_option(item.get("definition", ""))

        if not is_valid_definition_distractor(correct_definition, candidate_definition):
            continue

        score = 0

        if item.get("intent") == correct_intent:
            score += 4

        length_difference = abs(len(candidate_definition.split()) - len(correct_definition.split()))
        if length_difference <= 6:
            score += 3
        elif length_difference <= 12:
            score += 1

        score += min(item.get("quiz_score", 0), 6)
        score += random.random()

        candidates.append((candidate_definition, score))

    candidates = sorted(candidates, key=lambda value: value[1], reverse=True)

    selected = []
    seen = set()

    for candidate_definition, _score in candidates:
        key = canonical_text(candidate_definition)

        if key in seen:
            continue

        seen.add(key)
        selected.append(candidate_definition)

        if len(selected) >= max_count:
            break

    return selected


# alege distractori pentru intrebarile inverse, unde raspunsul corect este conceptul
# evitam concepte aproape identice si pastram aceeasi limba
def choose_concept_distractors(correct_item, items, max_count=3):
    correct_concept = normalize_concept_for_question(correct_item.get("concept", ""))
    correct_language = correct_item.get("language", "ro")
    correct_intent = correct_item.get("intent", detect_intent(correct_item))

    candidates = []

    for item in items:
        if item is correct_item:
            continue

        if item.get("language") != correct_language:
            continue

        candidate_concept = normalize_concept_for_question(item.get("concept", ""))

        if not candidate_concept:
            continue

        if canonical_text(candidate_concept) == canonical_text(correct_concept):
            continue

        if token_similarity(candidate_concept, correct_concept) > 0.72:
            continue

        score = 0

        if item.get("intent") == correct_intent:
            score += 3

        length_difference = abs(len(candidate_concept.split()) - len(correct_concept.split()))
        if length_difference <= 2:
            score += 2

        score += min(item.get("quiz_score", 0), 5)
        score += random.random()

        candidates.append((candidate_concept, score))

    candidates = sorted(candidates, key=lambda value: value[1], reverse=True)

    selected = []
    seen = set()

    for candidate_concept, _score in candidates:
        key = canonical_text(candidate_concept)

        if key in seen:
            continue

        seen.add(key)
        selected.append(candidate_concept)

        if len(selected) >= max_count:
            break

    return selected


# construieste intrebarea cu variante multiple, unde raspunsul corect este definitia
def build_mcq_question(item, items):
    concept = normalize_concept_for_question(item.get("concept", ""))
    definition = normalize_definition_for_option(item.get("definition", ""))
    lang = item.get("language", "ro")
    intent = item.get("intent", detect_intent(item))

    distractors = choose_definition_distractors(item, items, max_count=3)

    if len(distractors) < 3:
        return None

    options = [definition] + distractors[:3]
    options = list(dict.fromkeys(options))

    if len(options) < 4:
        return None

    random.shuffle(options)
    variants = generate_question_variants(concept, intent, lang)
    question_text = select_human_like_question(variants)

    return {
        "type": "mcq",
        "language": lang,
        "question": question_text,
        "options": options,
        "correct_answer": definition,
        "source_concept": concept,
        "source_definition": definition,
    }


# construieste intrebarea inversa, unde utilizatorul primeste definitia si alege conceptul
def build_reverse_question(item, items):
    concept = normalize_concept_for_question(item.get("concept", ""))
    definition = normalize_definition_for_option(item.get("definition", ""))
    lang = item.get("language", "ro")

    distractors = choose_concept_distractors(item, items, max_count=3)

    if len(distractors) < 3:
        return None

    options = [concept] + distractors[:3]
    options = list(dict.fromkeys(options))

    if len(options) < 4:
        return None

    random.shuffle(options)

    if lang == "ro":
        question_text = f"Ce concept se potriveste definitiei: {definition}?"
    else:
        question_text = f"Which concept matches the definition: {definition}?"

    return {
        "type": "mcq_reverse",
        "language": lang,
        "question": question_text,
        "options": options,
        "correct_answer": concept,
        "source_concept": concept,
        "source_definition": definition,
    }


# construieste o intrebare adevarat/fals
# pentru varianta falsa luam definitia altui concept din aceeasi limba
def build_true_false_question(item, items):
    definition = normalize_definition_for_option(item.get("definition", ""))
    lang = item.get("language", "ro")
    distractors = choose_definition_distractors(item, items, max_count=1)

    if not distractors:
        return None

    is_true = random.choice([True, False])
    chosen_definition = definition if is_true else distractors[0]
    statement = build_true_false_statement(item, chosen_definition)

    return {
        "type": "true_false",
        "language": lang,
        "question": statement,
        "correct_answer": is_true,
        "source_concept": normalize_concept_for_question(item.get("concept", "")),
        "source_definition": definition,
    }


# alege tipurile de intrebari in functie de dificultate
# ordinea nu este fixa, ca sa obtinem quiz-uri mai variate la regenerare
def get_question_type_order(difficulty):
    difficulty = (difficulty or "medium").lower()

    if difficulty == "easy":
        order = ["true_false", "mcq", "mcq_reverse"]
    elif difficulty == "hard":
        order = ["mcq_reverse", "mcq", "true_false"]
    else:
        order = ["mcq", "mcq_reverse", "true_false"]

    # schimbam usor ordinea, dar pastram prioritatea primei categorii
    first = order[0]
    rest = order[1:]
    random.shuffle(rest)
    return [first] + rest


# construieste o intrebare pentru un item, incercand mai multe tipuri daca primul nu are distractori suficienti
def build_question_for_item(item, items, difficulty):
    builders = {
        "mcq": build_mcq_question,
        "mcq_reverse": build_reverse_question,
        "true_false": build_true_false_question,
    }

    for question_type in get_question_type_order(difficulty):
        question = builders[question_type](item, items)

        if question:
            return question

    return None


# ordoneaza itemii astfel incat sa nu favorizam artificial o limba
# daca documentul contine doar romana sau doar engleza, toate intrebarile vin din limba disponibila
# daca documentul este mixt, alegerea este proportionala cu numarul de definitii bune gasite
def build_balanced_item_order(items):
    grouped = {}

    for item in items:
        lang = item.get("language", "ro")
        grouped.setdefault(lang, []).append(item)

    for lang in grouped:
        random.shuffle(grouped[lang])
        grouped[lang] = sorted(grouped[lang], key=lambda value: value.get("quiz_score", 0), reverse=True)

    ordered = []

    # interclasare simpla intre limbi; functioneaza si daca exista doar o limba
    while any(grouped.values()):
        active_languages = sorted(grouped.keys(), key=lambda key: len(grouped[key]), reverse=True)

        for lang in active_languages:
            if grouped[lang]:
                ordered.append(grouped[lang].pop(0))

    return ordered


# genereaza intrebarile pentru o singura limba
# functia ramane disponibila pentru compatibilitate cu eventuale apeluri existente
def generate_questions_for_language(items, language, difficulty="medium", max_questions=10):
    language_items = []

    for item in items:
        if item.get("language") == language:
            language_items.append(item)

    valid_items = prepare_quiz_items(language_items)

    if len(valid_items) < 2:
        return []

    questions = []
    used_sources = set()
    used_question_texts = set()

    for item in build_balanced_item_order(valid_items):
        source_key = (
            canonical_text(item.get("concept", "")),
            canonical_text(item.get("definition", "")),
            item.get("language", language),
        )

        if source_key in used_sources:
            continue

        question = build_question_for_item(item, valid_items, difficulty)

        if not question:
            continue

        question_key = canonical_text(question.get("question", ""))
        if question_key in used_question_texts:
            continue

        used_sources.add(source_key)
        used_question_texts.add(question_key)
        questions.append(question)

        if len(questions) >= max_questions:
            break

    return questions


# genereaza intrebarile finale pe baza definitiilor NLP
# nu mai impartim artificial numarul maxim 50/50 intre romana si engleza
# numarul de intrebari pe limba este determinat de definitiile valide disponibile
def generate_questions(definitions, difficulty="medium", max_questions=10):
    try:
        max_questions = int(max_questions)
    except Exception:
        max_questions = 10

    if max_questions <= 0:
        return []

    valid_items = prepare_quiz_items(definitions)

    if len(valid_items) < 2:
        return []

    questions = []
    used_sources = set()
    used_question_texts = set()
    ordered_items = build_balanced_item_order(valid_items)

    # prima trecere: generam intrebari din cele mai bune definitii
    for item in ordered_items:
        source_key = (
            canonical_text(item.get("concept", "")),
            canonical_text(item.get("definition", "")),
            item.get("language", "ro"),
        )

        if source_key in used_sources:
            continue

        question = build_question_for_item(item, valid_items, difficulty)

        if not question:
            continue

        question_key = canonical_text(question.get("question", ""))
        if question_key in used_question_texts:
            continue

        used_sources.add(source_key)
        used_question_texts.add(question_key)
        questions.append(question)

        if len(questions) >= max_questions:
            break

    # a doua trecere: daca nu am ajuns la max_questions, incercam din nou cu dificultate medie
    # acest fallback ajuta documentele in care unele concepte nu au suficienti distractori pentru modul hard/easy
    if len(questions) < max_questions and difficulty != "medium":
        for item in ordered_items:
            source_key = (
                canonical_text(item.get("concept", "")),
                canonical_text(item.get("definition", "")),
                item.get("language", "ro"),
            )

            if source_key in used_sources:
                continue

            question = build_question_for_item(item, valid_items, "medium")

            if not question:
                continue

            question_key = canonical_text(question.get("question", ""))
            if question_key in used_question_texts:
                continue

            used_sources.add(source_key)
            used_question_texts.add(question_key)
            questions.append(question)

            if len(questions) >= max_questions:
                break

    random.shuffle(questions)
    return questions[:max_questions]
