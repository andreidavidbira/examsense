from keybert import KeyBERT

kw_model = KeyBERT()


def extract_keywords(text, top_n=5):
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words=None,
        top_n=top_n
    )

    return [kw[0] for kw in keywords]