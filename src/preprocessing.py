import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def clean_text(text):
    # Keep only letters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase and split into words
    words = text.lower().split()
    # Remove stopwords
    words = [w for w in words if w not in stop_words]
    # Join back into string
    return " ".join(words)
