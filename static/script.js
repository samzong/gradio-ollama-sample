// Detect and apply system theme
function applyTheme() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.body.classList.add('dark');
  } else {
      document.body.classList.remove('dark');
  }
}

// Listen for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);

// Initially apply theme
applyTheme();

// Use localStorage to save and load conversations
function saveConversations(conversations) {
  localStorage.setItem('conversations', JSON.stringify(conversations));
}

function loadConversations() {
  const saved = localStorage.getItem('conversations');
  return saved ? JSON.parse(saved) : {};
}

// Load conversations on page load
window.addEventListener('load', function() {
  conversations = loadConversations();
  updateConversationList();
});

// Save conversations before page unload
window.addEventListener('beforeunload', function() {
  saveConversations(conversations);
});

function updateConversationList() {
  // Logic to update the conversation list
  // This function needs to be implemented to update the Gradio dropdown
  // You might need to use Gradio's JavaScript API for this
}