import random


def generate_questions(definitions, difficulty="easy"):
    questions = []

    if len(definitions) < 2:
        return []

    for item in definitions:
        concept = item["concept"]
        correct_def = item["definition"]

        # EASY → TRUE/FALSE
        if difficulty == "easy":
            other = random.choice(definitions)["definition"]

            is_true = random.choice([True, False])

            if is_true:
                question = f"{concept} este {correct_def}."
                answer = True
            else:
                question = f"{concept} este {other}."
                answer = False

            questions.append({
                "type": "true_false",
                "question": question,
                "correct_answer": answer
            })

        # HARD -> MCQ
        else:
            options = [correct_def]

            distractors = random.sample(definitions, min(3, len(definitions)-1))

            for d in distractors:
                if d["definition"] != correct_def:
                    options.append(d["definition"])

            random.shuffle(options)

            questions.append({
                "type": "mcq",
                "question": f"Ce reprezinta {concept}?",
                "options": options,
                "correct_answer": correct_def
            })

    return questions