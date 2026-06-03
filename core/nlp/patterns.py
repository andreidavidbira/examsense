"""
ExamSense+ - NLP Patterns
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pattern-urile lingvistice folosite pentru extragerea definitiilor
- separa expresiile relevante pentru limba romana si limba engleza
- grupeaza pattern-urile pe categorii semantice
- construieste listele finale ordonate folosite de extractorul NLP
"""

# ================= ROMANA =================

# pattern-uri tipice pentru definitii
ROMANIAN_PATTERN_DEFINITION = [
    "poate fi definit ca",
    "poate fi definita ca",
    "este definit ca",
    "este definita ca",
    "este definită ca",
    "este definită drept",
    "se defineste ca",
    "se definește ca",
    "se poate defini ca",
    "se poate considera ca",
    "este",
    "reprezinta",
    "reprezintă",
    "înseamnă",
    "semnifica",
    "semnifică",
]

# pattern-uri de tip referire sau asociere
ROMANIAN_PATTERN_REFERENCE = [
    "se refera la",
    "se referă la",
    "face referire la",
    "face referire asupra",
    "se refera asupra",
    "se referă asupra",
]

# pattern-uri de tip descriere
ROMANIAN_PATTERN_DESCRIPTION = [
    "descrie",
    "definește",
    "defineste",
    "caracterizeaza",
    "caracterizează",
    "poate fi descris ca",
    "poate fi descrisa ca",
    "poate fi descrisă ca",
]

# pattern-uri care sugereaza structura unui concept
ROMANIAN_PATTERN_STRUCTURE = [
    "este format din",
    "este formata din",
    "este formată din",
    "este alcatuit din",
    "este alcătuit din",
    "este alcatuita din",
    "este alcătuită din",
]

# pattern-uri care descriu un proces
ROMANIAN_PATTERN_PROCESS = [
    "consta in",
    "constă în",
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
    "este utilizata in",
    "este utilizată în",
    "este folosit in",
    "este folosita in",
    "este folosită în",
]

# pattern-uri speciale care apar mai rar, dar pot produce definitii utile
ROMANIAN_PATTERN_SPECIAL = [
    "constituie",
]


# lista finala pentru extractorul de limba romana
ROMANIAN_PATTERNS = sorted(
    ROMANIAN_PATTERN_DEFINITION +
    ROMANIAN_PATTERN_REFERENCE +
    ROMANIAN_PATTERN_DESCRIPTION +
    ROMANIAN_PATTERN_STRUCTURE +
    ROMANIAN_PATTERN_PROCESS +
    ROMANIAN_PATTERN_USAGE +
    ROMANIAN_PATTERN_CONTEXT +
    ROMANIAN_PATTERN_SPECIAL,
    key=len,
    reverse=True
)

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
    "is",
    "means",
    "represents",
]

# patterns that indicate reference or relation
ENGLISH_PATTERN_REFERENCE = [
    "refers to",
    "relates to",
    "corresponds to",
    "is associated with",
    "is connected to",
]

# descriptive patterns
ENGLISH_PATTERN_DESCRIPTION = [
    "can be described as",
    "is described as",
    "describes",
    "defines",
    "characterizes",
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
    "includes",
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

# optional classification patterns
ENGLISH_PATTERN_CLASSIFICATION = [
    "is a type of",
    "is a kind of",
    "is a form of",
    "is a class of",
    "is a category of",
]

# lista finala pentru extractorul de limba engleza
ENGLISH_PATTERNS = sorted(
    ENGLISH_PATTERN_DEFINITION +
    ENGLISH_PATTERN_REFERENCE +
    ENGLISH_PATTERN_DESCRIPTION +
    ENGLISH_PATTERN_STRUCTURE +
    ENGLISH_PATTERN_PROCESS +
    ENGLISH_PATTERN_USAGE +
    ENGLISH_PATTERN_CONTEXT +
    ENGLISH_PATTERN_CLASSIFICATION,
    key=len,
    reverse=True
)