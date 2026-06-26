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
            alert('Login form is valid! (Backend not connected yet)');
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