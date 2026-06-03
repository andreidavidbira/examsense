"""
ExamSense+ - AI Prompt Builders
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- construieste prompturile trimise catre modelul AI
- defineste regulile pentru generarea de definitii si intrebari de quiz
- defineste regulile pentru solverul AI care rezolva quiz-urile
- forteaza raspunsuri in format JSON valid, usor de procesat in backend
"""


# construieste promptul pentru generarea de definitii si intrebari pe baza unui document
def build_quiz_generation_prompt(text, difficulty="medium", max_questions=10):
    return f"""
Esti un asistent care citeste un document educational si produce:
1. o lista de definitii importante
2. un set de intrebari de quiz

Raspunsul trebuie sa fie STRICT JSON valid.
Nu folosi markdown.
Nu folosi blocuri ```json.
Nu adauga explicatii.
Nu adauga text in afara JSON-ului.

Formatul JSON trebuie sa fie exact:
{{
  "definitions": [
    {{
      "concept": "string",
      "definition": "string",
      "language": "ro" sau "en",
      "sentence": "string",
      "pattern": "ai_generated"
    }}
  ],
  "questions": [
    {{
      "type": "mcq" | "true_false" | "mcq_reverse",
      "language": "ro" | "en",
      "question": "string",
      "options": ["string", "string", "string", "string"] sau null,
      "correct_answer": "string" sau true/false
    }}
  ]
}}

Reguli foarte importante:
- extrage doar concepte relevante pentru invatare
- definitiile sa fie clare si concise
- genereaza CEL PUTIN {max_questions} intrebari valide
- intrebarile trebuie sa fie distincte, fara duplicate
- intrebarile trebuie sa fie variate si utile
- dificultatea ceruta este: {difficulty}
- daca folosesti tipul "true_false", campul "correct_answer" trebuie sa fie boolean real: true sau false
- daca folosesti tipul "mcq" sau "mcq_reverse", campul "correct_answer" trebuie sa fie exact una dintre optiuni
- pentru "mcq" si "mcq_reverse", furnizeaza exact 4 optiuni
- pentru "mcq_reverse", intrebi conceptul pornind de la definitie
- daca textul este in romana, pune language="ro"
- daca textul este in engleza, pune language="en"
- nu inventa concepte care nu apar in document
- toate intrebarile trebuie sa fie complete si valide
- daca unele intrebari sunt similare, reformuleaza-le astfel incat sa ramana distincte

Textul documentului este:
{text}
""".strip()


# construieste promptul pentru solverul AI care raspunde la intrebarile quiz-ului
def build_quiz_solver_prompt(questions_payload):
    return f"""
Esti un student virtual care rezolva un quiz.

Raspunsul trebuie sa fie STRICT JSON valid.
Nu folosi markdown.
Nu folosi blocuri ```json.
Nu adauga explicatii.
Nu adauga text in afara JSON-ului.

Formatul JSON trebuie sa fie exact:
[
  {{
    "question_id": 123,
    "selected_answer": "string" sau true/false
  }}
]

Reguli:
- raspunde pentru fiecare intrebare exact o data
- nu omite nicio intrebare
- pentru intrebari true_false, "selected_answer" trebuie sa fie boolean real: true sau false
- pentru intrebari mcq sau mcq_reverse, "selected_answer" trebuie sa fie exact una dintre optiunile primite
- nu inventa campuri suplimentare

Intrebarile sunt:
{questions_payload}
""".strip()