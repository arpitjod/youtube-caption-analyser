// popup.js

document.addEventListener('DOMContentLoaded', () => {
  const analyzeButton = document.getElementById('analyze-button');
  if (analyzeButton) {
    analyzeButton.addEventListener('click', onAnalyzeButtonClick);
  }
});

async function onAnalyzeButtonClick() {
  const statusText = document.getElementById('status-text');
  const analyzeButton = document.getElementById('analyze-button');
  
  analyzeButton.disabled = true;
  statusText.textContent = 'Getting active tab...';

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (tab.url && tab.url.includes("youtube.com/watch")) {
    const videoId = new URL(tab.url).searchParams.get("v");
    statusText.textContent = 'Fetching transcript...';

    try {
      const transcript = await getTranscript(videoId);
      statusText.textContent = 'Analyzing sentiment...';

      // 1. ANALYZE THE SENTIMENT (This part is new)
      const sentimentResult = await analyzeSentiment(transcript);

      // 2. DISPLAY THE RESULT (This part is new)
      if (sentimentResult) {
        const confidence = (sentimentResult.score * 100).toFixed(0);
        statusText.innerHTML = `Overall Sentiment: <br><strong>${sentimentResult.label}</strong> (${confidence}% confident)`;
      } else {
        statusText.textContent = 'Could not analyze sentiment.';
      }

    } catch (error) {
      statusText.textContent = 'Could not get transcript for this video.';
      console.error(error);
    }

  } else {
    statusText.textContent = 'Not a YouTube video page.';
  }
  
  analyzeButton.disabled = false;
}

// This function to get the transcript stays the same.
async function getTranscript(videoId) {
  const response = await fetch(`https://youtube-transcript-api.vercel.app/?videoId=${videoId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch transcript');
  }
  return response.json();
}

// 3. THIS IS THE NEW AI FUNCTION
// It replaces the old findSponsor function.
async function analyzeSentiment(transcript) {
  // Combine all the small text chunks from the transcript into one big block of text.
  const fullText = transcript.map(chunk => chunk.text).join(' ');

  // Load the sentiment analysis AI model.
  const classifier = await pipeline('sentiment-analysis', 'Xenova/distilbert-base-uncased-finetuned-sst-2-english');

  // Run the model on the full text of the video.
  // We'll only analyze the first 512 words for speed.
  const result = await classifier(fullText.substring(0, 512));

  console.log('Sentiment Analysis Result:', result);
  return result[0]; // The model returns an array, we just need the first item.
}