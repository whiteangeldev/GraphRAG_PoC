"""Full-width and half-width normalization for the Japanese path."""

import unicodedata


def normalize_text(text: str, *, lang: str) -> str:
    """Fold compatibility characters so Japanese and English share one matcher.

    NFKC maps full-width digits and letters onto their half-width forms and
    leaves Japanese kana and kanji in place.
    """

    folded = unicodedata.normalize("NFKC", text)
    if lang == "ja":
        folded = folded.replace("\u3000", " ")
    return " ".join(folded.split())
