# backend/server.py
from flask import Flask, jsonify
from flask_cors import CORS
import youtube_comments # This imports your friend's script

# Create a Flask web server
app = Flask(__name__)
# Enable CORS to allow your extension to talk to this server
CORS(app) 

# --- IMPORTANT ---
# Paste your YouTube Data API Key here
API_KEY = "AIzaSyDHGsRVbyaE9A6IpYDY37YbBI3AJitaicI"

# Define an API endpoint that takes a video_id
@app.route('/analyze/<video_id>')
def analyze_video_comments(video_id):
    if not API_KEY or API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
        return jsonify({"error": "YouTube API key is not set in server.py"}), 500
    
    try:
        print(f"Fetching comments for video ID: {video_id}...")
        # 1. Fetch comments (capped at 500 for speed during testing)
        df = youtube_comments.fetch_comments(video_id, API_KEY, max_comments=500)
        
        print(f"Analyzing {len(df)} comments...")
        # 2. Analyze the comments
        analyzed_df, topics = youtube_comments.analyze(df)

        # 3. Prepare the results as a JSON object
        results = {
            "commentCount": len(analyzed_df),
            "sentiment": analyzed_df['sentiment_label'].value_counts().to_dict(),
            "topics": topics,
            "topPositiveComment": analyzed_df.sort_values('sentiment_score', ascending=False).iloc[0]['cleaned'],
            "topNegativeComment": analyzed_df.sort_values('sentiment_score', ascending=True).iloc[0]['cleaned']
        }
        
        print("Analysis complete. Sending results.")
        # 4. Send the results back to the extension
        return jsonify(results)

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

# This allows you to run the server by typing "python server.py"
if __name__ == '__main__':
    app.run(debug=True, port=5000)