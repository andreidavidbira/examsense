import re


def clean_text(text):
    # eliminare simboluri OCR/PDF
    text = re.sub(r"[•●▪■►▼▲]", " ", text)

    # normalizare newline
    text = text.replace("\r", "\n")

    # eliminare spatii multiple pe fiecare linie
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line = re.sub(r"\s+", " ", line)
        line = re.sub(r"\s+([.,!?;:])", r"\1", line)

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()