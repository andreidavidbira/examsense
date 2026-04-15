import spacy

# incarcare model spaCy
nlp = spacy.load("en_core_web_sm")

# extrage concepte (substantive, noun phrases)
def extract_concepts(text):
    doc = nlp(text)

    concepts = set()

    # noun chunks (cele mai importante)
    for chunk in doc.noun_chunks:
        concepts.add(chunk.text.strip())

    return list(concepts)