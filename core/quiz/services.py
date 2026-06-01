import random


def normalize_concept_for_question(concept):
    return concept.lower().strip()


def is_good_quiz_item(item):
    concept = item.get("concept", "").strip().lower()
    definition = item.get("definition", "").strip()

    if not concept or not definition:
        return False

    if len(concept.split()) > 4:
        return False

    if len(definition.split()) < 3:
        return False

    if len(definition.split()) > 35:
        return False

    if any(char in concept for char in [")", "(", "\"", "“", "”"]):
        return False

    if concept in {"engl", "său", "sau"}:
        return False

    return True


def is_probably_feminine_ro(concept):
    feminine_endings = (
        "are",
        "ere",
        "ire",
        "ție",
        "tie",
        "ziune",
        "siune",
        "ime",
        "ate",
        "tate",
        "itate",
        "ență",
        "enta",
        "structură",
        "climă",
        "încapsulare",
        "mostenire",
        "moștenire",
        "latitudine",
        "longitudine",
        "temă",
        "tema",
        "densitate",
    )

    concept = concept.strip().lower()

    if concept in {
        "structură de date",
        "clima",
        "încapsularea",
        "moștenirea",
        "latitudinea",
        "longitudinea",
        "tema literară",
        "densitatea",
        "listă înlănțuită",
        "harta topografică",
    }:
        return True

    return concept.endswith(feminine_endings)


def ro_defined_phrase(concept):
    if is_probably_feminine_ro(concept):
        return f"Cum poate fi definită {concept}?"
    return f"Cum poate fi definit {concept}?"


def detect_intent(item):
    definition = item.get("definition", "").lower()
    pattern = item.get("pattern", "").lower()
    lang = item.get("language", "ro")

    if lang == "ro":
        if pattern in ["are rolul de"]:
            return "role"

        if pattern in [
            "este utilizat pentru",
            "este utilizată pentru",
            "este utilizata pentru",
            "este folosit pentru",
            "este folosită pentru",
            "este folosita pentru",
            "servește la",
            "serveste la",
        ]:
            return "usage"

        if pattern in [
            "este format din",
            "este formată din",
            "este formata din",
            "este alcătuit din",
            "este alcătuită din",
            "este alcatuit din",
            "este alcatuita din",
        ]:
            return "structure"

        if pattern in ["constă în", "consta in"]:
            return "process"

        if pattern in ["se referă la", "se refera la", "face referire la"]:
            return "reference"

        if pattern in [
            "reprezintă",
            "reprezinta",
            "este",
            "este definit ca",
            "este definită ca",
            "este definita ca",
            "înseamnă",
            "inseamna",
            "poate fi definit ca",
            "poate fi definita ca",
            "poate fi definită ca",
        ]:
            if definition.startswith("folosit ") or definition.startswith("utilizat "):
                return "usage"

            if definition.startswith("procesul "):
                return "process"

            return "definition"

        if "rol" in definition:
            return "role"

        if "folosit" in definition or "utilizat" in definition:
            return "usage"

        if "format din" in definition or "alcătuit din" in definition or "alcatuit din" in definition:
            return "structure"

        if "se referă la" in definition or "se refera la" in definition:
            return "reference"

        if "constă în" in definition or "consta in" in definition:
            return "process"

        return "definition"

    if pattern in ["serves as", "serves to"]:
        return "role"

    if pattern in [
        "is used for",
        "is used to",
        "is utilized for",
        "is utilized to",
        "is applied in",
        "is used in",
        "is implemented in",
    ]:
        return "usage"

    if pattern in [
        "consists of",
        "is composed of",
        "is made up of",
        "is built from",
        "is constructed from",
    ]:
        return "structure"

    if pattern in [
        "refers to",
        "relates to",
        "corresponds to",
        "is associated with",
        "is connected to",
    ]:
        return "reference"

    if pattern in [
        "is based on",
        "is derived from",
        "involves",
        "includes",
    ]:
        return "process"

    if pattern in [
        "is",
        "means",
        "represents",
        "is defined as",
        "can be defined as",
        "is described as",
        "can be described as",
        "defines",
        "describes",
        "characterizes",
    ]:
        if definition.startswith("to "):
            return "role"
        return "definition"

    if "role" in definition:
        return "role"

    if "used" in definition or "utilized" in definition:
        return "usage"

    if "consists" in definition or "composed of" in definition:
        return "structure"

    if "refers to" in definition or "relates to" in definition:
        return "reference"

    if "based on" in definition or "involves" in definition:
        return "process"

    return "definition"


def generate_question_variants(concept, intent, lang, item=None):
    current_concept = concept
    pattern = ""

    if item:
        pattern = item.get("pattern", "").lower()

    if lang == "ro":
        if intent == "definition":
            if pattern in ["reprezintă", "reprezinta"]:
                return [
                    f"Ce reprezinta {current_concept}?",
                    f"Ce este {current_concept}?",
                ]

            if pattern in [
                "este definit ca",
                "este definită ca",
                "este definita ca",
                "poate fi definit ca",
                "poate fi definita ca",
                "poate fi definită ca",
            ]:
                return [
                    ro_defined_phrase(current_concept),
                    f"Ce este {current_concept}?",
                ]

            return [
                f"Ce este {current_concept}?",
                f"Ce reprezinta {current_concept}?",
                ro_defined_phrase(current_concept),
            ]

        strategies = {
            "role": [
                f"Care este rolul {current_concept}?",
                f"Ce rol are {current_concept}?",
            ],
            "usage": [
                f"La ce este folosit {current_concept}?",
                f"Pentru ce se utilizeaza {current_concept}?",
            ],
            "structure": [
                f"Din ce este format {current_concept}?",
                f"Ce componente are {current_concept}?",
            ],
            "process": [
                f"In ce consta {current_concept}?",
                f"Cum functioneaza {current_concept}?",
            ],
            "reference": [
                f"La ce se refera {current_concept}?",
                f"Ce descrie {current_concept}?",
            ],
        }

        return strategies.get(intent, [f"Ce este {current_concept}?"])

    if intent == "definition":
        return [
            f"What is {current_concept}?",
            f"How can {current_concept} be defined?",
        ]

    strategies = {
        "role": [
            f"What is the role of {current_concept}?",
            f"What is {current_concept} used for?",
        ],
        "usage": [
            f"What is {current_concept} used for?",
            f"When is {current_concept} used?",
        ],
        "structure": [
            f"What does {current_concept} consist of?",
            f"What are the components of {current_concept}?",
        ],
        "process": [
            f"How does {current_concept} work?",
            f"What is the process behind {current_concept}?",
        ],
        "reference": [
            f"What does {current_concept} refer to?",
        ],
    }

    return strategies.get(intent, [f"What is {current_concept}?"])


def score_question(question):
    score = 0
    question_lower = question.lower()

    if "care este" in question_lower or "what is" in question_lower:
        score += 2

    if "cum" in question_lower or "how" in question_lower:
        score += 1

    if 4 <= len(question.split()) <= 10:
        score += 2

    if len(question.split()) > 12:
        score -= 2

    return score


def select_human_like_question(variants):
    scored = [(question, score_question(question)) for question in variants]
    scored = sorted(scored, key=lambda item: item[1], reverse=True)
    top = [item[0] for item in scored[:2]] if len(scored) >= 2 else [scored[0][0]]
    return random.choice(top)


def choose_distractors(correct_def, items, max_count=3):
    candidates = []

    for item in items:
        definition = item["definition"]

        if definition == correct_def:
            continue

        if 3 <= len(definition.split()) <= 30:
            candidates.append(definition)

    candidates = list(dict.fromkeys(candidates))

    if len(candidates) <= max_count:
        return candidates

    return random.sample(candidates, max_count)


def generate_questions_for_language(items, language, difficulty="medium", max_questions=10):
    questions = []

    valid_items = [item for item in items if is_good_quiz_item(item)]

    if len(valid_items) < 2:
        return []

    random.shuffle(valid_items)

    used_questions = set()

    for item in valid_items:
        concept = item["concept"]
        correct_def = item["definition"]

        concept_clean = normalize_concept_for_question(concept)

        if not concept_clean:
            continue

        intent = detect_intent(item)
        variants = generate_question_variants(concept_clean, intent, language, item=item)
        question_text = select_human_like_question(variants)

        if question_text in used_questions:
            continue

        used_questions.add(question_text)

        distractors = choose_distractors(correct_def, valid_items, max_count=3)
        can_make_mcq = len(distractors) >= 3

        if difficulty == "easy" or not can_make_mcq:
            if not distractors:
                continue

            false_def = random.choice(distractors)
            is_true = random.choice([True, False])
            chosen_def = correct_def if is_true else false_def

            if language == "ro":
                sentence = f"{concept_clean} reprezinta {chosen_def}."
            else:
                sentence = f"{concept_clean} represents {chosen_def}."

            questions.append({
                "type": "true_false",
                "language": language,
                "question": sentence,
                "correct_answer": is_true,
            })

        elif difficulty == "hard":
            concept_options = [
                normalize_concept_for_question(other_item["concept"])
                for other_item in valid_items
                if other_item["concept"] != concept
            ]

            concept_options = list(dict.fromkeys(concept_options))

            if len(concept_options) < 3:
                options = [correct_def] + distractors[:3]
                random.shuffle(options)

                questions.append({
                    "type": "mcq",
                    "language": language,
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_def,
                })
            else:
                distractor_concepts = random.sample(concept_options, 3)
                options = [concept_clean] + distractor_concepts
                random.shuffle(options)

                if language == "ro":
                    reverse_question = f"Ce concept se potriveste definitiei: {correct_def}?"
                else:
                    reverse_question = f"Which concept matches the definition: {correct_def}?"

                questions.append({
                    "type": "mcq_reverse",
                    "language": language,
                    "question": reverse_question,
                    "options": options,
                    "correct_answer": concept_clean,
                })

        else:
            options = [correct_def] + distractors[:3]
            options = list(dict.fromkeys(options))

            if len(options) < 4:
                false_def = random.choice(distractors)
                is_true = random.choice([True, False])
                chosen_def = correct_def if is_true else false_def

                if language == "ro":
                    sentence = f"{concept_clean} reprezinta {chosen_def}."
                else:
                    sentence = f"{concept_clean} represents {chosen_def}."

                questions.append({
                    "type": "true_false",
                    "language": language,
                    "question": sentence,
                    "correct_answer": is_true,
                })
            else:
                random.shuffle(options)

                questions.append({
                    "type": "mcq",
                    "language": language,
                    "question": question_text,
                    "options": options,
                    "correct_answer": correct_def,
                })

        if len(questions) >= max_questions:
            break

    return questions


def generate_questions(definitions, difficulty="medium", max_questions=10):
    definitions_ro = [item for item in definitions if item.get("language") == "ro"]
    definitions_en = [item for item in definitions if item.get("language") == "en"]

    max_ro = max_questions // 2
    max_en = max_questions - max_ro

    questions_ro = generate_questions_for_language(
        definitions_ro,
        language="ro",
        difficulty=difficulty,
        max_questions=max_ro,
    )

    questions_en = generate_questions_for_language(
        definitions_en,
        language="en",
        difficulty=difficulty,
        max_questions=max_en,
    )

    questions = questions_ro + questions_en
    random.shuffle(questions)

    if len(questions) > max_questions:
        questions = questions[:max_questions]

    return questions