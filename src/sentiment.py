# sentiment.py

from transformers import pipeline
from data_loader import get_captions
from preprocessing import clean_text

def analyze_video_sentiment(video_id):
    # 1. Get raw captions
    captions = get_captions(video_id)
    
 
    cleaned_captions = clean_text(captions)
    
 
    sentiment_analyzer = pipeline("sentiment-analysis")
    
 
    result = sentiment_analyzer(cleaned_captions[:500])
    
 
    print(f"Sentiment for video {video_id}: {result}")

 
if __name__ == "__main__":
    video_id = "A4_2rxpN5ag"  # replace with any YouTube video ID
    analyze_video_sentiment(video_id)
