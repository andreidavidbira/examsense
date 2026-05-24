from keybert import KeyBERT


# initializam modelul folosit pentru extragerea cuvintelor cheie
kw_model = KeyBERT()


# extragem cele mai relevante cuvinte sau expresii din text
def extract_keywords(text, top_n=5):
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words=None,
        top_n=top_n,
    )

    return [keyword[0] for keyword in keywords]