"""
ExamSense+ - NLP Text Cleaner
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- curata textul brut extras din documente
- elimina simbolurile nedorite aparute dupa OCR sau parsarea PDF-urilor
- normalizeaza newline-urile si spatiile
- reduce header-ele, footer-ele si marcajele repetitive din documente
- pregateste textul pentru etapele urmatoare din pipeline-ul NLP
"""

import re
from collections import Counter

BULLET_CHARS = "•●▪■►▼▲▶◆◇◦‣⁃-–—"

_SPACE_RE = re.compile(r"[ \t]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
_BAD_SYMBOLS_RE = re.compile(r"[●▪■►▼▲▶◆◇◦‣⁃]")
_LIST_PREFIX_RE = re.compile(rf"^\s*(?:[{re.escape(BULLET_CHARS)}]+|\(?\d+\)?[\).]|[a-zA-Z]\))\s+")
_NUMBERING_RE = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+")
_PAGE_MARKER_RE = re.compile(
 r"^(?:\d+|\d+\s*/\s*\d+|page\s+\d+(?:\s+of\s+\d+)?|pagina\s+\d+(?:\s+din\s+\d+)?|\d+\s+of\s+\d+)$",
 flags=re.IGNORECASE,
)
_DEFINITION_VERB_RE = re.compile(
 r"\b(este|sunt|reprezintă|reprezinta|înseamnă|inseamna|se referă|se refera|is|are|means|refers|represents)\b",
 flags=re.IGNORECASE,
)

# normalizeaza spatiile multiple din text

def normalize_spaces(text):
 return _SPACE_RE.sub(" ", str(text)).strip()

# repara cateva artefacte OCR/PDF frecvente in limba romana
# regula este generala: multe PDF-uri extrag s, / t, in loc de ș / ț

def fix_common_romanian_ocr(text):
 vowels = "aăâeéiîoóuúAĂÂEÉIÎOÓUÚ"
 text = re.sub(rf"s,(?=[{vowels}])", "ș", text)
 text = re.sub(rf"S,(?=[{vowels}])", "Ș", text)
 text = re.sub(rf"t,(?=[{vowels}])", "ț", text)
 text = re.sub(rf"T,(?=[{vowels}])", "Ț", text)
 text = text.replace("a˘", "ă").replace("A˘", "Ă")
 text = text.replace("ˆı", "î").replace("ˆI", "Î")
 return text

# detecteaza linii de tip numar de pagina, footer sau cod de slide

def is_page_marker(line):
 return bool(_PAGE_MARKER_RE.fullmatch(normalize_spaces(line)))

# detecteaza linii care seamana mai mult cu un titlu decat cu o propozitie

def is_probable_heading(line):
 line = normalize_spaces(line)
 if not line:
  return False
 simplified = _NUMBERING_RE.sub("", line).strip()
 words = simplified.split()
 if not words:
  return False
 if len(words) > 12:
  return False
 if simplified.endswith((".", "!", "?", ";")):
  return False
 if _DEFINITION_VERB_RE.search(simplified):
  return False
 letters = [char for char in simplified if char.isalpha()]
 uppercase_ratio = sum(char.isupper() for char in letters) / max(len(letters), 1)
 if uppercase_ratio > 0.65 and len(words) <= 8:
  return True
 if len(words) <= 5 and simplified[0].isupper() and not simplified.endswith(":"):
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
 if current_line[0] in BULLET_CHARS:
  return False
 if previous_line.endswith("-"):
  return True
 if previous_line.endswith((".", "!", "?", ":", ";")):
  return False
 if current_line[0].islower():
  return True
 if len(previous_line.split()) <= 3:
  return False
 # in PDF-uri randurile din paragrafe sunt rupte artificial; le unim moderat
 return True

# elimina linii repetitive de tip header/footer, fara a depinde de un anumit curs

def remove_repeated_short_lines(lines):
 normalized = [normalize_spaces(line).lower() for line in lines]
 counts = Counter(normalized)
 result = []
 for line in lines:
  key = normalize_spaces(line).lower()
  if counts[key] >= 4 and len(line.split()) <= 10:
   continue
  result.append(line)
 return result

# curata o linie bruta extrasa din document

def clean_line(line):
 line = str(line).strip()
 if not line:
  return ""
 line = fix_common_romanian_ocr(line)
 line = line.replace("\u00a0", " ")
 line = line.replace("“", '"').replace("”", '"').replace("„", '"').replace("’", "'")
 line = line.replace("–", "-").replace("—", "-")
 line = _BAD_SYMBOLS_RE.sub(" ", line)
 line = _LIST_PREFIX_RE.sub("", line)
 line = re.sub(r"\s+([.,!?;:])", r"\1", line)
 line = normalize_spaces(line)
 return line

# curata textul brut inainte de procesarea NLP

def clean_text(text):
 if text is None:
  return ""
 text = str(text).replace("\r\n", "\n").replace("\r", "\n")
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
  if cleaned_lines and should_join_with_previous(cleaned_lines[-1], line):
   if cleaned_lines[-1].endswith("-"):
    cleaned_lines[-1] = cleaned_lines[-1][:-1] + line
   else:
    cleaned_lines[-1] = cleaned_lines[-1] + " " + line
  else:
   cleaned_lines.append(line)
 text = "\n".join(cleaned_lines).strip()
 text = _SPACE_RE.sub(" ", text)
 text = _MULTI_NEWLINE_RE.sub("\n\n", text)
 return text.strip()