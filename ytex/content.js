// content.js

// This script runs on the YouTube page.
// Its job is to listen for messages from the popup and interact with the video player.

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Check if the message is the one we're expecting
  if (request.type === "SKIP_SPONSOR") {
    
    // Find the video player element on the page
    const videoPlayer = document.querySelector('video');
    
    if (videoPlayer) {
      console.log(`Skipping to: ${request.timestamp} seconds.`);
      // Set the video's current time to the new timestamp
      videoPlayer.currentTime = request.timestamp;
    }
  }
});