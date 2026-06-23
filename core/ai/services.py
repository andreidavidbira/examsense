"""
ExamSense+ - AI Services
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- implementeaza integrarea cu serviciile OpenAI pentru generarea si rezolvarea quiz-urilor
- curata si parseaza raspunsurile brute venite de la model
- normalizeaza definitiile si intrebarile generate de AI
- elimina duplicatele si filtreaza continutul invalid
- ruleaza solverul AI pentru comparatia dintre utilizator si AI
"""

import json
import random
import re
import time

from django.conf import settings
from openai import OpenAI

from .prompts import (
    build_quiz_generation_prompt,
    build_quiz_solver_prompt,
)


client = OpenAI(api_key=settings.OPENAI_API_KEY)


# extrage partea JSON din raspunsul text primit de la model
def _extract_json_text(raw_text):
    if not raw_text:
        raise ValueError("Empty response from AI service.")

    cleaned = str(raw_text).strip()

    # eliminam eventualele blocuri markdown daca modelul le-a returnat
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^```\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    cleaned = cleaned.strip()

    if cleaned.startswith("{") or cleaned.startswith("["):
        return cleaned

    obj_match = re.search(r"(\{.*\})", cleaned, flags=re.DOTALL)
    arr_match = re.search(r"(\[.*\])", cleaned, flags=re.DOTALL)

    candidates = []

    if obj_match:
        candidates.append(obj_match.group(1))

    if arr_match:
        candidates.append(arr_match.group(1))

    if not candidates:
        raise ValueError("Could not find JSON content in AI response.")

    # alegem cea mai lunga bucata identificata ca sa crestem sansele de parse corect
    candidates.sort(key=len, reverse=True)
    return candidates[0]


# parseaza in siguranta JSON-ul returnat de model
def _safe_json_loads(raw_text):
    json_text = _extract_json_text(raw_text)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        # nu afisam continutul raspunsului AI in consola, ca sa nu aglomeram logurile
        print("AI JSON PARSE ERROR:", repr(e))
        raise ValueError("AI returned invalid JSON.")


# reduce codurile de limba la formele folosite in aplicatie
def _normalize_language(value):
    value = str(value or "").strip().lower()

    if value.startswith("ro"):
        return "ro"

    return "en"


# valideaza si normalizeaza o definitie primita de la AI
def _normalize_definition_item(item):
    concept = str(item.get("concept", "")).strip()
    definition = str(item.get("definition", "")).strip()
    language = _normalize_language(item.get("language", "en"))
    sentence = str(item.get("sentence", "")).strip()
    pattern = str(item.get("pattern", "ai_generated")).strip() or "ai_generated"

    if not concept or not definition:
        return None

    return {
        "concept": concept,
        "definition": definition,
        "language": language,
        "sentence": sentence,
        "pattern": pattern,
    }


# limiteaza tipul intrebarii la tipurile permise in aplicatie
def _normalize_question_type(question_type):
    value = str(question_type or "").strip().lower()

    if value in {"mcq", "true_false", "mcq_reverse"}:
        return value

    return "mcq"


# valideaza si normalizeaza o intrebare generata de AI
def _normalize_question_item(item):
    question_type = _normalize_question_type(item.get("type"))
    language = _normalize_language(item.get("language", "en"))
    question_text = str(item.get("question", "")).strip()
    options = item.get("options")
    correct_answer = item.get("correct_answer")

    if not question_text:
        return None

    # tratam separat intrebarile de tip true/false
    if question_type == "true_false":
        if isinstance(correct_answer, str):
            lowered = correct_answer.strip().lower()

            if lowered in {"true", "adevărat", "adevarat", "yes", "1"}:
                correct_answer = True
            elif lowered in {"false", "fals", "no", "0"}:
                correct_answer = False
            else:
                return None
        else:
            correct_answer = bool(correct_answer)

        return {
            "type": "true_false",
            "language": language,
            "question": question_text,
            "options": None,
            "correct_answer": correct_answer,
        }

    normalized_options = []

    if isinstance(options, list):
        for option in options:
            option_text = str(option).strip()

            if option_text:
                normalized_options.append(option_text)

    # eliminam duplicatele din optiuni, pastrand ordinea
    seen = set()
    deduped_options = []

    for option in normalized_options:
        lowered = option.lower()
        if lowered not in seen:
            seen.add(lowered)
            deduped_options.append(option)

    normalized_options = deduped_options
    correct_answer = str(correct_answer or "").strip()

    if not correct_answer:
        return None

    options_lower = [option.lower() for option in normalized_options]

    # ne asiguram ca raspunsul corect exista in lista de optiuni
    if correct_answer.lower() not in options_lower:
        normalized_options.append(correct_answer)

    if len(normalized_options) < 2:
        return None

    # limitam lista la maximum 4 optiuni
    if len(normalized_options) > 4:
        correct_found = None

        for option in normalized_options:
            if option.lower() == correct_answer.lower():
                correct_found = option
                break

        first_three = []
        for option in normalized_options:
            if option.lower() != correct_answer.lower():
                first_three.append(option)
            if len(first_three) == 3:
                break

        if correct_found:
            normalized_options = first_three + [correct_found]
        else:
            normalized_options = normalized_options[:4]

    # folosim forma exacta a raspunsului corect din optiuni
    for option in normalized_options:
        if option.lower() == correct_answer.lower():
            correct_answer = option
            break

    random.shuffle(normalized_options)

    return {
        "type": question_type,
        "language": language,
        "question": question_text,
        "options": normalized_options,
        "correct_answer": correct_answer,
    }


# elimina definitiile duplicate pastrand doar intrarile unice
def _dedupe_definitions(definitions):
    unique_definitions = []
    seen_definitions = set()

    for item in definitions:
        key = (
            item["concept"].strip().lower(),
            item["definition"].strip().lower(),
            item["language"],
        )

        if key not in seen_definitions:
            seen_definitions.add(key)
            unique_definitions.append(item)

    return unique_definitions


# elimina intrebarile duplicate pe baza tipului, limbii si textului
def _dedupe_questions(questions):
    unique_questions = []
    seen_questions = set()

    for item in questions:
        key = (
            item["type"],
            item["language"],
            item["question"].strip().lower(),
        )

        if key not in seen_questions:
            seen_questions.add(key)
            unique_questions.append(item)

    return unique_questions


# face o cerere unica catre model pentru a obtine definitii si intrebari
def _request_quiz_bundle_once(trimmed_text, difficulty, requested_questions):
    prompt = build_quiz_generation_prompt(
        text=trimmed_text,
        difficulty=difficulty,
        max_questions=requested_questions,
    )

    start_time = time.perf_counter()

    response = client.responses.create(
        model=settings.OPENAI_QUESTION_MODEL,
        input=prompt,
    )

    payload = _safe_json_loads(response.output_text)

    if not isinstance(payload, dict):
        raise ValueError("AI response for quiz generation must be a JSON object.")

    definitions_raw = payload.get("definitions", [])
    questions_raw = payload.get("questions", [])

    if not isinstance(definitions_raw, list):
        definitions_raw = []

    if not isinstance(questions_raw, list):
        questions_raw = []

    definitions = []
    for item in definitions_raw:
        if not isinstance(item, dict):
            continue

        normalized = _normalize_definition_item(item)
        if normalized:
            definitions.append(normalized)

    questions = []
    for item in questions_raw:
        if not isinstance(item, dict):
            continue

        normalized = _normalize_question_item(item)
        if normalized:
            questions.append(normalized)

    definitions = _dedupe_definitions(definitions)
    questions = _dedupe_questions(questions)

    duration = time.perf_counter() - start_time
    print(
        f"[AI QUIZ REQUEST] model={settings.OPENAI_QUESTION_MODEL}, "
        f"difficulty={difficulty}, requested={requested_questions}, "
        f"definitions={len(definitions)}, questions={len(questions)}, "
        f"duration={duration:.4f}s"
    )

    return {
        "definitions": definitions,
        "questions": questions,
    }


# genereaza definitii si intrebari cu AI, cu o a doua incercare daca nu ies suficiente
def generate_quiz_bundle_with_ai(text, difficulty="medium", max_questions=10):
    start_time = time.perf_counter()

    if not text or not str(text).strip():
        raise ValueError("Document text is empty.")

    trimmed_text = str(text).strip()
    max_chars = getattr(settings, "OPENAI_INPUT_MAX_CHARS", 60000)

    if len(trimmed_text) > max_chars:
        trimmed_text = trimmed_text[:max_chars]

    # cerem initial mai multe intrebari decat numarul final dorit
    first_request_count = max_questions + max(5, max_questions // 3)

    try:
        first_pass = _request_quiz_bundle_once(
            trimmed_text=trimmed_text,
            difficulty=difficulty,
            requested_questions=first_request_count,
        )
    except Exception as e:
        print("OPENAI QUESTION MODEL ERROR:", repr(e))
        raise

    all_definitions = list(first_pass["definitions"])
    all_questions = list(first_pass["questions"])
    passes = 1

    # daca nu avem suficiente intrebari valide, mai facem o incercare
    if len(all_questions) < max_questions:
        missing_count = max_questions - len(all_questions)
        second_request_count = missing_count + 5

        try:
            second_pass = _request_quiz_bundle_once(
                trimmed_text=trimmed_text,
                difficulty=difficulty,
                requested_questions=second_request_count,
            )

            passes += 1
            all_definitions.extend(second_pass["definitions"])
            all_questions.extend(second_pass["questions"])

            all_definitions = _dedupe_definitions(all_definitions)
            all_questions = _dedupe_questions(all_questions)

        except Exception as e:
            print("OPENAI QUESTION MODEL SECOND PASS ERROR:", repr(e))

    final_questions = all_questions[:max_questions]

    if not final_questions:
        raise ValueError("AI did not generate valid quiz questions.")

    duration = time.perf_counter() - start_time
    print(
        f"[AI QUIZ GENERATION] difficulty={difficulty}, "
        f"requested={max_questions}, generated={len(final_questions)}, "
        f"definitions={len(all_definitions)}, passes={passes}, "
        f"duration={duration:.4f}s"
    )

    return {
        "definitions": all_definitions,
        "questions": final_questions,
    }


# trimite intrebarile catre solverul AI si normalizeaza raspunsurile primite
def solve_quiz_with_ai(question_objects):
    questions_payload = []

    for question in question_objects:
        questions_payload.append({
            "question_id": question.id,
            "question_type": question.question_type,
            "language": question.language,
            "question_text": question.question_text,
            "options": question.options,
        })

    prompt = build_quiz_solver_prompt(
        questions_payload=json.dumps(questions_payload, ensure_ascii=False)
    )

    start_time = time.perf_counter()

    try:
        response = client.responses.create(
            model=settings.OPENAI_SOLVER_MODEL,
            input=prompt,
        )
    except Exception as e:
        print("OPENAI SOLVER MODEL ERROR:", repr(e))
        raise

    payload = _safe_json_loads(response.output_text)

    if not isinstance(payload, list):
        raise ValueError("AI solver response must be a JSON list.")

    question_map = {}
    for question in question_objects:
        question_map[question.id] = question

    normalized_answers = []

    for item in payload:
        if not isinstance(item, dict):
            continue

        question_id = item.get("question_id")
        selected_answer = item.get("selected_answer")

        if question_id not in question_map:
            continue

        question = question_map[question_id]

        if question.question_type == "true_false":
            if isinstance(selected_answer, str):
                lowered = selected_answer.strip().lower()

                if lowered in {"true", "adevărat", "adevarat", "yes", "1"}:
                    selected_answer = True
                elif lowered in {"false", "fals", "no", "0"}:
                    selected_answer = False
                else:
                    selected_answer = False
            else:
                selected_answer = bool(selected_answer)
        else:
            selected_answer = str(selected_answer or "").strip()

            if isinstance(question.options, list):
                matched_option = None

                for option in question.options:
                    if str(option).strip().lower() == selected_answer.lower():
                        matched_option = str(option).strip()
                        break

                if matched_option is not None:
                    selected_answer = matched_option

        normalized_answers.append({
            "question_id": question_id,
            "selected_answer": selected_answer,
        })

    duration = time.perf_counter() - start_time
    print(
        f"[AI SOLVER REQUEST] model={settings.OPENAI_SOLVER_MODEL}, "
        f"questions={len(question_objects)}, answers={len(normalized_answers)}, "
        f"duration={duration:.4f}s"
    )

    return normalized_answers