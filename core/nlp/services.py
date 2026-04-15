import spacy
from langdetect import detect

from nlp.definition_extractor import extract_definitions

nlp_ro = spacy.load("ro_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")


def detect_language(text):
    try:
        lang = detect(text)
        return "ro" if "ro" in lang else "en"
    except:
        return "en"


def split_sentences(text):
    lang = detect_language(text)

    if lang == "ro":
        doc = nlp_ro(text)
    else:
        doc = nlp_en(text)

    return [sent.text.strip() for sent in doc.sents]


def process_text(text):
    sentences = split_sentences(text)
    definitions = extract_definitions(sentences)

    return {
        "definitions": definitions
    }


# pentru compatibilitate cu restul proiectului
def extract_concepts(text):
    result = process_text(text)
    return result["definitions"]