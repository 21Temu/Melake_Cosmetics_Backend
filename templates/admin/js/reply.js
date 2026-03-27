function showReplyForm(messageId) {
    const replyHtml = `
        <div id="reply-modal" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
            <div style="background: white; padding: 20px; border-radius: 8px; max-width: 500px; width: 90%;">
                <h3>Quick Reply</h3>
                <textarea id="reply-text" rows="4" style="width: 100%; padding: 8px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px;"></textarea>
                <div style="text-align: right;">
                    <button onclick="closeModal()" style="padding: 8px 16px; margin-right: 10px; background: #6c757d; color: white; border: none; border-radius: 4px;">Cancel</button>
                    <button onclick="sendReply(${messageId})" style="padding: 8px 16px; background: #28a745; color: white; border: none; border-radius: 4px;">Send</button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', replyHtml);
}

function closeModal() {
    const modal = document.getElementById('reply-modal');
    if (modal) modal.remove();
}

async function sendReply(messageId) {
    const replyText = document.getElementById('reply-text').value;
    if (!replyText.trim()) {
        alert('Please enter a reply message');
        return;
    }
    
    try {
        const response = await fetch(`/admin/reply-to-message/${messageId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `reply_text=${encodeURIComponent(replyText)}`
        });
        
        if (response.ok) {
            alert('Reply sent successfully!');
            location.reload();
        } else {
            alert('Failed to send reply');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error sending reply');
    }
}