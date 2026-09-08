import re
from collections import Counter

STOPWORDS = {
    "از","به","در","با","برای","که","این","آن","را","و","یا","روی",
    "است","هست","شد","شده","می","تا","بر","یک","دو","سه","چهار",
    "های","هایش","هایشان","باشد","کرد","کرده","خواهد","هم","نیز"
}


def tokenize(text: str):

    text = re.sub(r"[^\w\s]", " ", text)

    return text.split()


def extract_keywords(text, limit=20):

    words = []

    for word in tokenize(text):

        word = word.strip()

        if len(word) < 3:
            continue

        if word.isdigit():
            continue

        if word in STOPWORDS:
            continue

        words.append(word)

    counter = Counter(words)

    return [w for w, _ in counter.most_common(limit)]
