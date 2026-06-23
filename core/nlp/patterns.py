"""
ExamSense+ - NLP Patterns
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pattern-urile lingvistice folosite pentru extragerea definitiilor
- separa expresiile relevante pentru limba romana si limba engleza
- compileaza expresiile regulate o singura data, pentru viteza mai buna
- grupeaza pattern-urile dupa forta lor, pentru filtrare si scoring
- pastreaza reguli generale, fara dependenta de un anumit document de test
"""

import re

# ================= ROMANA =================

# pattern-uri explicite pentru definitii; acestea sunt cele mai sigure
ROMANIAN_PATTERN_DEFINITION = [
 "poate fi definit ca",
 "poate fi definită ca",
 "poate fi definita ca",
 "poate fi definit drept",
 "poate fi definită drept",
 "poate fi definita drept",
 "este definit ca",
 "este definită ca",
 "este definita ca",
 "este definit drept",
 "este definită drept",
 "este definita drept",
 "se defineste ca",
 "se definește ca",
 "se poate defini ca",
 "se poate considera ca",
 "poate fi considerat ca",
 "poate fi considerată ca",
 "poate fi considerata ca",
 "este denumit",
 "este denumită",
 "este denumita",
 "este numit",
 "este numită",
 "este numita",
 "se numește",
 "se numeste",
 "reprezinta",
 "reprezintă",
 "înseamnă",
 "inseamna",
 "semnifica",
 "semnifică",
 "denota",
 "denotă",
]

# pattern-uri de tip referire sau asociere
ROMANIAN_PATTERN_REFERENCE = [
 "se refera la",
 "se referă la",
 "face referire la",
 "face referire asupra",
 "se refera asupra",
 "se referă asupra",
 "este asociat cu",
 "este asociată cu",
 "este asociata cu",
 "este legat de",
 "este legată de",
 "este legata de",
]

# pattern-uri de tip descriere
ROMANIAN_PATTERN_DESCRIPTION = [
 "poate fi descris ca",
 "poate fi descrisă ca",
 "poate fi descrisa ca",
 "este descris ca",
 "este descrisă ca",
 "este descrisa ca",
]

# pattern-uri care sugereaza structura unui concept
ROMANIAN_PATTERN_STRUCTURE = [
 "este compus din",
 "este compusă din",
 "este compusa din",
 "este format din",
 "este formată din",
 "este formata din",
 "este alcatuit din",
 "este alcătuit din",
 "este alcatuita din",
 "este alcătuită din",
]

# pattern-uri care descriu un proces sau o baza de functionare
ROMANIAN_PATTERN_PROCESS = [
 "consta in",
 "constă în",
 "se bazeaza pe",
 "se bazează pe",
 "are la baza",
 "are la bază",
 "este derivat din",
 "este derivată din",
 "este derivata din",
]

# pattern-uri care indica rolul sau utilizarea unui concept
ROMANIAN_PATTERN_USAGE = [
 "are rolul de",
 "are scopul de",
 "este utilizat pentru",
 "este utilizata pentru",
 "este utilizată pentru",
 "este folosit pentru",
 "este folosita pentru",
 "este folosită pentru",
 "serveste la",
 "servește la",
]

# pattern-uri care indica un context de utilizare
ROMANIAN_PATTERN_CONTEXT = [
 "este utilizat in",
 "este utilizat în",
 "este utilizata in",
 "este utilizată în",
 "este folosit in",
 "este folosit în",
 "este folosita in",
 "este folosită în",
 "este aplicat in",
 "este aplicat în",
 "este aplicată în",
 "este aplicata in",
]

# pattern-uri slabe; acestea se folosesc numai cu validari mai stricte
ROMANIAN_PATTERN_WEAK = [
 "este",
 "sunt",
 "devine",
 "include",
 "conține",
 "contine",
 "constituie",
 "permite",
 "caracterizeaza",
 "caracterizează",
 "definește",
 "defineste",
 "descrie",
]

ROMANIAN_PATTERNS = sorted(
 ROMANIAN_PATTERN_DEFINITION
 + ROMANIAN_PATTERN_REFERENCE
 + ROMANIAN_PATTERN_DESCRIPTION
 + ROMANIAN_PATTERN_STRUCTURE
 + ROMANIAN_PATTERN_PROCESS
 + ROMANIAN_PATTERN_USAGE
 + ROMANIAN_PATTERN_CONTEXT
 + ROMANIAN_PATTERN_WEAK,
 key=len,
 reverse=True,
)

STRONG_ROMANIAN_PATTERNS = sorted(
 ROMANIAN_PATTERN_DEFINITION
 + ROMANIAN_PATTERN_REFERENCE
 + ROMANIAN_PATTERN_STRUCTURE
 + ROMANIAN_PATTERN_USAGE,
 key=len,
 reverse=True,
)

MEDIUM_ROMANIAN_PATTERNS = sorted(
 ROMANIAN_PATTERN_DESCRIPTION
 + ROMANIAN_PATTERN_PROCESS
 + ROMANIAN_PATTERN_CONTEXT,
 key=len,
 reverse=True,
)

WEAK_ROMANIAN_PATTERNS = sorted(ROMANIAN_PATTERN_WEAK, key=len, reverse=True)

# ================= ENGLISH =================

# patterns commonly used for definitions
ENGLISH_PATTERN_DEFINITION = [
 "can be defined as",
 "is defined as",
 "is defined by",
 "is commonly defined as",
 "is generally defined as",
 "is often defined as",
 "is typically defined as",
 "can be considered as",
 "can be considered a",
 "is considered as",
 "is considered a",
 "can be described as",
 "is described as",
 "is called",
 "is named",
 "means",
 "represents",
 "denotes",
]

# patterns that indicate reference or relation
ENGLISH_PATTERN_REFERENCE = [
 "refers to",
 "relates to",
 "corresponds to",
 "is associated with",
 "is connected to",
 "is related to",
]

# patterns that indicate structure or composition
ENGLISH_PATTERN_STRUCTURE = [
 "consists of",
 "is composed of",
 "is made up of",
 "is built from",
 "is constructed from",
]

# patterns related to process or behavior
ENGLISH_PATTERN_PROCESS = [
 "is based on",
 "is derived from",
 "involves",
]

# usage or role related patterns
ENGLISH_PATTERN_USAGE = [
 "is used for",
 "is used to",
 "is utilized for",
 "is utilized to",
 "serves to",
 "serves as",
 "is intended to",
 "is designed to",
]

# context-related patterns
ENGLISH_PATTERN_CONTEXT = [
 "is applied in",
 "is used in",
 "is implemented in",
]

# classification patterns
ENGLISH_PATTERN_CLASSIFICATION = [
 "is a type of",
 "is a kind of",
 "is a form of",
 "is a class of",
 "is a category of",
]

# weak patterns; they need stronger validation in the extractor
ENGLISH_PATTERN_WEAK = [
 "is",
 "are",
 "contains",
 "includes",
 "allows",
 "enables",
 "defines",
 "describes",
 "characterizes",
]

ENGLISH_PATTERNS = sorted(
 ENGLISH_PATTERN_DEFINITION
 + ENGLISH_PATTERN_REFERENCE
 + ENGLISH_PATTERN_STRUCTURE
 + ENGLISH_PATTERN_PROCESS
 + ENGLISH_PATTERN_USAGE
 + ENGLISH_PATTERN_CONTEXT
 + ENGLISH_PATTERN_CLASSIFICATION
 + ENGLISH_PATTERN_WEAK,
 key=len,
 reverse=True,
)

STRONG_ENGLISH_PATTERNS = sorted(
 ENGLISH_PATTERN_DEFINITION
 + ENGLISH_PATTERN_REFERENCE
 + ENGLISH_PATTERN_STRUCTURE
 + ENGLISH_PATTERN_USAGE
 + ENGLISH_PATTERN_CLASSIFICATION,
 key=len,
 reverse=True,
)

MEDIUM_ENGLISH_PATTERNS = sorted(
 ENGLISH_PATTERN_PROCESS + ENGLISH_PATTERN_CONTEXT,
 key=len,
 reverse=True,
)

WEAK_ENGLISH_PATTERNS = sorted(ENGLISH_PATTERN_WEAK, key=len, reverse=True)

# ================= FILTRARE =================

# cuvinte care indica inceputuri de discurs, nu concepte reale
DISCOURSE_STARTS = {
 "deci", "astfel", "totusi", "totuși", "insa", "însă", "prin", "pentru", "deoarece",
 "cand", "când", "daca", "dacă", "unde", "iar", "dar",
 "therefore", "thus", "however", "because", "when", "while", "where", "if", "and", "or",
}

# cuvinte prea generale pentru a fi folosite ca termeni centrali
GENERIC_CONCEPTS = {
 "acesta", "aceasta", "acestea", "acest", "acei", "cele", "cel", "cea", "care", "ceea",
 "notiunea", "noțiunea", "conceptul", "principiul", "principiul de baza", "principiul de bază",
 "metoda", "sistemul", "procesul", "aplicatia", "aplicația", "exemplul", "figura", "tabelul",
 "this", "that", "these", "those", "it", "they", "which", "who", "what",
 "method", "system", "process", "application", "example", "figure", "table",
}

# fragmente care apar frecvent in PDF-uri, slide-uri sau cod si trebuie filtrate
METADATA_WORDS = {
 "pagina", "page", "slide", "capitol", "chapter", "figura", "figure", "tabel", "table",
 "copyright", "universitatea", "facultatea", "laborator", "curs", "exemplu", "example",
 "bibliografie", "references", "contents", "cuprins", "anexa", "appendix",
}

# semnale pentru continut procedural, mai putin potrivit pentru definitii
PROCEDURAL_STARTS = {
 "apasati", "apăsați", "selectati", "selectați", "introduceti", "introduceți",
 "executati", "executați", "click", "choose", "select", "press", "run", "open",
 "install", "download", "configure", "set", "create",
}

# ================= REGEX COMPILATE =================

# pattern explicit pentru linii de tip "Concept: definitie" sau "Concept - definitie"
LABELED_DEFINITION_RE = re.compile(
 r"^\s*(?P<concept>[A-ZĂÂÎȘȚA-Za-z0-9][^:\-–—]{2,90})\s*[:\-–—]\s*(?P<definition>.{12,700})$"
)

# pattern pentru eliminarea inceputurilor de lista
LIST_PREFIX_RE = re.compile(r"^\s*(?:\(?\d+\)?[\).]|[a-zA-Z]\)|[•●▪■►▼▲▶◆◇◦‣⁃\-–—])\s+")

# expresie folosita pentru prefiltrare rapida; evita analiza propozitiilor fara semnal definitoriu
DEFINITION_SEPARATOR_RE = re.compile(
 r"(?<!\w)(" + "|".join(re.escape(p) for p in sorted(ROMANIAN_PATTERNS + ENGLISH_PATTERNS, key=len, reverse=True)) + r")(?!\w)",
 flags=re.IGNORECASE,
)

# construieste regulile compilate o singura data, nu pentru fiecare propozitie

def build_pattern_rules(patterns, strong_patterns, medium_patterns, weak_patterns):
 rules = []
 for pattern in sorted(patterns, key=len, reverse=True):
  if pattern in strong_patterns:
   weight = 4
  elif pattern in medium_patterns:
   weight = 3
  elif pattern in weak_patterns:
   weight = 1
  else:
   weight = 2
  regex = re.compile(
   rf"^\s*(?P<concept>.{{2,130}}?)\s+(?<!\w){re.escape(pattern)}(?!\w)\s+(?P<definition>.{{8,700}})\s*$",
   flags=re.IGNORECASE,
  )
  rules.append({
   "pattern": pattern,
   "regex": regex,
   "weight": weight,
   "weak": pattern in weak_patterns,
  })
 return tuple(rules)

ROMANIAN_PATTERN_RULES = build_pattern_rules(
 ROMANIAN_PATTERNS,
 set(STRONG_ROMANIAN_PATTERNS),
 set(MEDIUM_ROMANIAN_PATTERNS),
 set(WEAK_ROMANIAN_PATTERNS),
)

ENGLISH_PATTERN_RULES = build_pattern_rules(
 ENGLISH_PATTERNS,
 set(STRONG_ENGLISH_PATTERNS),
 set(MEDIUM_ENGLISH_PATTERNS),
 set(WEAK_ENGLISH_PATTERNS),
)

PATTERN_WEIGHTS = {}
for rule in ROMANIAN_PATTERN_RULES + ENGLISH_PATTERN_RULES:
 PATTERN_WEIGHTS[rule["pattern"]] = rule["weight"]