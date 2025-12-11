// Bookmarks and Tabs Display Functions

function showBookmarks() {
    const chatArea = document.getElementById('chatArea');
    chatArea.innerHTML = '';
    
    // Add title
    const titleDiv = document.createElement('div');
    titleDiv.style.cssText = 'font-weight: 600; font-size: 18px; margin: 24px 16px 16px 16px; color: #202124;';
    titleDiv.textContent = '📚 ブックマーク';
    chatArea.appendChild(titleDiv);
    
    // Get bookmarks from localStorage
    const bookmarks = JSON.parse(localStorage.getItem('bookmarks') || '[]');
    
    if (bookmarks.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.style.cssText = 'color: #888; padding: 20px; text-align: center; margin: 0 16px;';
        emptyDiv.textContent = 'ブックマークがありません';
        chatArea.appendChild(emptyDiv);
        return;
    }
    
    // Display bookmarks
    bookmarks.forEach((bookmark, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.style.cssText = 'margin: 0 16px 12px 16px; padding: 16px; background: #ffffff; border: 1px solid #e8eaed; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); position: relative;';
        
        cardDiv.innerHTML = `
            <div style="font-weight: 600; font-size: 15px; margin-bottom: 8px;">
                <a href="${bookmark.url}" target="_self" style="color: #0063B2; text-decoration: none; font-weight: 500;">
                    ${bookmark.title}
                </a>
                <button class="remove-bookmark-btn" data-index="${index}" style="float: right; background: none; border: none; cursor: pointer; font-size: 18px; color: #d93025; padding: 0; margin-left: 8px;" title="ブックマークから削除">×</button>
            </div>
            <div style="color: #006621; font-size: 13px; word-break: break-all;">
                ${bookmark.url}
            </div>
            <div style="color: #5f6368; font-size: 12px; margin-top: 8px;">
                追加日時: ${new Date(bookmark.timestamp).toLocaleString('ja-JP')}
            </div>
        `;
        
        chatArea.appendChild(cardDiv);
    });
    
    // Add event listeners for remove buttons
    document.querySelectorAll('.remove-bookmark-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.getAttribute('data-index'));
            bookmarks.splice(index, 1);
            localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
            showBookmarks(); // Refresh display
        });
    });
}

function showTabs() {
    const chatArea = document.getElementById('chatArea');
    chatArea.innerHTML = '';
    
    // Add title
    const titleDiv = document.createElement('div');
    titleDiv.style.cssText = 'font-weight: 600; font-size: 18px; margin: 24px 16px 16px 16px; color: #202124;';
    titleDiv.textContent = '🗂️ タブ履歴';
    chatArea.appendChild(titleDiv);
    
    // Get tabs from localStorage
    const tabs = JSON.parse(localStorage.getItem('tabs') || '[]');
    
    if (tabs.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.style.cssText = 'color: #888; padding: 20px; text-align: center; margin: 0 16px;';
        emptyDiv.textContent = 'タブ履歴がありません';
        chatArea.appendChild(emptyDiv);
        return;
    }
    
    // Display tabs (most recent first)
    tabs.reverse().forEach((tab, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.style.cssText = 'margin: 0 16px 12px 16px; padding: 16px; background: #ffffff; border: 1px solid #e8eaed; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); position: relative;';
        
        cardDiv.innerHTML = `
            <div style="font-weight: 600; font-size: 15px; margin-bottom: 8px;">
                <a href="${tab.url}" target="_self" style="color: #0063B2; text-decoration: none; font-weight: 500;">
                    ${tab.title}
                </a>
                <button class="remove-tab-btn" data-index="${tabs.length - 1 - index}" style="float: right; background: none; border: none; cursor: pointer; font-size: 18px; color: #d93025; padding: 0; margin-left: 8px;" title="タブ履歴から削除">×</button>
            </div>
            <div style="color: #006621; font-size: 13px; word-break: break-all;">
                ${tab.url}
            </div>
            <div style="color: #5f6368; font-size: 12px; margin-top: 8px;">
                訪問日時: ${new Date(tab.timestamp).toLocaleString('ja-JP')}
            </div>
        `;
        
        chatArea.appendChild(cardDiv);
    });
    
    // Add event listeners for remove buttons
    document.querySelectorAll('.remove-tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.getAttribute('data-index'));
            tabs.splice(index, 1);
            localStorage.setItem('tabs', JSON.stringify(tabs));
            showTabs(); // Refresh display
        });
    });
}
