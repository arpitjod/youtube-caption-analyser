# fetch_and_analyze_youtube_comments.py
import re
import time
import pandas as pd
import numpy as np
from googleapiclient.discovery import build
from langdetect import detect
import emoji
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from tqdm.auto import tqdm

# Download NLTK assets
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# ------------ 1) Fetch comments from YouTube Data API v3 ------------
def fetch_comments(video_id: str, api_key: str, max_comments=5000):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    next_page_token = None
    pbar = tqdm(total=max_comments, desc="Fetching comments")
    while True:
        request = youtube.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat='plainText'
        )
        resp = request.execute()
        for item in resp.get('items', []):
            top = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'commentId': top.get('id'),
                'author': top.get('authorDisplayName'),
                'text': top.get('textDisplay'),
                'publishedAt': top.get('publishedAt'),
                'likeCount': top.get('likeCount'),
                'replyCount': item['snippet'].get('totalReplyCount', 0)
            })
            # include replies if present
            if item.get('replies'):
                for r in item['replies'].get('comments', []):
                    rs = r['snippet']
                    comments.append({
                        'commentId': rs.get('id'),
                        'author': rs.get('authorDisplayName'),
                        'text': rs.get('textDisplay'),
                        'publishedAt': rs.get('publishedAt'),
                        'likeCount': rs.get('likeCount'),
                        'replyCount': 0
                    })
            pbar.update(1)
            if len(comments) >= max_comments:
                break
        
        if len(comments) >= max_comments:
            break
        next_page_token = resp.get('nextPageToken')
        if not next_page_token:
            break
        time.sleep(0.1)
    pbar.close()
    return pd.DataFrame(comments)

# ------------ 2) Cleaning functions ------------
URL_RE = re.compile(r'https?://\S+|www\.\S+')
MENTION_RE = re.compile(r'@\w+')
HTML_RE = re.compile(r'<.*?>')
MULTI_SPACE = re.compile(r'\s+')
def remove_emoji(text):
    return emoji.replace_emoji(text, replace='')

PUNCT_RE = re.compile(r'[^\w\s]')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text: str, remove_emojis=True, remove_urls=True, lower=True):
    if not isinstance(text, str):
        return ''
    txt = text
    if remove_urls:
        txt = URL_RE.sub('', txt)
    txt = HTML_RE.sub('', txt)
    txt = MENTION_RE.sub('', txt)
    if remove_emojis:
        txt = remove_emoji(txt)
    if lower:
        txt = txt.lower()
    txt = PUNCT_RE.sub(' ', txt)
    txt = MULTI_SPACE.sub(' ', txt).strip()
    return txt

def preprocess_text(text: str):
    cleaned = clean_text(text)
    lang = 'unknown'
    try:
        lang = detect(text)
    except:
        pass
    tokens = [lemmatizer.lemmatize(tok) for tok in cleaned.split() if tok not in stop_words and len(tok) > 1]
    return ' '.join(tokens), lang

# ------------ 3) Feature extraction: sentiment, embeddings, topics ------------
sentiment_pipe = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def analyze(df: pd.DataFrame):
    if df.empty:
        return df, []
    df['cleaned'], df['lang'] = zip(*df['text'].map(preprocess_text))
    df_en = df[df['lang'].isin(['en','en-US','en-UK','en-GB'] ) | (df['lang'] == 'en')].copy()
    if df_en.empty:
        return df_en, []
        
    sentiments = []
    for b in np.array_split(df_en['cleaned'].tolist(), max(1, len(df_en)//32)):
        if len(b)==0: continue
        res = sentiment_pipe(list(b), truncation=True)
        sentiments.extend(res)
    df_en['sentiment_label'] = [r['label'] for r in sentiments]
    df_en['sentiment_score'] = [r.get('score', None) for r in sentiments]

    df_en['embedding'] = list(embed_model.encode(df_en['cleaned'].tolist(), show_progress_bar=True, convert_to_numpy=True))

    tfidf = TfidfVectorizer(max_df=0.95, min_df=5, ngram_range=(1,2), max_features=2000)
    X = tfidf.fit_transform(df_en['cleaned'].fillna(''))
    n_topics = 8
    nmf = NMF(n_components=n_topics, random_state=0)
    W = nmf.fit_transform(X)
    H = nmf.components_
    topics = []
    feature_names = tfidf.get_feature_names_out()
    for topic_idx, topic in enumerate(H):
        top_features = [feature_names[i] for i in topic.argsort()[:-11:-1]]
        topics.append(" ".join(top_features))
    df_en['topic'] = W.argmax(axis=1)
    df_en['topic_keywords'] = df_en['topic'].map(lambda t: topics[t])

    return df_en, topics

# ------------ 4) Example run ------------
if __name__ == "__main__":
    API_KEY = "YOUR_YOUTUBE_API_KEY_HERE" # Replace for direct script run
    VIDEO_ID = "3JZ_D3ELwOQ"
    df = fetch_comments(VIDEO_ID, API_KEY, max_comments=1000)
    print("Fetched", len(df), "comments")
    analyzed_df, topics = analyze(df)
    analyzed_df.to_csv("youtube_comments_analysis.csv", index=False)
    print("Saved youtube_comments_analysis.csv")
    print("Topics found:")
    for i, t in enumerate(topics):
        print(i, ":", t)
    
    # ------------ 5) Sentiment Analysis Reports & Visualizations ------------
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    df = pd.read_csv("youtube_comments_analysis.csv")
    print("Sentiment counts:")
    print(df['sentiment_label'].value_counts())
    df['sentiment_label'].value_counts().plot(kind='bar', title='Sentiment Distribution')
    plt.show()