// Main JavaScript file

// Form validation (Bootstrap). Skip AJAX lead forms — they use custom validation + loading UI.
(function() {
    'use strict';

    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        if (form.getAttribute('data-lead-ajax') === 'true') {
            return;
        }
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();

// Smooth scrolling for anchor links - DISABLED to fix auto-scroll issue
// This was causing scrolling on href="#" buttons (modals, dropdowns)
// document.querySelectorAll('a[href^="#"]').forEach(anchor => {
//     anchor.addEventListener('click', function(e) {
//         e.preventDefault();
//         
//         const target = document.querySelector(this.getAttribute('href'));
//         if (target) {
//             target.scrollIntoView({
//                 behavior: 'smooth',
//                 block: 'start'
//             });
//         }
//     });
// });

// Navbar scroll effect - temporarily disabled to test auto-scroll issue
// window.addEventListener('scroll', function() {
//     const navbar = document.querySelector('.navbar');
//     if (window.scrollY > 50) {
//         navbar.classList.add('navbar-scrolled');
//     } else {
//         navbar.classList.remove('navbar-scrolled');
//     }
// });

// Phone number formatting
const phoneInputs = document.querySelectorAll('input[type="tel"]');
phoneInputs.forEach(input => {
    input.addEventListener('input', function(e) {
        let x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
        e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
    });
});

// Loading spinner for forms (not for data-lead-ajax — those manage their own button UI).
document.querySelectorAll('form').forEach(function (form) {
    if (form.getAttribute('data-lead-ajax') === 'true') {
        return;
    }
    form.addEventListener('submit', function () {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (!submitBtn) {
            return;
        }

        if (typeof this.checkValidity === 'function' && !this.checkValidity()) {
            return;
        }

        const requiredFields = this.querySelectorAll('[required]');
        let allValid = true;

        requiredFields.forEach(function (field) {
            const value = (field.value || '').trim();

            if (field.tagName === 'SELECT') {
                if (value === '') allValid = false;
                return;
            }

            if (field.type === 'email') {
                if (value === '' || !field.checkValidity()) allValid = false;
                return;
            }

            if (value === '') allValid = false;
        });

        if (!allValid) {
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    });
});

// Tooltip initialization
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Popover initialization
var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
});

// Counter animation
function animateCounter(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        element.innerHTML = Math.floor(progress * (end - start) + start) + '+';
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Trigger counter animation when element comes into view - temporarily disabled
// const observerOptions = {
//     threshold: 0.5
// };

// const observer = new IntersectionObserver((entries) => {
//     entries.forEach(entry => {
//         if (entry.isIntersecting) {
//             const counters = entry.target.querySelectorAll('.counter');
//             counters.forEach(counter => {
//                 const target = parseInt(counter.getAttribute('data-target'));
//                 animateCounter(counter, 0, target, 2000);
//             });
//             observer.unobserve(entry.target);
//         }
//     });
// }, observerOptions);

// document.querySelectorAll('.stats-section').forEach(section => {
//     observer.observe(section);
// });