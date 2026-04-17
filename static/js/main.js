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

function resetPublicLeadSubmitButton(btn) {
    if (!btn || !btn.dataset.originalHtml) {
        return;
    }
    btn.disabled = false;
    btn.innerHTML = btn.dataset.originalHtml;
    delete btn.dataset.originalHtml;
    delete btn.dataset.leadSubmitting;
}

function showAjaxFormMessage(form, message, isSuccess) {
    if (!form) {
        return;
    }
    var holder = form.querySelector('[data-form-feedback]');
    if (!holder) {
        holder = document.createElement('div');
        holder.setAttribute('data-form-feedback', '1');
        holder.className = 'alert mt-3';
        form.appendChild(holder);
    }
    holder.classList.remove('alert-success', 'alert-danger', 'd-none');
    holder.classList.add(isSuccess ? 'alert-success' : 'alert-danger');
    holder.textContent = message || (isSuccess ? 'Submitted successfully.' : 'Something went wrong. Please try again.');
}

function clearAjaxValidation(form) {
    form.querySelectorAll('.is-invalid').forEach(function (field) {
        field.classList.remove('is-invalid');
    });
}

function applyAjaxValidationErrors(form, errors) {
    if (!errors) {
        return;
    }
    Object.keys(errors).forEach(function (name) {
        var field = form.querySelector('[name="' + name + '"]');
        if (!field) {
            return;
        }
        field.classList.add('is-invalid');
    });
}

document.querySelectorAll('form[data-lead-ajax="true"]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        var submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn || submitBtn.dataset.leadSubmitting === '1') {
            return;
        }

        clearAjaxValidation(form);
        submitBtn.dataset.leadSubmitting = '1';
        submitBtn.dataset.originalHtml = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML =
            '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Sending...';

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(function (response) {
                return response.json().then(function (payload) {
                    return { ok: response.ok, payload: payload };
                });
            })
            .then(function (result) {
                if (result.ok && result.payload && result.payload.ok) {
                    showAjaxFormMessage(form, result.payload.message, true);
                    if (result.payload.redirect_url) {
                        window.location.assign(result.payload.redirect_url);
                    }
                    return;
                }
                applyAjaxValidationErrors(form, result.payload ? result.payload.errors : null);
                showAjaxFormMessage(form, (result.payload && result.payload.message) || 'Please correct the form and try again.', false);
            })
            .catch(function () {
                showAjaxFormMessage(form, 'Network error while submitting. Please try again.', false);
            })
            .finally(function () {
                resetPublicLeadSubmitButton(submitBtn);
            });
    });
});

// Public quote forms: fast feedback, no double-submit, recover if navigation never happens.
document.querySelectorAll('form.public-lead-form').forEach(function (form) {
    if (form.getAttribute('data-lead-ajax') === 'true') {
        return;
    }
    form.addEventListener('submit', function (event) {
        if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
            return;
        }
        var submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) {
            return;
        }
        if (submitBtn.dataset.leadSubmitting === '1') {
            event.preventDefault();
            return;
        }
        submitBtn.dataset.leadSubmitting = '1';
        submitBtn.dataset.originalHtml = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML =
            '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Sending…';
        window.setTimeout(function () {
            resetPublicLeadSubmitButton(submitBtn);
        }, 45000);
    });
});

// BF cache / back button: restore stuck submit buttons
window.addEventListener('pageshow', function (event) {
    if (!event.persisted) {
        return;
    }
    document.querySelectorAll('form.public-lead-form button[type="submit"]').forEach(resetPublicLeadSubmitButton);
});

// Other forms (not public lead, not ajax): light loading state with safety timeout
document.querySelectorAll('form').forEach(function (form) {
    if (form.getAttribute('data-lead-ajax') === 'true' || form.classList.contains('public-lead-form')) {
        return;
    }
    form.addEventListener('submit', function () {
        var submitBtn = this.querySelector('button[type="submit"]');
        if (!submitBtn) {
            return;
        }

        if (typeof this.checkValidity === 'function' && !this.checkValidity()) {
            return;
        }

        var requiredFields = this.querySelectorAll('[required]');
        var allValid = true;

        requiredFields.forEach(function (field) {
            var value = (field.value || '').trim();

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

        if (submitBtn.dataset.originalHtml) {
            return;
        }
        submitBtn.dataset.originalHtml = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML =
            '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing…';
        window.setTimeout(function () {
            resetPublicLeadSubmitButton(submitBtn);
        }, 45000);
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