"""
ExamSense+ - NLP Concept Extraction
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- initializeaza modelul KeyBERT folosit pentru extragerea cuvintelor cheie
- extrage termeni si expresii relevante din text
- ofera suport pentru analiza NLP suplimentara in cadrul proiectului ExamSense+
- pastreaza pipeline-ul functional si cand KeyBERT nu este disponibil
"""

import re
from collections import Counter


# lista mica de stopwords, folosita doar pentru fallback-ul fara KeyBERT
STOPWORDS = {
    # romana
    "un", "o", "unei", "unui", "este", "sunt", "care", "prin", "pentru", "din", "cu", "la",
    "in", "în", "si", "și", "sau", "iar", "dar", "acest", "aceasta", "aceste", "acestea",
    "de", "pe", "ale", "al", "ai", "a", "se", "ca", "fi", "mai", "multe", "poate", "fie",
    "acel", "aceea", "acela", "acestei", "acestor", "dintre", "intre", "între", "sau", "ori",
    # engleza
    "the", "a", "an", "is", "are", "of", "to", "for", "and", "or", "in", "on", "with",
    "that", "this", "as", "by", "from", "can", "be", "used", "using", "which", "where",
}

_kw_model = None


# initializam modelul folosit pentru extragerea cuvintelor cheie
# folosim incarcare intarziata ca sa nu incetineasca pornirea aplicatiei

def get_keyword_model():
    global _kw_model

    if _kw_model is not None:
        return _kw_model

    try:
        from keybert import KeyBERT

        _kw_model = KeyBERT()
    except Exception:
        _kw_model = None

    return _kw_model


# normalizeaza spatiile multiple din text

def normalize_spaces(text):
    return re.sub(r"\s+", " ", str(text)).strip()


# verifica daca un keyword extras este suficient de curat

def is_valid_keyword(keyword):
    keyword = normalize_spaces(keyword)
    words = keyword.split()

    if not keyword:
        return False

    if len(words) > 5:
        return False

    if len(keyword) > 70:
        return False

    if any(len(word) < 2 for word in words):
        return False

    if words[0].lower() in STOPWORDS or words[-1].lower() in STOPWORDS:
        return False

    if all(word.lower() in STOPWORDS for word in words):
        return False

    # eliminam formule, cod si notatii prea tehnice care nu sunt concepte naturale
    if re.search(r"[=+*/\\{}\[\]<>∈⊕≤≥√]", keyword):
        return False

    # un keyword dominat de cifre este de obicei valoare, pagina sau formula
    digit_ratio = sum(char.isdigit() for char in keyword) / max(len(keyword), 1)
    if digit_ratio > 0.25:
        return False

    return True


# fallback simplu pentru extragerea termenilor candidati

def extract_keywords_fallback(text, top_n=5):
    text = normalize_spaces(text.lower())

    # pastram termeni tehnici cu cratima/slash, dar eliminam restul simbolurilor
    tokens = re.findall(r"[a-zăâîșț][a-zăâîșț0-9_\-/]*", text, flags=re.IGNORECASE)
    tokens = [token for token in tokens if token.lower() not in STOPWORDS and len(token) >= 3]

    candidates = Counter()

    for size in (1, 2, 3):
        for index in range(0, len(tokens) - size + 1):
            gram_tokens = tokens[index:index + size]

            if gram_tokens[0].lower() in STOPWORDS or gram_tokens[-1].lower() in STOPWORDS:
                continue

            keyword = " ".join(gram_tokens)

            if is_valid_keyword(keyword):
                # n-gramurile mai lungi primesc scor usor mai mare
                candidates[keyword] += 1 + (size * 0.2)

    return [item[0] for item in candidates.most_common(top_n)]


# extrage cele mai relevante cuvinte sau expresii din textul primit

def extract_keywords(text, top_n=5):
    text = normalize_spaces(text)

    if not text:
        return []

    model = get_keyword_model()

    if model is not None:
        try:
            keywords = model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 3),
                stop_words=None,
                top_n=top_n * 2,
                use_mmr=True,
                diversity=0.45,
            )

            result = []

            for keyword, _score in keywords:
                keyword = normalize_spaces(keyword)

                if is_valid_keyword(keyword):
                    result.append(keyword)

                if len(result) >= top_n:
                    break

            if result:
                return result
        except Exception:
            pass

    return extract_keywords_fallback(text, top_n=top_n)
