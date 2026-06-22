"""
ExamSense+ - NLP Patterns
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pattern-urile lingvistice folosite pentru extragerea definitiilor
- separa expresiile relevante pentru limba romana si limba engleza
- grupeaza pattern-urile pe categorii semantice
- construieste listele finale ordonate folosite de extractorul NLP
- pastreaza si o ponderare generala a pattern-urilor, folosita pentru ranking
"""

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
    "este formata din",
    "este formată din",
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

# pattern-uri slabe; produc rezultate utile, dar trebuie filtrate/scorate mai atent
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
    ROMANIAN_PATTERN_DEFINITION +
    ROMANIAN_PATTERN_REFERENCE +
    ROMANIAN_PATTERN_DESCRIPTION +
    ROMANIAN_PATTERN_STRUCTURE +
    ROMANIAN_PATTERN_PROCESS +
    ROMANIAN_PATTERN_USAGE +
    ROMANIAN_PATTERN_CONTEXT +
    ROMANIAN_PATTERN_WEAK,
    key=len,
    reverse=True,
)

# pattern-uri considerate puternice pentru scoring
STRONG_ROMANIAN_PATTERNS = sorted(
    ROMANIAN_PATTERN_DEFINITION +
    ROMANIAN_PATTERN_REFERENCE +
    ROMANIAN_PATTERN_STRUCTURE +
    ROMANIAN_PATTERN_USAGE,
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
    ENGLISH_PATTERN_DEFINITION +
    ENGLISH_PATTERN_REFERENCE +
    ENGLISH_PATTERN_STRUCTURE +
    ENGLISH_PATTERN_PROCESS +
    ENGLISH_PATTERN_USAGE +
    ENGLISH_PATTERN_CONTEXT +
    ENGLISH_PATTERN_CLASSIFICATION +
    ENGLISH_PATTERN_WEAK,
    key=len,
    reverse=True,
)

STRONG_ENGLISH_PATTERNS = sorted(
    ENGLISH_PATTERN_DEFINITION +
    ENGLISH_PATTERN_REFERENCE +
    ENGLISH_PATTERN_STRUCTURE +
    ENGLISH_PATTERN_USAGE +
    ENGLISH_PATTERN_CLASSIFICATION,
    key=len,
    reverse=True,
)

WEAK_ENGLISH_PATTERNS = sorted(ENGLISH_PATTERN_WEAK, key=len, reverse=True)


# ================= SCORING =================

# ponderi generale, nu dependente de un anumit document
PATTERN_WEIGHTS = {}

for pattern in STRONG_ROMANIAN_PATTERNS + STRONG_ENGLISH_PATTERNS:
    PATTERN_WEIGHTS[pattern] = 4

for pattern in ROMANIAN_PATTERN_DESCRIPTION + ROMANIAN_PATTERN_PROCESS + ROMANIAN_PATTERN_CONTEXT:
    PATTERN_WEIGHTS.setdefault(pattern, 3)

for pattern in ENGLISH_PATTERN_PROCESS + ENGLISH_PATTERN_CONTEXT:
    PATTERN_WEIGHTS.setdefault(pattern, 3)

for pattern in WEAK_ROMANIAN_PATTERNS + WEAK_ENGLISH_PATTERNS:
    PATTERN_WEIGHTS.setdefault(pattern, 1)
