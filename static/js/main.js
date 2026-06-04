/* ─── DesiBazaar — Main JavaScript ─── */

// ══════════════════════════════════════════
// Dark Mode
// ══════════════════════════════════════════
const toggleBtn = document.getElementById('darkModeToggle');
const html = document.documentElement;

function applyTheme(theme) {
  html.setAttribute('data-theme', theme);
  document.body.setAttribute('data-theme', theme);
  if (toggleBtn) {
    toggleBtn.innerHTML = theme === 'dark'
      ? '<i class="bi bi-sun-fill"></i>'
      : '<i class="bi bi-moon-fill"></i>';
  }
}

const savedTheme = localStorage.getItem('desibazaar-theme') || 'light';
applyTheme(savedTheme);

if (toggleBtn) {
  toggleBtn.addEventListener('click', () => {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem('desibazaar-theme', next);
    applyTheme(next);
  });
}

// ══════════════════════════════════════════
// Auto-dismiss alerts
// ══════════════════════════════════════════
document.querySelectorAll('.alert-toast').forEach(el => {
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(100%)';
    el.style.transition = 'all 0.4s ease';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

// ══════════════════════════════════════════
// Back to Top
// ══════════════════════════════════════════
const backToTop = document.getElementById('backToTop');
if (backToTop) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      backToTop.classList.add('visible');
    } else {
      backToTop.classList.remove('visible');
    }
  });
  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// ══════════════════════════════════════════
// Intersection Observer — fade-up animation
// ══════════════════════════════════════════
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => {
        entry.target.classList.add('visible');
      }, i * 80);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ══════════════════════════════════════════
// AJAX Add to Cart
// ══════════════════════════════════════════
function addToCartAjax(productId, btn) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    || document.cookie.match(/csrftoken=([^;]+)/)?.[1];

  fetch(`/cart/add/${productId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      // Update cart badge
      document.querySelectorAll('.cart-badge').forEach(el => {
        el.textContent = data.cart_count;
        el.style.display = data.cart_count > 0 ? 'flex' : 'none';
      });
      // Update bottom nav badge
      document.querySelectorAll('.bn-badge').forEach(el => {
        el.textContent = data.cart_count;
        el.style.display = data.cart_count > 0 ? 'flex' : 'none';
      });
      // Dispatch custom event for badge bounce
      document.dispatchEvent(new CustomEvent('cartUpdated', { detail: { count: data.cart_count } }));
      // Animate button
      if (btn) {
        const orig = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check-lg"></i> Added!';
        btn.disabled = true;
        btn.style.background = '#2E7D32';
        setTimeout(() => {
          btn.innerHTML = orig;
          btn.disabled = false;
          btn.style.background = '';
        }, 1500);
      }
      showToast(data.message || 'Added to cart! 🛒', 'success');
    } else if (data.requires_login) {
      showToast('Please login to add items to cart', 'warning');
      setTimeout(() => window.location.href = '/login/?next=' + window.location.pathname, 1200);
    }
  })
  .catch(() => showToast('Please login to add items to cart', 'warning'));
}

// ══════════════════════════════════════════
// AJAX Wishlist Toggle
// ══════════════════════════════════════════
function toggleWishlistAjax(productId, btn) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    || document.cookie.match(/csrftoken=([^;]+)/)?.[1];

  fetch(`/wishlist/toggle/${productId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      document.querySelectorAll('.wishlist-badge').forEach(el => {
        el.textContent = data.wishlist_count;
      });
      if (btn) {
        const icon = btn.querySelector('i');
        if (data.added) {
          btn.classList.add('active');
          if (icon) { icon.classList.remove('bi-heart'); icon.classList.add('bi-heart-fill'); icon.style.color = '#e53935'; }
        } else {
          btn.classList.remove('active');
          if (icon) { icon.classList.remove('bi-heart-fill'); icon.classList.add('bi-heart'); icon.style.color = ''; }
        }
      }
      showToast(data.message, data.added ? 'success' : 'info');
    }
  })
  .catch(() => showToast('Please login to manage wishlist', 'warning'));
}

// ══════════════════════════════════════════
// Cart quantity update
// ══════════════════════════════════════════
function updateCartQty(itemId, newQty) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    || document.cookie.match(/csrftoken=([^;]+)/)?.[1];

  fetch(`/cart/update/${itemId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `quantity=${newQty}`,
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      // If item was deleted, remove its row from the DOM
      if (data.deleted) {
        const row = document.getElementById(`cart-row-${itemId}`);
        if (row) {
          row.style.opacity = '0';
          row.style.transform = 'translateX(-20px)';
          row.style.transition = 'all 0.3s ease';
          setTimeout(() => { row.remove(); }, 300);
        }
      } else {
        const subtotalEl = document.getElementById(`subtotal-${itemId}`);
        if (subtotalEl) subtotalEl.textContent = `₹${parseFloat(data.subtotal).toFixed(2)}`;
      }
      const totalEl = document.getElementById('cart-total');
      const orderTotalEl = document.getElementById('orderTotal');
      if (totalEl) totalEl.textContent = `₹${parseFloat(data.total).toFixed(2)}`;
      if (orderTotalEl) orderTotalEl.textContent = `₹${parseFloat(data.total).toFixed(2)}`;
      document.querySelectorAll('.cart-badge').forEach(el => el.textContent = data.cart_count);
      document.querySelectorAll('.bn-badge').forEach(el => el.textContent = data.cart_count);
      document.dispatchEvent(new CustomEvent('cartUpdated', { detail: { count: data.cart_count } }));
    }
  });
}

// ══════════════════════════════════════════
// Toast Notification
// ══════════════════════════════════════════
function showToast(message, type = 'success') {
  const container = document.querySelector('.messages-container') || (() => {
    const c = document.createElement('div');
    c.className = 'messages-container';
    document.body.appendChild(c);
    return c;
  })();

  const colors = {
    success: '#2E7D32',
    danger: '#c62828',
    warning: '#f57f17',
    info: '#1565c0',
  };
  const icons = {
    success: 'bi-check-circle-fill',
    danger: 'bi-x-circle-fill',
    warning: 'bi-exclamation-circle-fill',
    info: 'bi-info-circle-fill',
  };

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const bgColor = isDark ? '#1e1e1e' : 'white';
  const textColor = isDark ? '#f0f0f0' : '#333';

  const toast = document.createElement('div');
  toast.className = 'alert alert-toast d-flex align-items-center gap-2 mb-2';
  toast.style.cssText = `background:${bgColor}; border-left: 4px solid ${colors[type] || '#333'};box-shadow:0 4px 20px rgba(0,0,0,0.15);`;
  toast.innerHTML = `
    <i class="bi ${icons[type] || 'bi-bell-fill'}" style="color:${colors[type]};font-size:1.1rem;"></i>
    <span style="font-size:0.88rem;font-weight:600;color:${textColor};">${message}</span>
    <button type="button" class="btn-close btn-close-sm ms-auto" onclick="this.parentElement.remove()"></button>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ══════════════════════════════════════════
// Product Image Gallery
// ══════════════════════════════════════════
document.querySelectorAll('.product-thumb').forEach(thumb => {
  thumb.addEventListener('click', function () {
    const mainImg = document.getElementById('mainProductImg');
    if (mainImg) {
      mainImg.src = this.src.replace('?w=80', '?w=600');
      document.querySelectorAll('.product-thumb').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
    }
  });
});

// ══════════════════════════════════════════
// Star Rating Interactive
// ══════════════════════════════════════════
const stars = document.querySelectorAll('.star-rating-input i');
const ratingInput = document.getElementById('id_rating');
stars.forEach((star, i) => {
  star.addEventListener('click', () => {
    stars.forEach((s, j) => {
      s.classList.toggle('filled', j <= i);
    });
    if (ratingInput) ratingInput.value = i + 1;
  });
  star.addEventListener('mouseenter', () => {
    stars.forEach((s, j) => s.classList.toggle('filled', j <= i));
  });
});
const starContainer = document.querySelector('.star-rating-input');
if (starContainer) {
  starContainer.addEventListener('mouseleave', () => {
    const val = ratingInput ? parseInt(ratingInput.value) : 0;
    stars.forEach((s, j) => s.classList.toggle('filled', j < val));
  });
}

// ══════════════════════════════════════════
// Newsletter subscribe AJAX
// ══════════════════════════════════════════
const newsletterForm = document.getElementById('newsletterForm');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const email = this.querySelector('input[type=email]').value;
    const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]')?.value;
    fetch('/newsletter/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `email=${encodeURIComponent(email)}`,
    })
    .then(res => res.json())
    .then(data => {
      showToast(data.message, 'success');
      this.reset();
    });
  });
}

// ══════════════════════════════════════════
// Payment option selector
// ══════════════════════════════════════════
document.querySelectorAll('.payment-option').forEach(opt => {
  opt.addEventListener('click', function () {
    document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('selected'));
    this.classList.add('selected');
    const radio = this.querySelector('input[type=radio]');
    if (radio) radio.checked = true;
  });
});

// ══════════════════════════════════════════
// Sticky Navbar shadow on scroll
// ══════════════════════════════════════════
window.addEventListener('scroll', () => {
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    if (window.scrollY > 10) {
      navbar.style.boxShadow = '0 4px 30px rgba(255,107,53,0.2)';
    } else {
      navbar.style.boxShadow = '0 2px 20px rgba(255,107,53,0.12)';
    }
  }
});

// ══════════════════════════════════════════
// Cart item remove (inline)
// ══════════════════════════════════════════
document.querySelectorAll('.cart-remove-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    const row = this.closest('.cart-item-card');
    if (row) {
      row.style.opacity = '0';
      row.style.transform = 'translateX(-20px)';
      row.style.transition = 'all 0.3s ease';
    }
  });
});

// ══════════════════════════════════════════
// Tooltip init (Bootstrap)
// ══════════════════════════════════════════
const tooltipEls = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
tooltipEls.forEach(el => new bootstrap.Tooltip(el));

console.log('%cDesiBazaar 🛒', 'color:#FF6B35;font-size:24px;font-weight:bold;');
console.log('%cAuthentic Indian Products from Every Corner of India', 'color:#2E7D32;font-size:12px;');

// ══════════════════════════════════════════
// Search Autocomplete
// ══════════════════════════════════════════
(function() {
  const searchInput = document.getElementById('searchInput');
  const dropdown = document.getElementById('searchDropdown');
  if (!searchInput || !dropdown) return;

  let debounceTimer;

  searchInput.addEventListener('input', function() {
    clearTimeout(debounceTimer);
    const q = this.value.trim();
    if (q.length < 2) { dropdown.style.display = 'none'; return; }

    debounceTimer = setTimeout(() => {
      fetch(`/api/search-autocomplete/?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
          if (!data.results.length) { dropdown.style.display = 'none'; return; }
          dropdown.innerHTML = data.results.map(r => `
            <a href="${r.url}" class="search-suggestion-item d-flex align-items-center gap-2 px-3 py-2 text-decoration-none">
              ${r.image ? `<img src="${r.image}" alt="" style="width:40px;height:40px;object-fit:cover;border-radius:8px;flex-shrink:0;">` : `<div style="width:40px;height:40px;background:rgba(255,107,53,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;">🛍️</div>`}
              <div style="min-width:0;">
                <div style="font-weight:600;font-size:0.85rem;color:var(--text-dark);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${r.name}</div>
                <div style="font-size:0.75rem;color:var(--text-muted);">${r.category} · ${r.state}</div>
              </div>
              ${r.price ? `<div class="ms-auto text-primary fw-bold" style="font-size:0.85rem;white-space:nowrap;">₹${r.price}</div>` : ''}
            </a>
          `).join('') + `<div class="px-3 py-2 text-center" style="border-top:1px solid rgba(255,107,53,0.1);">
            <a href="/search/?q=${encodeURIComponent(q)}" class="text-primary small fw-bold">View all results →</a>
          </div>`;
          dropdown.style.display = 'block';
        });
    }, 300);
  });

  document.addEventListener('click', e => {
    if (!searchInput.contains(e.target)) dropdown.style.display = 'none';
  });

  searchInput.addEventListener('keydown', e => {
    if (e.key === 'Escape') dropdown.style.display = 'none';
  });
})();


// ══════════════════════════════════════════
// Quick View Modal
// ══════════════════════════════════════════
function openQuickView(productId) {
  const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';

  // Build modal if not exists
  let modal = document.getElementById('quickViewModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'quickViewModal';
    modal.className = 'modal fade';
    modal.innerHTML = `
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content" style="border-radius:20px;border:none;background:var(--card-bg);">
          <div class="modal-header" style="border:none;padding:1.5rem 1.5rem 0;">
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body p-4" id="quickViewBody">
            <div class="text-center py-5"><div class="spinner-border text-primary"></div></div>
          </div>
        </div>
      </div>`;
    document.body.appendChild(modal);
  }

  const bsModal = new bootstrap.Modal(modal);
  bsModal.show();

  fetch(`/api/quick-view/${productId}/`)
    .then(r => r.json())
    .then(p => {
      const stars = '★'.repeat(Math.round(p.rating)) + '☆'.repeat(5 - Math.round(p.rating));
      document.getElementById('quickViewBody').innerHTML = `
        <div class="row g-4">
          <div class="col-md-5">
            <img src="${p.image}" alt="${p.name}" style="width:100%;border-radius:16px;object-fit:cover;max-height:320px;">
          </div>
          <div class="col-md-7">
            <div class="section-badge mb-2">${p.category}</div>
            <h4 class="fw-bold" style="font-family:'Poppins',sans-serif;">${p.name}</h4>
            <div class="d-flex align-items-center gap-2 mb-2">
              <span style="color:#FFC107;">${stars}</span>
              <span class="text-muted small">${p.rating} (${p.reviews} reviews)</span>
            </div>
            <div class="d-flex align-items-center gap-3 mb-3">
              <span style="font-size:1.8rem;font-weight:800;color:var(--primary);">₹${p.price}</span>
              ${p.original_price ? `<span class="text-muted text-decoration-line-through fs-5">₹${p.original_price}</span><span class="badge bg-danger">${p.discount}% OFF</span>` : ''}
            </div>
            <p class="text-muted mb-3" style="font-size:0.9rem;line-height:1.7;">${p.description}</p>
            <div class="d-flex align-items-center gap-2 mb-4">
              <i class="bi bi-geo-alt-fill text-primary"></i>
              <span class="text-muted small">Origin: <strong>${p.state}</strong></span>
              ${p.in_stock ? '<span class="badge bg-success ms-2">In Stock</span>' : '<span class="badge bg-danger ms-2">Out of Stock</span>'}
            </div>
            <div class="d-flex flex-wrap gap-2">
              ${p.in_stock ? `
              <form method="POST" action="/cart/add/${p.id}/" style="display:inline;">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf}">
                <button type="submit" class="btn-primary-custom" style="border:none;padding:0.6rem 1.5rem;font-size:0.9rem;">
                  <i class="bi bi-bag-plus me-2"></i>Add to Cart
                </button>
              </form>` : ''}
              <a href="${p.url}" class="btn-outline-custom" style="padding:0.6rem 1.5rem;font-size:0.9rem;">
                <i class="bi bi-eye me-1"></i>View Full Details
              </a>
            </div>
            ${p.tags.length ? `<div class="mt-3">${p.tags.slice(0,5).map(t=>`<span class="badge" style="background:rgba(255,107,53,0.1);color:var(--primary);margin-right:4px;font-weight:500;">${t}</span>`).join('')}</div>` : ''}
          </div>
        </div>`;

      // Track recently viewed
      fetch(`/api/track-viewed/${p.id}/`);
    });
}


// ══════════════════════════════════════════
// Recently Viewed — load on homepage/product list
// ══════════════════════════════════════════
(function loadRecentlyViewed() {
  const container = document.getElementById('recentlyViewedContainer');
  if (!container) return;

  fetch('/api/recently-viewed/')
    .then(r => r.json())
    .then(data => {
      if (!data.products.length) { container.parentElement?.remove(); return; }
      container.innerHTML = data.products.map(p => `
        <div class="col-6 col-md-4 col-lg-3">
          <a href="/products/${p.slug}/" class="text-decoration-none">
            <div class="product-card h-100 p-0 overflow-hidden" style="cursor:pointer;">
              <div style="position:relative;height:140px;overflow:hidden;">
                <img src="${p.image}" alt="${p.name}" loading="lazy"
                  style="width:100%;height:100%;object-fit:cover;transition:transform 0.4s ease;">
              </div>
              <div class="p-3">
                <div class="product-category">${p.category}</div>
                <div class="product-name" style="font-size:0.85rem;font-weight:600;color:var(--text-dark);margin-bottom:4px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">${p.name}</div>
                <div class="product-price">₹${p.price}</div>
              </div>
            </div>
          </a>
        </div>`).join('');
    });
})();


// ══════════════════════════════════════════
// Coupon Code
// ══════════════════════════════════════════
const couponForm = document.getElementById('couponForm');
if (couponForm) {
  couponForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const code = document.getElementById('couponInput').value.trim();
    const csrf = this.querySelector('[name=csrfmiddlewaretoken]')?.value;
    const msgEl = document.getElementById('couponMessage');

    fetch('/api/coupon/apply/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `code=${encodeURIComponent(code)}`,
    })
    .then(r => r.json())
    .then(data => {
      if (msgEl) {
        msgEl.textContent = data.message;
        msgEl.className = data.valid ? 'text-success small mt-1' : 'text-danger small mt-1';
      }
      if (data.valid) {
        showToast(`${data.discount}% discount applied!`, 'success');
        // Update total if discount element exists
        const discountRow = document.getElementById('couponDiscountRow');
        if (discountRow) discountRow.style.display = 'flex';
        const discountEl = document.getElementById('couponDiscountAmount');
        const totalEl = document.getElementById('orderTotal');
        if (discountEl && totalEl) {
          const total = parseFloat(totalEl.dataset.amount || totalEl.textContent.replace('₹',''));
          const disc = (total * data.discount / 100).toFixed(2);
          discountEl.textContent = `-₹${disc}`;
          totalEl.textContent = `₹${(total - disc).toFixed(2)}`;
        }
      }
    });
  });
}


// ══════════════════════════════════════════
// Compare Products
// ══════════════════════════════════════════
function toggleCompare(productId, btn) {
  fetch(`/api/compare/${productId}/`)
    .then(r => r.json())
    .then(data => {
      if (!data.ok) { showToast(data.message, 'warning'); return; }
      const bar = document.getElementById('compareBar');
      const countEl = document.getElementById('compareCount');
      if (bar) bar.style.display = data.count > 0 ? 'flex' : 'none';
      if (countEl) countEl.textContent = data.count;

      if (btn) {
        const added = data.ids.includes(productId);
        btn.classList.toggle('active', added);
        btn.title = added ? 'Remove from compare' : 'Compare';
        const icon = btn.querySelector('i');
        if (icon) {
          icon.style.color = added ? '#FF6B35' : '';
        }
      }
      showToast(data.count > 0 ? `${data.count} product(s) in compare` : 'Removed from compare', 'info');
    });
}


// ══════════════════════════════════════════
// WhatsApp Float Button
// ══════════════════════════════════════════
(function addWhatsApp() {
  const btn = document.createElement('a');
  btn.href = 'https://wa.me/911800123456?text=Hi%2C%20I%20need%20help%20with%20my%20DesiBazaar%20order';
  btn.target = '_blank';
  btn.rel = 'noopener noreferrer';
  btn.setAttribute('aria-label', 'Chat on WhatsApp');
  btn.style.cssText = `
    position:fixed; bottom:5.5rem; right:1.5rem; z-index:9990;
    width:52px; height:52px; border-radius:50%; background:#25D366;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 4px 20px rgba(37,211,102,0.4);
    transition:all 0.3s ease; text-decoration:none;
  `;
  btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="white" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>`;

  btn.addEventListener('mouseenter', () => btn.style.transform = 'scale(1.12)');
  btn.addEventListener('mouseleave', () => btn.style.transform = 'scale(1)');
  document.body.appendChild(btn);
})();


// ══════════════════════════════════════════
// Cookie Consent Banner
// ══════════════════════════════════════════
(function cookieConsent() {
  if (localStorage.getItem('db-cookie-consent')) return;

  const banner = document.createElement('div');
  banner.id = 'cookieBanner';
  banner.style.cssText = `
    position:fixed; bottom:0; left:0; right:0; z-index:9999;
    background:var(--card-bg,#fff); border-top:1px solid rgba(255,107,53,0.2);
    box-shadow:0 -4px 30px rgba(0,0,0,0.12);
    padding:1rem 1.5rem; display:flex; align-items:center; gap:1rem; flex-wrap:wrap;
    animation:slideUp 0.4s ease;
  `;
  banner.innerHTML = `
    <div style="flex:1;min-width:200px;">
      <strong style="font-family:'Poppins',sans-serif;font-size:0.9rem;">🍪 We use cookies</strong>
      <p style="margin:0;font-size:0.8rem;color:var(--text-muted,#666);margin-top:2px;">
        To enhance your shopping experience, remember your cart, and analyse site traffic.
        <a href="/privacy/" style="color:var(--primary,#FF6B35);font-weight:600;">Learn more</a>
      </p>
    </div>
    <div class="d-flex gap-2 flex-wrap">
      <button onclick="acceptCookies()" style="background:var(--primary,#FF6B35);color:white;border:none;padding:0.5rem 1.2rem;border-radius:20px;font-weight:600;font-size:0.85rem;cursor:pointer;">
        Accept All
      </button>
      <button onclick="document.getElementById('cookieBanner').remove();localStorage.setItem('db-cookie-consent','essential');"
        style="background:transparent;color:var(--text-muted);border:1px solid #ddd;padding:0.5rem 1.2rem;border-radius:20px;font-size:0.85rem;cursor:pointer;">
        Essential Only
      </button>
    </div>`;

  setTimeout(() => document.body.appendChild(banner), 1500);
})();

function acceptCookies() {
  localStorage.setItem('db-cookie-consent', 'all');
  const b = document.getElementById('cookieBanner');
  if (b) { b.style.transform = 'translateY(100%)'; b.style.transition = '0.3s ease'; setTimeout(() => b.remove(), 300); }
}


// ══════════════════════════════════════════
// Social Share
// ══════════════════════════════════════════
function shareProduct(platform) {
  const url = encodeURIComponent(window.location.href);
  const title = encodeURIComponent(document.title);
  const urls = {
    whatsapp: `https://wa.me/?text=${title}%20${url}`,
    twitter: `https://twitter.com/intent/tweet?text=${title}&url=${url}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
    copy: null,
  };
  if (platform === 'copy') {
    navigator.clipboard.writeText(window.location.href).then(() => showToast('Link copied to clipboard!', 'success'));
    return;
  }
  window.open(urls[platform], '_blank', 'width=600,height=400');
}


// ══════════════════════════════════════════
// Track page view (recently viewed)
// ══════════════════════════════════════════
const productIdMeta = document.querySelector('meta[name="product-id"]');
if (productIdMeta) {
  const pid = parseInt(productIdMeta.content);
  if (pid) fetch(`/api/track-viewed/${pid}/`);
}
