# Frontend JavaScript - Auto-refresh pending links

## API Response Structure

```json
{
  "id": "uuid",
  "original_url": "https://s.shopee.vn/...",
  "resolved_url": "https://shopee.vn/...",
  "status": "pending|processing|done|failed",
  "product_id": "uuid",
  "error_message": "...",
  "created_at": "2026-05-08T..."
}
```

## Implementation Guide

### 1. Create Link (Form Submit)

```javascript
// File: resources/js/links.js

async function createLink(url) {
    try {
        const response = await fetch('/api/links/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({ url: url })
        });
        
        const link = await response.json();
        
        if (link.status === 'pending' || link.status === 'processing') {
            // Show toast notification
            showToast('Đang xử lý link... Bạn có thể tiếp tục sử dụng.', 'info');
            
            // Start polling for status updates
            pollLinkStatus(link.id);
            
            // Redirect to dashboard (user can continue working)
            window.location.href = '/links';
        } else if (link.status === 'done') {
            // Already completed (sync mode)
            showToast('Link đã được tạo thành công!', 'success');
            window.location.href = `/links/${link.id}`;
        }
    } catch (error) {
        showToast('Lỗi khi tạo link: ' + error.message, 'error');
    }
}
```

### 2. Poll Link Status (Auto-refresh)

```javascript
// Poll every 3 seconds until done/failed
function pollLinkStatus(linkId, maxAttempts = 40) {
    let attempts = 0;
    
    const intervalId = setInterval(async () => {
        attempts++;
        
        try {
            const response = await fetch(`/api/links/${linkId}/`, {
                headers: {
                    'Authorization': `Bearer ${getToken()}`
                }
            });
            const link = await response.json();
            
            if (link.status === 'done') {
                clearInterval(intervalId);
                showToast('Link đã được xử lý xong!', 'success');
                
                // Update UI if user still on page
                updateLinkCard(linkId, link);
                
                // Or reload page
                // window.location.reload();
            } else if (link.status === 'failed') {
                clearInterval(intervalId);
                showToast('Xử lý link thất bại: ' + link.error_message, 'error');
                updateLinkCard(linkId, link);
            } else if (attempts >= maxAttempts) {
                // Timeout after 2 minutes (40 * 3s)
                clearInterval(intervalId);
                showToast('Xử lý link đang mất nhiều thời gian. Vui lòng refresh sau.', 'warning');
            }
        } catch (error) {
            console.error('Poll error:', error);
        }
    }, 3000); // Poll every 3 seconds
}
```

### 3. Update UI (Link Card)

```javascript
function updateLinkCard(linkId, linkData) {
    const card = document.querySelector(`[data-link-id="${linkId}"]`);
    if (!card) return;
    
    // Update status badge
    const statusBadge = card.querySelector('.status-badge');
    if (statusBadge) {
        statusBadge.className = `badge bg-${getStatusColor(linkData.status)}`;
        statusBadge.textContent = linkData.status;
    }
    
    // If done, fetch and show product info
    if (linkData.status === 'done' && linkData.product_id) {
        fetchProductInfo(linkData.product_id).then(product => {
            // Update card with product data
            updateProductPreview(card, product);
        });
    }
}

function getStatusColor(status) {
    const colors = {
        'pending': 'warning',
        'processing': 'info',
        'done': 'success',
        'failed': 'danger'
    };
    return colors[status] || 'secondary';
}
```

### 4. Show Toast Notification

```javascript
// Using Bootstrap Toast
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}" 
             role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const container = document.getElementById('toast-container');
    container.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = container.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Auto-remove after hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}
```

### 5. HTML Structure

```html
<!-- Add to layout.blade.php -->
<div id="toast-container" 
     class="position-fixed top-0 end-0 p-3" 
     style="z-index: 11"></div>

<!-- Link creation form -->
<form id="create-link-form" onsubmit="handleSubmit(event)">
    <input type="url" name="url" placeholder="Paste Shopee affiliate link..." required>
    <button type="submit" id="submit-btn">Tạo link</button>
</form>

<script>
async function handleSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const url = form.url.value;
    const btn = form.querySelector('#submit-btn');
    
    // Disable button while processing
    btn.disabled = true;
    btn.textContent = 'Đang xử lý...';
    
    await createLink(url);
    
    // Re-enable after a moment (will redirect anyway)
    setTimeout(() => {
        btn.disabled = false;
        btn.textContent = 'Tạo link';
    }, 1000);
}
</script>
```

---

## Laravel Blade Implementation

### resources/views/links/create.blade.php

```blade
@extends('layouts.app')

@section('content')
<div class="container">
    <h2>Tạo Affiliate Link</h2>
    
    <form id="create-link-form">
        @csrf
        <div class="mb-3">
            <label for="url" class="form-label">Shopee Affiliate Link</label>
            <input type="url" 
                   class="form-control" 
                   id="url" 
                   name="url" 
                   placeholder="https://s.shopee.vn/..." 
                   required>
            <div class="form-text">
                Paste link affiliate Shopee (dạng s.shopee.vn hoặc full URL)
            </div>
        </div>
        
        <button type="submit" class="btn btn-primary" id="submit-btn">
            <span class="spinner-border spinner-border-sm d-none" id="spinner"></span>
            <span id="btn-text">Tạo Link</span>
        </button>
    </form>
</div>

<script>
document.getElementById('create-link-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('submit-btn');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btn-text');
    const urlInput = document.getElementById('url');
    
    // Show loading state
    btn.disabled = true;
    spinner.classList.remove('d-none');
    btnText.textContent = 'Đang tạo...';
    
    try {
        const response = await fetch('{{ url("/api/links/") }}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ url: urlInput.value })
        });
        
        const link = await response.json();
        
        if (link.status === 'pending' || link.status === 'processing') {
            showToast('Link đang được xử lý... Bạn có thể tiếp tục làm việc!', 'info');
            
            // Redirect to links page
            setTimeout(() => {
                window.location.href = '{{ route("links.index") }}';
            }, 1000);
        } else if (link.status === 'done') {
            showToast('Link đã được tạo thành công!', 'success');
            window.location.href = `/links/${link.id}`;
        }
    } catch (error) {
        showToast('Lỗi: ' + error.message, 'danger');
        btn.disabled = false;
        spinner.classList.add('d-none');
        btnText.textContent = 'Tạo Link';
    }
});

// Copy toast function here...
</script>
@endsection
```

---

## Performance Benefits

### Before (Sync):
```
User 1: Submit → Wait 10s → Done
User 2: Submit → Wait 10s → Done  
User 3: Submit → Wait 10s → Done

Total: 30s sequential (BLOCKED)
```

### After (Async):
```
User 1: Submit → Return instant → Processing in background
User 2: Submit → Return instant → Processing in background
User 3: Submit → Return instant → Processing in background

All process in parallel! (10s total)
UI responsive, users can continue working
```

---

## Testing

1. **Enable async mode** (already set in `.env`):
   ```
   ASYNC_LINK_PROCESSING=True
   ```

2. **Test link creation**:
   - Submit link
   - Should see "pending" status
   - Toast notification shown
   - Redirected to dashboard
   - Link auto-updates after ~5-10s

3. **Monitor logs**:
   ```
   Started background thread for link {id}
   Starting scraping for link {id}...
   ✅ Link {id} processing completed!
   ```
