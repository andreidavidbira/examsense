import spacy
import re
from langdetect import detect

# incarca ambele limbi(engleza si romana)
nlp_ro = spacy.load("ro_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

STOPWORDS_RO = {"etapa", "aceasta", "acest", "implementarea", "se", "sa", "si", "in", "la", "de", "cu"}
STOPWORDS_EN = {"the", "this", "that", "and", "in", "on", "of", "for", "with"}


def normalize_text(text):
    text = re.sub(r'\s+', ' ', text)

    # normalizare diacritice
    replacements = {
        "ă": "a", "â": "a", "î": "i",
        "ș": "s", "ş": "s",
        "ț": "t", "ţ": "t"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.strip()


def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"


def extract_concepts(text):
    text = normalize_text(text)
    lang = detect_language(text)

    if lang == "ro":
        doc = nlp_ro(text)
        stopwords = STOPWORDS_RO
    else:
        doc = nlp_en(text)
        stopwords = STOPWORDS_EN

    concepts = set()

    # 🔹 ENGLEZA
    if lang == "en":
        for chunk in doc.noun_chunks:
            concept = chunk.text.strip().lower()

            if len(concept) < 3:
                continue

            if len(concept.split()) > 4:
                continue

            if any(word in stopwords for word in concept.split()):
                continue

            concepts.add(concept)

    # 🔹 ROMANA (fallback corect)
    elif lang == "ro":
        for token in doc:
            # luam doar substantive
            if token.pos_ in ["NOUN", "PROPN"]:
                concept = token.text.strip().lower()

                if len(concept) < 3:
                    continue

                if concept in stopwords:
                    continue

                concepts.add(concept)

    return {
        "language": lang,
        "concepts": sorted(list(concepts))
    }