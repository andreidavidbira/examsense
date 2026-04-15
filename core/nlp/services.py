from langdetect import detect
import spacy

from nlp.definition_extractor import extract_definitions

nlp_ro = spacy.load("ro_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")


def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"


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