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


def generate_question_by_pattern(concept, pattern, lang):

    if lang == "ro":

        if pattern in ROMANIAN_PATTERN_DEFINITION:
            return f"Ce este {concept}?"

        elif pattern in ROMANIAN_PATTERN_REFERENCE:
            return f"La ce se refera {concept}?"

        elif pattern in ROMANIAN_PATTERN_DESCRIPTION:
            return f"Cum poate fi descris {concept}?"

        elif pattern in ROMANIAN_PATTERN_STRUCTURE:
            return f"Din ce este format {concept}?"

        elif pattern in ROMANIAN_PATTERN_PROCESS:
            return f"In ce consta {concept}?"

        elif pattern in ROMANIAN_PATTERN_USAGE:
            return f"La ce este folosit {concept}?"

        elif pattern in ROMANIAN_PATTERN_CONTEXT:
            return f"In ce context este utilizat {concept}?"

        elif pattern in ROMANIAN_PATTERN_SPECIAL:
            return f"Ce reprezinta {concept}?"

        else:
            return f"Ce este {concept}?"

    else:

        if pattern in ENGLISH_PATTERN_DEFINITION or pattern in ENGLISH_PATTERN_CLASSIFICATION:
            return f"What is {concept}?"

        elif pattern in ENGLISH_PATTERN_REFERENCE:
            return f"What does {concept} refer to?"

        elif pattern in ENGLISH_PATTERN_DESCRIPTION:
            return f"How can {concept} be described?"

        elif pattern in ENGLISH_PATTERN_STRUCTURE:
            return f"What does {concept} consist of?"

        elif pattern in ENGLISH_PATTERN_PROCESS:
            return f"What is {concept} based on?"

        elif pattern in ENGLISH_PATTERN_USAGE:
            return f"What is {concept} used for?"

        elif pattern in ENGLISH_PATTERN_CONTEXT:
            return f"In what context is {concept} used?"

        else:
            return f"What is {concept}?"


def generate_questions(definitions, difficulty="easy"):
    questions = []

    if len(definitions) < 2:
        return []

    for item in definitions:
        concept = item["concept"]
        correct_def = item["definition"]
        pattern = item.get("pattern", "")
        lang = item.get("language", "ro")

        other_defs = [
            d["definition"] for d in definitions
            if d["definition"] != correct_def
        ]

        if not other_defs:
            continue

        question_text = generate_question_by_pattern(concept, pattern, lang)

        if difficulty == "easy":
            false_def = random.choice(other_defs)
            is_true = random.choice([True, False])

            if lang == "ro":
                sentence = f"{concept} este {correct_def if is_true else false_def}."
            else:
                sentence = f"{concept} is {correct_def if is_true else false_def}."

            questions.append({
                "type": "true_false",
                "question": sentence,
                "correct_answer": is_true
            })

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

    return questions