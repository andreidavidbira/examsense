"""
ExamSense+ - NLP Text Cleaner
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- curata textul brut extras din documente
- elimina simbolurile nedorite aparute dupa OCR sau parsarea PDF-urilor
- normalizeaza newline-urile si spatiile
- pregateste textul pentru etapele urmatoare din pipeline-ul NLP
- aplica reguli generale pentru documente academice, slide-uri si cursuri PDF/DOCX
"""

import re
from collections import Counter


BULLET_CHARS = "•●▪■►▼▲▶◆◇◦‣⁃-–—"


# normalizeaza spatiile multiple din text

def normalize_spaces(text):
    return re.sub(r"[ \t]+", " ", str(text)).strip()


# repara cateva artefacte OCR/PDF frecvente in limba romana
# regula este generala: multe PDF-uri extrag s, / t, in loc de ș / ț

def fix_common_romanian_ocr(text):
    # Corectam doar cazul in care virgula este lipita intre litera si vocala,
    # de exemplu "s,i" -> "și" sau "t,ie" -> "ție".
    # Nu inlocuim "text, imagine", deoarece acolo virgula este punctuatie reala.
    vowels = "aăâeéiîoóuúAĂÂEÉIÎOÓUÚ"
    text = re.sub(rf"s,(?=[{vowels}])", "ș", text)
    text = re.sub(rf"S,(?=[{vowels}])", "Ș", text)
    text = re.sub(rf"t,(?=[{vowels}])", "ț", text)
    text = re.sub(rf"T,(?=[{vowels}])", "Ț", text)
    text = text.replace("a˘", "ă").replace("A˘", "Ă").replace("ˆı", "î")
    return text


# detecteaza linii de tip numar de pagina, footer sau cod de slide

def is_page_marker(line):
    line = normalize_spaces(line)

    if not line:
        return True

    patterns = [
        r"^\d+$",
        r"^\d+\s*/\s*\d+$",
        r"^page\s+\d+(\s+of\s+\d+)?$",
        r"^pagina\s+\d+(\s+din\s+\d+)?$",
        r"^\d+\s+of\s+\d+$",
    ]

    for pattern in patterns:
        if re.fullmatch(pattern, line, flags=re.IGNORECASE):
            return True

    return False


# detecteaza linii care seamana mai mult cu un titlu decat cu o propozitie

def is_probable_heading(line):
    line = normalize_spaces(line)

    if not line:
        return False

    simplified = re.sub(r"^\d+(\.\d+)*\.?\s*", "", line).strip()
    words = simplified.split()

    if not words:
        return False

    if len(words) > 12:
        return False

    if simplified.endswith((".", "!", "?", ";")):
        return False

    # titlurile au frecvent capitalizare ridicata si nu au verb clar
    letters = [char for char in simplified if char.isalpha()]
    uppercase_ratio = sum(char.isupper() for char in letters) / max(len(letters), 1)

    has_definition_verb = re.search(
        r"\b(este|sunt|reprezintă|reprezinta|înseamnă|inseamna|is|are|means|refers)\b",
        simplified,
        flags=re.IGNORECASE,
    )

    if uppercase_ratio > 0.65 and len(words) <= 8 and not has_definition_verb:
        return True

    if len(words) <= 5 and not has_definition_verb and not simplified.endswith(":"):
        return True

    return False


# decide daca doua linii trebuie unite intr-o singura unitate textuala

def should_join_with_previous(previous_line, current_line):
    previous_line = previous_line.rstrip()
    current_line = current_line.lstrip()

    if not previous_line or not current_line:
        return False

    if is_probable_heading(previous_line):
        return False

    if previous_line.endswith("-"):
        return True

    if previous_line.endswith((".", "!", "?", ":", ";")):
        return False

    # nu unim doua bullet-uri diferite
    if current_line[0] in BULLET_CHARS:
        return False

    # daca linia curenta incepe cu litera mica, cel mai probabil continua propozitia
    if current_line[0].islower():
        return True

    # daca linia precedenta este foarte scurta, este probabil heading
    if len(previous_line.split()) <= 3:
        return False

    # in PDF-uri, randurile din paragrafe sunt rupte artificial; le unim moderat
    return True


# elimina linii repetitive de tip header/footer, fara a depinde de un anumit curs

def remove_repeated_short_lines(lines):
    normalized = [normalize_spaces(line).lower() for line in lines]
    counts = Counter(normalized)
    result = []

    for line in lines:
        key = normalize_spaces(line).lower()

        # eliminam doar liniile scurte care se repeta de multe ori; pot fi header/footer
        if counts[key] >= 4 and len(line.split()) <= 8:
            continue

        result.append(line)

    return result


# curata o linie bruta extrasa din document

def clean_line(line):
    line = line.strip()

    if not line:
        return ""

    line = fix_common_romanian_ocr(line)

    # eliminam simboluri parasite aparute frecvent dupa OCR sau extractie din PDF
    line = re.sub(r"[●▪■►▼▲▶◆◇◦‣⁃]", " ", line)

    # transformam bullet-urile in separator simplu, ca sa ramana propozitia citibila
    line = re.sub(rf"^\s*[{re.escape(BULLET_CHARS)}]+\s*", "", line)

    # eliminam prefixe numerice de lista, dar nu distrugem notatii de tip 1.2.3 din text
    line = re.sub(r"^\(?\d+[\).]\s+", "", line)

    # normalizam ghilimelele si apostrofurile
    line = line.replace("“", '"').replace("”", '"').replace("„", '"').replace("’", "'")

    # eliminam spatii inaintea punctuatiei
    line = re.sub(r"\s+([.,!?;:])", r"\1", line)
    line = normalize_spaces(line)

    return line


# curata textul brut inainte de procesarea NLP

def clean_text(text):
    if text is None:
        return ""

    text = str(text)

    # normalizam toate newline-urile la acelasi format
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    raw_lines = text.split("\n")
    lines = []

    for line in raw_lines:
        line = clean_line(line)

        if not line:
            continue

        if is_page_marker(line):
            continue

        lines.append(line)

    lines = remove_repeated_short_lines(lines)

    cleaned_lines = []

    for line in lines:
        # liniile de tip heading sunt pastrate, dar nu sunt unite agresiv cu paragraful urmator
        if cleaned_lines and should_join_with_previous(cleaned_lines[-1], line):
            if cleaned_lines[-1].endswith("-"):
                cleaned_lines[-1] = cleaned_lines[-1][:-1] + line
            else:
                cleaned_lines[-1] = cleaned_lines[-1] + " " + line
        else:
            cleaned_lines.append(line)

    text = "\n".join(cleaned_lines).strip()

    # curatari finale pe tot textul
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
