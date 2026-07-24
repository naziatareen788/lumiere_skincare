// ===== HERO IMAGE FALLBACK =====
var heroImg = document.getElementById('heroImg');
if (heroImg) {
    heroImg.addEventListener('error', function() {
        heroImg.parentElement.innerHTML = '<p class="hero-img-fallback">✦ Hero Image Here</p>';
    });
}

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
    var isHidden = form.classList.contains('hidden');

    if (isHidden) {
        form.classList.remove('hidden');
        input.focus();
    } else if (input.value.trim() !== '') {
        form.submit();
    } else {
        form.classList.add('hidden');
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
    const qtyInput = document.getElementById('qtyInput');
    if (qtyEl) {
        let qty = parseInt(qtyEl.textContent) + change;
        if (qty < 1) qty = 1;
        qtyEl.textContent = qty;
        if (qtyInput) qtyInput.value = qty;
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

// ===== AUTO FILTER ON PAGE LOAD =====
window.addEventListener('DOMContentLoaded', function() {

    var productsPage = document.getElementById('productsPage');
    var catParam = productsPage ? productsPage.dataset.category : 'all';
    var skinParam = productsPage ? productsPage.dataset.skinType : 'all';

    var titleEl = document.getElementById('pageTitle');
    if (titleEl) {
        if (catParam !== 'all') {
            titleEl.textContent = catParam;
        } else if (skinParam !== 'all') {
            titleEl.textContent = skinParam + ' Type';
        } else {
            titleEl.textContent = 'All Products';
        }
    }

    var cards = document.querySelectorAll('.products-grid-full .prod-card');
    if (cards.length === 0) return;

    if (catParam === 'all' && skinParam === 'all') return;

    cards.forEach(function(card) {
        var cardCat = card.getAttribute('data-category') || '';
        var cardSkin = card.getAttribute('data-skin') || '';
        var show = false;

        if (catParam !== 'all') {
            var catLower = catParam.toLowerCase();
            var cardCatLower = cardCat.toLowerCase();

            if (catLower === 'cleansers' && cardCatLower === 'cleanser') show = true;
            else if (catLower === 'toners' && cardCatLower === 'toner') show = true;
            else if (catLower === 'serums' && cardCatLower === 'serum') show = true;
            else if (catLower === 'moisturizers' && cardCatLower === 'moisturizer') show = true;
            else if (catLower === 'sunscreens' && cardCatLower === 'sunscreen') show = true;
            else if (catLower === 'treatments' && (cardCatLower === 'mask' || cardCatLower === 'serum' || cardCatLower === 'toner')) show = true;
        }

        if (skinParam !== 'all') {
            var skinLower = skinParam.toLowerCase();
            var cardSkinLower = cardSkin.toLowerCase();
            show = cardSkinLower.includes(skinLower) || cardSkinLower.includes('all');
        }

        card.style.display = show ? 'block' : 'none';
    });

    var countEl = document.querySelector('.products-count');
    if (countEl) {
        var visible = document.querySelectorAll('.products-grid-full .prod-card[style="display: block;"]').length;
        countEl.textContent = 'Showing ' + visible + ' products';
    }
});

// ===== SEARCH FILTER — SHOP PAGE =====
window.addEventListener('load', function () {
    var productsPage = document.getElementById('productsPage');
    var searchDisplay = productsPage ? productsPage.dataset.search : '';
    var searchVal = searchDisplay ? searchDisplay.toLowerCase() : '';

    if (!searchVal) return;

    var cards = document.querySelectorAll('.prod-card');
    var visibleCount = 0;

    cards.forEach(function (card) {
        var nameEl = card.querySelector('.prod-name');
        var name = nameEl ? nameEl.textContent.toLowerCase() : '';
        var matches = name.indexOf(searchVal) !== -1;

        if (!matches) {
            card.style.display = 'none';
        } else if (card.style.display !== 'none') {
            visibleCount++;
        }
    });

    var titleEl = document.getElementById('pageTitle');
    if (titleEl) {
        titleEl.textContent = 'Search results for "' + searchDisplay + '"';
    }

    var countEl = document.querySelector('.products-count');
    if (countEl) {
        countEl.textContent = 'Showing ' + visibleCount + ' result' + (visibleCount === 1 ? '' : 's');
    }

    if (visibleCount === 0) {
        var grid = document.querySelector('.products-grid-full');
        if (grid) {
            grid.innerHTML = '<p class="search-empty">No products found matching "' + searchDisplay + '". Try a different keyword.</p>';
        }
    }
});

// ===== CHECKOUT — PAYMENT SELECTION =====
function selectPayment(type) {
    document.getElementById('cod-option').classList.remove('active');
    document.getElementById('online-option').classList.remove('active');
    document.getElementById('onlineTransferBox').classList.add('hidden');

    if (type === 'cod') {
        document.getElementById('cod-option').classList.add('active');
        document.querySelector('input[value="cod"]').checked = true;
    } else {
        document.getElementById('online-option').classList.add('active');
        document.querySelector('input[value="online"]').checked = true;
        document.getElementById('onlineTransferBox').classList.remove('hidden');
    }
}

// ===== CHECKOUT — FORM VALIDATION =====
function validateCheckout() {
    const fields = [
        { id: 'full_name', msg: 'Please enter your full name!' },
        { id: 'email', msg: 'Please enter your email address!' },
        { id: 'phone', msg: 'Please enter your phone number!' },
        { id: 'address', msg: 'Please enter your delivery address!' },
        { id: 'city', msg: 'Please enter your city!' }
    ];

    let valid = true;

    fields.forEach(function(field) {
        const el = document.getElementById(field.id);
        const existing = el.parentElement.querySelector('.form-alert');
        if (existing) existing.remove();
        el.style.borderColor = '#d8e8d0';

        if (!el.value.trim()) {
            const alert = document.createElement('div');
            alert.className = 'form-alert error';
            alert.textContent = field.msg;
            el.parentElement.appendChild(alert);
            el.style.borderColor = '#c0392b';
            valid = false;
        }
    });

    const phone = document.getElementById('phone');
    if (phone && phone.value.trim() && !/^[0-9\-\+]{10,13}$/.test(phone.value.trim())) {
        const existing = phone.parentElement.querySelector('.form-alert');
        if (existing) existing.remove();
        const alert = document.createElement('div');
        alert.className = 'form-alert error';
        alert.textContent = 'Please enter a valid phone number!';
        phone.parentElement.appendChild(alert);
        phone.style.borderColor = '#c0392b';
        valid = false;
    }

    if (valid) {
        document.getElementById('checkoutForm').submit();
    }
}

// ===== QUIZ — STEP NAVIGATION =====
function nextStep(current) {
    if (current === 1) {
        const name = document.getElementById('user_name');
        if (name && !name.value.trim()) {
            alert('Please enter your name!');
            return;
        }
    }

    if (current === 2) {
        const skinType = document.querySelector('input[name="skin_type"]:checked');
        if (!skinType) {
            alert('Please select your skin type!');
            return;
        }
    }

    document.getElementById('step' + current).classList.remove('active');
    document.getElementById('step' + (current + 1)).classList.add('active');
}

function prevStep(current) {
    document.getElementById('step' + current).classList.remove('active');
    document.getElementById('step' + (current - 1)).classList.add('active');
}

// ===== QUIZ — MAX 3 CONCERNS =====
var concernCheckboxes = document.querySelectorAll('input[name="concerns"]');
if (concernCheckboxes.length > 0) {
    concernCheckboxes.forEach(function(cb) {
        cb.addEventListener('change', function() {
            const checked = document.querySelectorAll('input[name="concerns"]:checked');
            if (checked.length > 3) {
                this.checked = false;
                alert('You can select maximum 3 concerns!');
            }
        });
    });

    var quizForm = document.getElementById('quizForm');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            const checked = document.querySelectorAll('input[name="concerns"]:checked');
            if (checked.length === 0) {
                e.preventDefault();
                alert('Please select at least 1 skin concern!');
            }
        });
    }
}

// ===== NEWSLETTER SUBSCRIBE =====
const newsletterForm = document.querySelector('.newsletter-form form');
const subscribeInput = document.querySelector('.newsletter-form input');

if (newsletterForm && subscribeInput) {
    newsletterForm.addEventListener('submit', function(e) {
        const email = subscribeInput.value.trim();

        if (email === '') {
            e.preventDefault();
            showAlert(subscribeInput, 'Please enter your email address!', 'error');
        } else if (!isValidEmail(email)) {
            e.preventDefault();
            showAlert(subscribeInput, 'Please enter a valid email address!', 'error');
        }
    });
}

// ===== CONTACT FORM =====
const contactForm = document.querySelector('.contact-form-box form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        const fields = contactForm.querySelectorAll('input, textarea');
        let valid = true;

        fields.forEach(function(field) {
            if (field.value.trim() === '') {
                showAlert(field, 'This field is required!', 'error');
                valid = false;
            } else if (field.type === 'email' && !isValidEmail(field.value.trim())) {
                showAlert(field, 'Please enter a valid email!', 'error');
                valid = false;
            } else {
                clearAlert(field);
            }
        });

        if (!valid) {
            e.preventDefault();
        }
    });
}

// ===== REVIEW FORM =====
// const reviewBtn = document.querySelector('.write-review .btn-dark');
// if (reviewBtn) {
   // reviewBtn.addEventListener('click', function() {
     //   const nameField = document.querySelector('.write-review input[type="text"]');
//        const reviewField = document.querySelector('.write-review textarea');
//        let valid = true;
//
//        if (nameField && nameField.value.trim() === '') {
//            showAlert(nameField, 'Please enter your name!', 'error');
//            valid = false;
//        } else if (nameField) {
//            clearAlert(nameField);
//        }
//        if (reviewField && reviewField.value.trim() === '') {
//            showAlert(reviewField, 'Please write your review!', 'error');
//            valid = false;
//        } else if (reviewField) {
//            clearAlert(reviewField);
//        }
//        if (valid) {
//            if (nameField) nameField.value = '';
//            if (reviewField) reviewField.value = '';
//            reviewBtn.textContent = '✓ Review Submitted!';
//            reviewBtn.style.background = '#4a6a40';
//            setTimeout(function() {
//                reviewBtn.textContent = 'Submit Review';
//                reviewBtn.style.background = '#2d4a2d';
//            }, 3000);
//        }
//    });
//}

// ===== HELPER FUNCTIONS =====
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showAlert(field, message, type) {
    clearAlert(field);
    const alert = document.createElement('div');
    alert.className = 'form-alert ' + type;
    alert.textContent = message;
    field.parentElement.appendChild(alert);
    field.style.borderColor = type === 'error' ? '#c0392b' : '#2d4a2d';
}

function clearAlert(field) {
    const existing = field.parentElement.querySelector('.form-alert');
    if (existing) existing.remove();
    field.style.borderColor = '#d8e8d0';
}

// ===== LOGIN VALIDATION =====
const loginForm = document.querySelector('form[action="/login"]');
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
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

        if (!valid) {
            e.preventDefault();
        }
    });
}

// ===== REGISTER VALIDATION =====
const registerForm = document.querySelector('form[action="/register"]');
if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
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

        if (!valid) {
            e.preventDefault();
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

// ===== ADMIN DELETE CONFIRM MODALS =====
function initDeleteModal(triggerSelector, overlayId, nameElId, confirmBtnId, cancelBtnId) {
    var overlay = document.getElementById(overlayId);
    if (!overlay) return;

    var nameEl = document.getElementById(nameElId);
    var confirmBtn = document.getElementById(confirmBtnId);
    var cancelBtn = document.getElementById(cancelBtnId);
    var pendingForm = null;

    function closeModal() {
        overlay.classList.remove('active');
        pendingForm = null;
    }

    document.querySelectorAll(triggerSelector).forEach(function(btn) {
        btn.addEventListener('click', function() {
            pendingForm = btn.closest('form');
            nameEl.textContent = btn.dataset.name;
            overlay.classList.add('active');
        });
    });

    confirmBtn.addEventListener('click', function() {
        if (pendingForm) pendingForm.submit();
    });

    cancelBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', function(e) {
        if (e.target === overlay) closeModal();
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });
}

initDeleteModal('.js-delete-user', 'deleteModal', 'deleteModalName', 'deleteModalConfirm', 'deleteModalCancel');
initDeleteModal('.js-delete-product', 'deleteProductModal', 'deleteProductModalName', 'deleteProductModalConfirm', 'deleteProductModalCancel');