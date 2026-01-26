// Utility functions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Update cart count on page load
    updateCartCount();

    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Update cart count
function updateCartCount() {
    fetch('/api/cart-count')
        .then(response => response.json())
        .then(data => {
            const cartCountEl = document.getElementById('cart-count');
            if (cartCountEl) {
                cartCountEl.textContent = data.count;
                if (data.count > 0) {
                    cartCountEl.style.display = 'inline-block';
                } else {
                    cartCountEl.style.display = 'none';
                }
            }
        })
        .catch(error => console.error('Error:', error));
}

// Show notification toast
function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.position-fixed.bottom-0');
    if (!toastContainer) return;

    const toast = document.getElementById('toast');
    const toastBody = toast.querySelector('.toast-body');

    // Update toast content and style
    if (type === 'success') {
        toastBody.innerHTML = '<i class="fas fa-check-circle"></i> ' + message;
        toastBody.className = 'toast-body bg-success text-white';
    } else if (type === 'error') {
        toastBody.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + message;
        toastBody.className = 'toast-body bg-danger text-white';
    } else if (type === 'info') {
        toastBody.innerHTML = '<i class="fas fa-info-circle"></i> ' + message;
        toastBody.className = 'toast-body bg-info text-white';
    }

    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Format currency
function formatCurrency(amount) {
    return '฿' + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Loading spinner
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.role = 'status';
    spinner.innerHTML = '<span class="visually-hidden">Loading...</span>';
    return spinner;
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Number input handler
function handleNumberInput(event) {
    const value = event.target.value;
    if (value && isNaN(value)) {
        event.target.value = '';
    }
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Phone validation (Thai format)
function isValidPhone(phone) {
    const phoneRegex = /^[0-9]{9,10}$/;
    return phoneRegex.test(phone.replace(/[\s\-]/g, ''));
}

// Add active class to current nav link
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Initialize on page load
window.addEventListener('load', setActiveNavLink);

// Export functions for use in templates
window.formatCurrency = formatCurrency;
window.showToast = showToast;
window.isValidEmail = isValidEmail;
window.isValidPhone = isValidPhone;
window.handleNumberInput = handleNumberInput;
