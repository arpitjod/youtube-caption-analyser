// content.js
function injectButton() {
  const targetElement = document.querySelector('#above-the-fold #top-row');
  if (targetElement && !document.getElementById('yt-comment-analyzer-btn')) {
    const btn = document.createElement('button');
    btn.textContent = 'Analyze Comments';
    btn.id = 'yt-comment-analyzer-btn';
    btn.onclick = handleAnalysisClick;
    targetElement.appendChild(btn);
  }
}

function handleAnalysisClick() {
  const videoId = new URL(window.location.href).searchParams.get("v");
  displayResultsPanel('<p>Sending request to backend... (This can take a minute)</p>');

  chrome.runtime.sendMessage({ type: 'GET_COMMENT_ANALYSIS', videoId: videoId }, (response) => {
    if (!response || response.error) {
      const errorMsg = response ? response.error : 'No response from background.';
      displayResultsPanel(`<p>Error: ${errorMsg}</p>`);
    } else {
      const resultsHTML = formatResults(response);
      displayResultsPanel(resultsHTML);
    }
  });
}

function displayResultsPanel(content) {
  // Remove existing overlay if it exists
  const existingOverlay = document.getElementById('yt-results-overlay');
  if (existingOverlay) existingOverlay.remove();
  
  // Create overlay and panel
  const overlay = document.createElement('div');
  overlay.id = 'yt-results-overlay';

  const panel = document.createElement('div');
  panel.id = 'yt-results-panel';

  const closeBtn = document.createElement('span');
  closeBtn.id = 'yt-results-close-btn';
  closeBtn.innerHTML = '&times;';
  closeBtn.onclick = () => overlay.remove();

  panel.innerHTML = content;
  panel.prepend(closeBtn);
  overlay.appendChild(panel);
  document.body.appendChild(overlay);
}

function formatResults(data) {
  const positive = data.sentiment.POSITIVE || 0;
  const negative = data.sentiment.NEGATIVE || 0;
  let topicsHTML = data.topics.map((topic, index) => `<li><b>Topic ${index + 1}:</b> ${topic}</li>`).join('');

  return `
    <h3>Analysis Complete for ${data.commentCount} comments.</h3>
    <h4>Sentiment Breakdown</h4>
    <p>Positive: ${positive} | Negative: ${negative}</p>
    <h4>Dominant Topics</h4>
    <ul>${topicsHTML}</ul>
    <h4>Top Positive Comment</h4>
    <p><em>"${data.topPositiveComment}"</em></p>
    <h4>Top Negative Comment</h4>
    <p><em>"${data.topNegativeComment}"</em></p>
  `;
}

// YouTube uses a dynamic page, so we need to check when the video player is ready
const observer = new MutationObserver((mutations) => {
  if (document.querySelector('#above-the-fold #top-row')) {
    injectButton();
  }
});

observer.observe(document.body, { childList: true, subtree: true });