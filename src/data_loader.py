from youtube_transcript_api import YouTubeTranscriptApi

def get_captions(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    captions = " ".join([t["text"] for t in transcript])
    return captions

