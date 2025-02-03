function handleError(error, context) {
  console.error(`Error in ${context}:`, error);
  showNotification(`Error in ${context}: ${error.message}`);
}

chrome.downloads.onDeterminingFilename.addListener((downloadItem, suggest) => {
  try {
    console.log(`Blocking download: ${downloadItem.url}`);
    suggest({ filename: downloadItem.filename || 'download', cancel: true });
  } catch (error) {
    handleError(error, 'onDeterminingFilename');
  }
});

chrome.downloads.onCreated.addListener((downloadItem) => {
  try {
    chrome.downloads.pause(downloadItem.id, () => {
      if (chrome.runtime.lastError) {
        handleError(chrome.runtime.lastError, 'pausing download');
        return;
      }
      
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon128.png',
        title: 'Download Paused',
        message: 'Do you want to redirect through DDAS?',
        buttons: [
          { title: 'Yes' },
          { title: 'No' }
        ],
        requireInteraction: true
      }, (notificationId) => {
        if (chrome.runtime.lastError) {
          handleError(chrome.runtime.lastError, 'creating notification');
          return;
        }
        
        chrome.notifications.onButtonClicked.addListener((clickedId, buttonIndex) => {
          if (clickedId === notificationId) {
            if (buttonIndex === 0) {
              // User confirmed to redirect
              chrome.downloads.cancel(downloadItem.id, () => {
                if (chrome.runtime.lastError) {
                  handleError(chrome.runtime.lastError, 'cancelling download');
                } else {
                  console.log('Download cancelled successfully');
                  sendUrlToApplication(downloadItem.url);
                }
              });
            } else {
              chrome.downloads.resume(downloadItem.id);
            }
            chrome.notifications.clear(notificationId);
          }
        });
      });
    });
  } catch (error) {
    handleError(error, 'onCreated');
  }
});

function sendUrlToApplication(url) {
  const applicationUrl = "http://localhost:5003/receive-url";

  fetch(applicationUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ url })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Server response:', data);
    showNotification(data.message);
  })
  .catch(error => {
    handleError(error, 'sending URL to application');
  });
}

function showNotification(message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon128.png',
    title: 'DDAS Message',
    message: message
  }, () => {
    if (chrome.runtime.lastError) {
      console.error('Error showing notification:', chrome.runtime.lastError);
    }
  });
}
