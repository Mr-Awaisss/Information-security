/**
 * SECUREAUTH — FRONTEND INTERACTION AND SECURITY ENGINE
 */

document.addEventListener("DOMContentLoaded", function() {
    // 1. PAGE LOAD EFFECTS
    document.body.classList.add("loaded");

    // 2. NAVBAR SCROLL EFFECT
    const navbar = document.getElementById("main-navbar");
    if (navbar) {
        window.addEventListener("scroll", function() {
            if (window.scrollY > 20) {
                navbar.classList.add("scrolled");
            } else {
                navbar.classList.remove("scrolled");
            }
        });
    }

    // 3. AUTO-DISMISS FLASH MESSAGES
    const flashMessages = document.querySelectorAll("[id^='flash-']");
    flashMessages.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            // Add fade class and transition out
            alert.style.transition = "opacity 0.6s ease, transform 0.6s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(function() {
                bsAlert.close();
            }, 600);
        }, 5000); // Trigger after 5 seconds
    });

    // 4. PASSWORD VISIBILITY TOGGLE
    const toggleButtons = document.querySelectorAll(".btn-toggle-password");
    toggleButtons.forEach(function(btn) {
        btn.addEventListener("click", function() {
            const targetId = btn.getAttribute("data-target");
            const inputField = document.getElementById(targetId);
            const icon = btn.querySelector("i");
            
            if (inputField && icon) {
                if (inputField.type === "password") {
                    inputField.type = "text";
                    icon.classList.remove("bi-eye");
                    icon.classList.add("bi-eye-slash");
                } else {
                    inputField.type = "password";
                    icon.classList.remove("bi-eye-slash");
                    icon.classList.add("bi-eye");
                }
            }
        });
    });

    // 5. STRENGTH METER AND PASSWORD RULES CHECKER
    const passwordInput = document.getElementById("password") || document.getElementById("new_password");
    const strengthFill = document.getElementById("strength-bar-fill");
    const strengthText = document.getElementById("strength-text");
    const checklist = document.getElementById("password-checklist");

    if (passwordInput && strengthFill && strengthText) {
        passwordInput.addEventListener("input", function() {
            const val = passwordInput.value;
            const metrics = checkPasswordStrength(val);
            
            // Update Fill Bar Width and Color Class
            strengthFill.style.width = metrics.percent + "%";
            strengthFill.className = "strength-bar-fill"; // Reset
            
            if (metrics.score > 0) {
                strengthFill.classList.add(metrics.colorClass);
            }
            
            // Update text label
            strengthText.textContent = `Strength: ${metrics.label}`;
            
            // Update Requirements Checklist visually if present
            if (checklist) {
                updateChecklistItem("length", metrics.checks.length);
                updateChecklistItem("uppercase", metrics.checks.uppercase);
                updateChecklistItem("lowercase", metrics.checks.lowercase);
                updateChecklistItem("digit", metrics.checks.digit);
                updateChecklistItem("special", metrics.checks.special);
            }
        });
    }

    // Helper functions for password scoring
    function checkPasswordStrength(pwd) {
        const checks = {
            length: pwd.length >= 8,
            uppercase: /[A-Z]/.test(pwd),
            lowercase: /[a-z]/.test(pwd),
            digit: /\d/.test(pwd),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(pwd)
        };
        
        // Calculate raw score based on completed criteria
        let score = 0;
        if (pwd.length > 0) {
            if (checks.length) score++;
            if (checks.uppercase) score++;
            if (checks.lowercase) score++;
            if (checks.digit) score++;
            if (checks.special) score++;
            
            // Bonus points for longer passwords
            if (pwd.length >= 12 && score >= 4) {
                score = 5;
            }
        }
        
        let label = "Empty";
        let colorClass = "";
        let percent = 0;
        
        switch(score) {
            case 0:
                label = "Empty";
                colorClass = "";
                percent = 0;
                break;
            case 1:
                label = "Weak (Critical)";
                colorClass = "strength-weak";
                percent = 20;
                break;
            case 2:
                label = "Fair (Insecure)";
                colorClass = "strength-fair";
                percent = 40;
                break;
            case 3:
                label = "Good (Medium)";
                colorClass = "strength-good";
                percent = 60;
                break;
            case 4:
                label = "Strong (Secure)";
                colorClass = "strength-strong";
                percent = 80;
                break;
            case 5:
                label = "Very Strong (Maximum)";
                colorClass = "strength-very-strong";
                percent = 100;
                break;
        }
        
        return { score, label, colorClass, percent, checks };
    }

    function updateChecklistItem(requirement, isValid) {
        const item = document.querySelector(`[data-requirement="${requirement}"]`);
        if (item) {
            const icon = item.querySelector(".checklist-icon");
            if (isValid) {
                item.classList.remove("invalid");
                item.classList.add("valid");
                if (icon) {
                    icon.className = "bi bi-check-circle-fill checklist-icon";
                }
            } else {
                item.classList.remove("valid");
                item.classList.add("invalid");
                if (icon) {
                    icon.className = "bi bi-x-circle-fill checklist-icon";
                }
            }
        }
    }

    // 6. CONFIRM PASSWORD MATCH DETECTOR
    const confirmInput = document.getElementById("confirm_password");
    const matchIndicator = document.getElementById("password-match-indicator");
    
    if (passwordInput && confirmInput && matchIndicator) {
        confirmInput.addEventListener("input", checkMatch);
        passwordInput.addEventListener("input", checkMatch);
    }
    
    function checkMatch() {
        if (!confirmInput || !passwordInput || !matchIndicator) return;
        const pwd = passwordInput.value;
        const conf = confirmInput.value;
        
        if (conf.length === 0) {
            matchIndicator.classList.add("d-none");
            return;
        }
        
        matchIndicator.classList.remove("d-none");
        const icon = matchIndicator.querySelector("i");
        const text = matchIndicator.querySelector("span");
        
        if (pwd === conf) {
            matchIndicator.className = "password-match-indicator match";
            icon.className = "bi bi-patch-check-fill";
            text.textContent = "Passwords match successfully.";
        } else {
            matchIndicator.className = "password-match-indicator mismatch";
            icon.className = "bi bi-patch-exclamation-fill";
            text.textContent = "Passwords do not match.";
        }
    }

    // 7. FORM SUBMISSION LOADING INDICATORS
    const forms = document.querySelectorAll("form");
    forms.forEach(function(form) {
        form.addEventListener("submit", function(e) {
            const submitBtn = form.querySelector(".btn-submit");
            if (submitBtn) {
                const textSpan = submitBtn.querySelector(".btn-text");
                const loaderSpan = submitBtn.querySelector(".btn-loader");
                const arrowIcon = submitBtn.querySelector(".btn-arrow");
                
                if (textSpan && loaderSpan) {
                    // Only display loader if HTML5 validation passes
                    if (form.checkValidity()) {
                        textSpan.classList.add("d-none");
                        loaderSpan.classList.remove("d-none");
                        if (arrowIcon) arrowIcon.classList.add("d-none");
                        submitBtn.disabled = true;
                    }
                }
            }
        });
    });

    // 8. DASHBOARD COUNT-UP STAT ANIMATION
    const statsValue = document.querySelectorAll(".stat-value");
    statsValue.forEach(function(el) {
        const valStr = el.textContent.trim();
        // Only run count-up for numbers (e.g. not Last Login datetime values)
        if (!isNaN(valStr) && valStr.length > 0) {
            const targetVal = parseInt(valStr);
            if (targetVal > 0) {
                animateCounter(el, 0, targetVal, 1000);
            }
        }
    });

    function animateCounter(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                element.textContent = end;
            }
        };
        window.requestAnimationFrame(step);
    }
});
