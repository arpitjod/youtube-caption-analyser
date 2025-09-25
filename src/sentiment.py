# sentiment.py

from transformers import pipeline
from data_loader import get_captions
from preprocessing import clean_text

def analyze_video_sentiment(video_id):
    # 1. Get raw captions
    captions = get_captions(video_id)
    
    # 2. Clean captions
    cleaned_captions = clean_text(captions)
    
    # 3. Initialize sentiment analysis pipeline
    sentiment_analyzer = pipeline("sentiment-analysis")
    
    # 4. Analyze sentiment (first 500 chars to avoid very long input)
    result = sentiment_analyzer(cleaned_captions[:500])
    
    # 5. Print result
    print(f"Sentiment for video {video_id}: {result}")

# Test the function
if __name__ == "__main__":
    video_id = "A4_2rxpN5ag"  # replace with any YouTube video ID
    analyze_video_sentiment(video_id)
