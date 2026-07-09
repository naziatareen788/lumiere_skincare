// ===== SPLASH SCREEN =====
window.addEventListener('load', function() {
    setTimeout(function() {
        var splash = document.getElementById('splash');
        if (splash) {
            splash.classList.add('hide');
        }
    }, 2500);
});


// ===== NAVBAR SEARCH TOGGLE =====
function toggleSearch(e) {
    e.preventDefault();
    var form = document.getElementById('searchForm');
    var input = document.getElementById('searchInput');
    var isHidden = (form.style.display === 'none' || form.style.display === '');

    if (isHidden) {
        form.style.display = 'inline-flex';
        input.focus();
    } else if (input.value.trim() !== '') {
        form.submit();
    } else {
        form.style.display = 'none';
    }
}


// ===== FILTER BUTTONS — HOMEPAGE =====
const filterBtns = document.querySelectorAll('.ftag');
filterBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
        filterBtns.forEach(function(b) {
            b.classList.remove('active');
        });
        this.classList.add('active');

        const selected = this.textContent.trim();
        const cards = document.querySelectorAll('.products-grid .prod-card');

        cards.forEach(function(card) {
            const category = card.getAttribute('data-category');
            if (selected === 'All') {
                card.style.display = 'block';
            } else if (category === selected) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// ===== FAQ ACCORDION =====
const faqItems = document.querySelectorAll('.faq-item');
faqItems.forEach(function(item) {
    item.addEventListener('click', function() {
        this.classList.toggle('open');
    });
});

// ===== NAVBAR SCROLL EFFECT =====
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    }
});

// ===== PRODUCT DETAIL — IMAGE GALLERY =====
function changeImage(imgName, thumbEl) {
    const mainImg = document.getElementById('mainImg');
    if (mainImg) {
        mainImg.src = mainImg.src.replace(/images\/.*$/, 'images/' + imgName);
    }
    document.querySelectorAll('.thumbnail').forEach(function(t) {
        t.classList.remove('active');
    });
    if (thumbEl) thumbEl.classList.add('active');
}

// ===== PRODUCT DETAIL — QUANTITY =====
function changeQty(change) {
    const qtyEl = document.getElementById('qty');
    if (qtyEl) {
        let qty = parseInt(qtyEl.textContent) + change;
        if (qty < 1) qty = 1;
        qtyEl.textContent = qty;
    }
}

// ===== PRODUCT DETAIL — TABS =====
function showTab(tabName, btn) {
    document.querySelectorAll('.tab-content').forEach(function(t) {
        t.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(function(b) {
        b.classList.remove('active');
    });
    const activeTab = document.getElementById('tab-' + tabName);
    if (activeTab) activeTab.classList.add('active');
    if (btn) btn.classList.add('active');
}

// ===== SHOP PAGE FILTER =====
const filterCheckboxes = document.querySelectorAll('.filter-sidebar input[type="checkbox"]');
filterCheckboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {

        const checkedSkinTypes = [];
        const checkedCategories = [];
        const checkedPrices = [];

        document.querySelectorAll('.filter-group').forEach(function(group) {
            const heading = group.querySelector('h4').textContent.trim();
            group.querySelectorAll('input:checked').forEach(function(cb) {
                const label = cb.parentElement.textContent.trim();
                if (heading === 'Skin Type') checkedSkinTypes.push(label);
                if (heading === 'Category') checkedCategories.push(label);
                if (heading === 'Price Range') checkedPrices.push(label);
            });
        });

        const allCards = document.querySelectorAll('.products-grid-full .prod-card');

        allCards.forEach(function(card) {
            const cardSkin = card.getAttribute('data-skin') || '';
            const cardCategory = card.getAttribute('data-category') || '';
            const cardPriceText = card.querySelector('.prod-price') ?
                card.querySelector('.prod-price').textContent.replace('PKR ', '').replace(',', '').trim() : '0';
            const cardPrice = parseInt(cardPriceText);

            let skinMatch = checkedSkinTypes.length === 0;
            if (!skinMatch) {
                checkedSkinTypes.forEach(function(s) {
                    if (cardSkin.toLowerCase().includes(s.toLowerCase()) ||
                        cardSkin.toLowerCase().includes('all')) {
                        skinMatch = true;
                    }
                });
            }

            let catMatch = checkedCategories.length === 0;
            if (!catMatch) {
                checkedCategories.forEach(function(c) {
                    if (c === 'Cleansers' && cardCategory === 'Cleanser') catMatch = true;
                    if (c === 'Toners' && cardCategory === 'Toner') catMatch = true;
                    if (c === 'Moisturizers' && cardCategory === 'Moisturizer') catMatch = true;
                    if (c === 'Sunscreens' && cardCategory === 'Sunscreen') catMatch = true;
                    if (c === 'Treatments' && (cardCategory === 'Serum' || cardCategory === 'Mask')) catMatch = true;
                });
            }

            let priceMatch = checkedPrices.length === 0;
            if (!priceMatch) {
                checkedPrices.forEach(function(p) {
                    if (p === 'Under PKR 2,000' && cardPrice < 2000) priceMatch = true;
                    if (p === 'PKR 2,000 - 3,000' && cardPrice >= 2000 && cardPrice <= 3000) priceMatch = true;
                    if (p === 'PKR 3,000 - 4,000' && cardPrice > 3000 && cardPrice <= 4000) priceMatch = true;
                    if (p === 'Above PKR 4,000' && cardPrice > 4000) priceMatch = true;
                });
            }

            card.style.display = (skinMatch && catMatch && priceMatch) ? 'block' : 'none';
        });

        const visible = document.querySelectorAll('.products-grid-full .prod-card[style="display: block;"]').length;
        const countEl = document.querySelector('.products-count');
        if (countEl) {
            countEl.textContent = 'Showing ' + visible + ' products';
        }
    });
});

// ===== LOGIN VALIDATION =====
const loginForm = document.querySelector('form[action="/login"]');
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const email = loginForm.querySelector('input[name="email"]');
        const password = loginForm.querySelector('input[name="password"]');
        let valid = true;

        [email, password].forEach(function(field) {
            const existing = field.parentElement.querySelector('.form-alert');
            if (existing) existing.remove();
            field.style.borderColor = '#d8e8d0';
        });

        if (!email.value.trim()) {
            showFieldError(email, 'Please enter your email address!');
            valid = false;
        }
        if (!password.value.trim()) {
            showFieldError(password, 'Please enter your password!');
            valid = false;
        }

        if (valid) {
            alert('Login form is valid! ');
        }
    });
}

// ===== REGISTER VALIDATION =====
const registerForm = document.querySelector('form[action="/register"]');
if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const fullName = registerForm.querySelector('input[name="full_name"]');
        const email = registerForm.querySelector('input[name="email"]');
        const password = registerForm.querySelector('input[name="password"]');
        const confirmPassword = registerForm.querySelector('input[name="confirm_password"]');
        const fields = [fullName, email, password, confirmPassword];
        let valid = true;

        fields.forEach(function(field) {
            const existing = field.parentElement.querySelector('.form-alert');
            if (existing) existing.remove();
            field.style.borderColor = '#d8e8d0';
        });

        fields.forEach(function(field) {
            if (!field.value.trim()) {
                showFieldError(field, 'This field is required!');
                valid = false;
            }
        });

        if (password.value && password.value.length < 6) {
            showFieldError(password, 'Password must be at least 6 characters!');
            valid = false;
        }

        if (password.value && confirmPassword.value && password.value !== confirmPassword.value) {
            showFieldError(confirmPassword, 'Passwords do not match!');
            valid = false;
        }

        if (valid) {
            alert('Registration form is valid! (Backend not connected yet)');
        }
    });
}

// ===== SHARED ERROR DISPLAY =====
function showFieldError(field, message) {
    const alert = document.createElement('div');
    alert.className = 'form-alert';
    alert.textContent = message;
    field.parentElement.appendChild(alert);
    field.style.borderColor = '#c0392b';
} 