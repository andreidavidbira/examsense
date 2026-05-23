import random


from nlp.patterns import (
    ROMANIAN_PATTERN_DEFINITION,
    ROMANIAN_PATTERN_REFERENCE,
    ROMANIAN_PATTERN_DESCRIPTION,
    ROMANIAN_PATTERN_STRUCTURE,
    ROMANIAN_PATTERN_PROCESS,
    ROMANIAN_PATTERN_USAGE,
    ROMANIAN_PATTERN_CONTEXT,
    ROMANIAN_PATTERN_SPECIAL,

    ENGLISH_PATTERN_DEFINITION,
    ENGLISH_PATTERN_REFERENCE,
    ENGLISH_PATTERN_DESCRIPTION,
    ENGLISH_PATTERN_STRUCTURE,
    ENGLISH_PATTERN_PROCESS,
    ENGLISH_PATTERN_USAGE,
    ENGLISH_PATTERN_CONTEXT,
    ENGLISH_PATTERN_CLASSIFICATION
)


# ================= NORMALIZARE CONCEPT =================

def normalize_concept_for_question(concept):
    concept = concept.lower().strip()

    # eliminare articulatii simple (romana)
    endings = ["ul", "ului", "le", "lor", "a", "ele"]

    for end in endings:
        if concept.endswith(end) and len(concept) > len(end) + 2:
            concept = concept[:-len(end)]
            break

    return concept.strip()


# ================= GENERARE INTREBARE =================

def generate_question_by_pattern(concept, pattern, lang):
    concept_clean = normalize_concept_for_question(concept)

    if lang == "ro":

        if pattern in ROMANIAN_PATTERN_DEFINITION:
            return f"Ce este {concept_clean}?"

        elif pattern in ROMANIAN_PATTERN_REFERENCE:
            return f"La ce se refera {concept_clean}?"

        elif pattern in ROMANIAN_PATTERN_DESCRIPTION:
            return f"Cum este descris {concept_clean}?"

        elif pattern in ROMANIAN_PATTERN_STRUCTURE:
            return f"Din ce este format {concept_clean}?"

        elif pattern in ROMANIAN_PATTERN_PROCESS:
            return f"In ce consta {concept_clean}?"

        elif pattern in ROMANIAN_PATTERN_USAGE:
            return f"Care este rolul lui {concept_clean}?"

        elif pattern in ROMANIAN_PATTERN_CONTEXT:
            return f"Unde este utilizat {concept_clean}?"

        elif pattern in ROMANIAN_PATTERN_SPECIAL:
            return f"Ce reprezinta {concept_clean}?"

        else:
            return f"Ce este {concept_clean}?"

    else:

        if pattern in ENGLISH_PATTERN_DEFINITION or pattern in ENGLISH_PATTERN_CLASSIFICATION:
            return f"What is {concept_clean}?"

        elif pattern in ENGLISH_PATTERN_REFERENCE:
            return f"What does {concept_clean} refer to?"

        elif pattern in ENGLISH_PATTERN_DESCRIPTION:
            return f"How is {concept_clean} described?"

        elif pattern in ENGLISH_PATTERN_STRUCTURE:
            return f"What does {concept_clean} consist of?"

        elif pattern in ENGLISH_PATTERN_PROCESS:
            return f"What is {concept_clean} based on?"

        elif pattern in ENGLISH_PATTERN_USAGE:
            return f"What is {concept_clean} used for?"

        elif pattern in ENGLISH_PATTERN_CONTEXT:
            return f"In what context is {concept_clean} used?"

        else:
            return f"What is {concept_clean}?"


# ================= GENERARE QUIZ =================

def generate_questions(definitions, difficulty="easy", max_questions=10):
    questions = []

    if len(definitions) < 2:
        return []

    used_questions = set()

    for item in definitions:
        concept = item["concept"]
        correct_def = item["definition"]
        pattern = item.get("pattern", "")
        lang = item.get("language", "ro")

        concept_clean = normalize_concept_for_question(concept)

        # filtrare concept slab
        if not concept_clean or len(concept_clean) < 3:
            continue

        # definiri alternative (pentru distractori)
        other_defs = [
            d["definition"] for d in definitions
            if d["definition"] != correct_def and len(d["definition"].split()) > 3
        ]

        if not other_defs:
            continue

        question_text = generate_question_by_pattern(concept, pattern, lang)

        # evita duplicate
        if question_text in used_questions:
            continue

        used_questions.add(question_text)

        # ================= EASY =================
        if difficulty == "easy":

            false_def = random.choice(other_defs)
            is_true = random.choice([True, False])

            if lang == "ro":
                sentence = f"{concept_clean} este {correct_def if is_true else false_def}."
            else:
                sentence = f"{concept_clean} is {correct_def if is_true else false_def}."

            questions.append({
                "type": "true_false",
                "question": sentence,
                "correct_answer": is_true
            })

        # ================= HARD =================
        else:
            distractors = random.sample(other_defs, min(3, len(other_defs)))

            options = [correct_def] + distractors
            random.shuffle(options)

            questions.append({
                "type": "mcq",
                "question": question_text,
                "options": options,
                "correct_answer": correct_def
            })

        # limitare
        if len(questions) >= max_questions:
            break

    return questions