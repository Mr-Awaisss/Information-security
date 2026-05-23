# Presentation: Secure Password Hashing and Authentication Mechanisms
### Project Viva Presentation Outline

This document outlines the structure, slides, and talking points for the university project viva/presentation.

---

## Slide Outline

### Slide 1: Title & Overview
*   **Title**: Secure Password Hashing and Authentication Mechanisms
*   **Sub-title**: Designing a Defense-in-Depth Authentication Infrastructure
*   **Details**: Presented by [Student Name] | Capstone Project Viva | May 2026
*   **Talking Points**:
    *   Introduce yourself and state the purpose of the project.
    *   Explain that this project focuses on implementing security best practices across web applications, specifically focusing on password storage, brute-force defenses, input sanitization, and session safety.

### Slide 2: Introduction & Motivation
*   **Title**: The Importance of Authentication Security
*   **Key Points**:
    *   Identity validation is the first line of defense for web systems.
    *   Credential theft remains the leading attack vector in data breaches (81% of breaches involve compromised credentials).
    *   Major security incidents (e.g., Yahoo, LinkedIn, RockYou) highlight the catastrophic failures resulting from weak or unsalted hashing algorithms.
*   **Talking Points**:
    *   Why are we still talking about password security? Because passwords are still the primary credential type used worldwide.
    *   Weak storage mechanisms make system compromise simple once an attacker gains read access to the database.

### Slide 3: Problem Statement
*   **Title**: Vulnerabilities in Legacy Systems
*   **Key Points**:
    *   **Insecure Password Storage**: Plaintext storage or fast cryptographic hashing (MD5, SHA-256) without salts.
    *   **Lack of Lockout Policies**: Susceptibility to rapid brute-force dictionary attacks.
    *   **NoSQL Injection Vulnerabilities**: Malicious payloads in query parameters bypassing standard authentication checks.
    *   **Session Hijacking**: Insecure cookie configurations permitting token interception.
*   **Talking Points**:
    *   Explain how fast cryptographic algorithms allow attackers to calculate billions of guesses per second using GPUs.
    *   Point out the risk of NoSQL injection where attackers submit structured data to bypass login screens.

### Slide 4: Project Objectives
*   **Title**: Core Technical Goals
*   **Key Points**:
    *   Develop a secure, modular Flask web application with MongoDB.
    *   Implement adaptive password hashing using **bcrypt** with tunable work factors.
    *   Establish server-side and client-side password strength validation.
    *   Create active brute-force protections (limiters and temporal account lockouts).
    *   Mitigate NoSQL injection using robust query sanitization.
    *   Verify all security implementations through an automated test suite.
*   **Talking Points**:
    *   These objectives outline a layered, defense-in-depth approach.
    *   Each layer addresses one or more vulnerabilities listed in the problem statement.

### Slide 5: Literature Review — Hashing Evaluation
*   **Title**: Evaluation of Hashing Architectures
*   **Key Points**:
    *   MD5/SHA-1: Obsolete and vulnerable to collisions.
    *   SHA-256: Excellent for integrity checking, but too fast for password hashing (susceptible to GPU cracking).
    *   bcrypt: Adaptive work factor, built-in salting, Blowfish-based, resistant to hardware acceleration.
    *   Argon2: Memory-hard, excellent ASIC resistance, but higher implementation complexity.
*   **Talking Points**:
    *   Explain why bcrypt is chosen: its workload scales exponentially with the cost factor ($2^{\text{cost}}$).
    *   Describe the necessity of salting to defeat rainbow table attacks.

### Slide 6: Proposed Methodology
*   **Title**: Authentication Flow Chart
*   **Key Points**:
    *   Client request $\rightarrow$ Input Sanitization $\rightarrow$ Lockout Validation $\rightarrow$ Bcrypt Check $\rightarrow$ Session Initiation.
    *   Automated logging of security events (success, failure, lockout).
    *   Temporal lockout enforcement at 5 failed attempts.
*   **Talking Points**:
    *   Explain the user lifecycle from inputs to database checks.
    *   Highlight that checking the lockout status occurs *before* conducting the resource-intensive bcrypt verification to save server resources.

### Slide 7: System Architecture
*   **Title**: Three-Tier Security Architecture
*   **Key Points**:
    *   **Presentation Layer**: Bootstrap 5, glassmorphism UI, client-side validation, password strength progress bar.
    *   **Application Layer**: Flask application factory, Flask-Login session management, Flask-WTF CSRF tokens.
    *   **Security Layer**: Bcrypt utility, brute-force state machine, NoSQL sanitization filters.
    *   **Database Layer**: MongoDB collections (`users`, `login_attempts`, `security_logs`).
*   **Talking Points**:
    *   Discuss how the system separates concerns so that security utilities can be verified independently.
    *   Show how database logs provide audit trails for forensic analysis.

### Slide 8: Password Hashing Implementation
*   **Title**: Bcrypt Hashing in Action
*   **Key Points**:
    *   Bcrypt cost factor set to `12` (adds ~250ms processing delay).
    *   Random salt automatically generated per user password.
    *   Code implementation details: `bcrypt.hashpw` and `bcrypt.checkpw`.
*   **Talking Points**:
    *   Explain how the 250ms delay is imperceptible to a single user but makes automated attacks (requiring millions of tries) computationally impossible.
    *   Acknowledge that password salts do not need to be secret; they just need to be unique to prevent bulk precomputation.

### Slide 9: Brute-Force & Lockout Defenses
*   **Title**: Dynamic Lockout State Machine
*   **Key Points**:
    *   Tracking failed login attempts per user account.
    *   Temporal Lockout: Account is locked for 15 minutes after 5 consecutive failures.
    *   Endpoint Rate-Limiting: Limit of 5 logins per minute per IP using Flask-Limiter.
*   **Talking Points**:
    *   Explain the difference between application-level lockout (locking the account username) and network-level rate limiting (limiting the IP address).
    *   This prevents distributed attacks targeting a single account and single-IP dictionary sweeps.

### Slide 10: NoSQL Injection & Sanitization
*   **Title**: Preventing Query Injection Attacks
*   **Key Points**:
    *   Attackers use JSON objects like `{"$gt": ""}` to bypass authentication.
    *   **Defensive Strategy**: Recursive sanitization utility `sanitize_input` that strips key identifiers starting with `$`.
    *   Enforces casting string inputs and regex validation for structured fields (emails, usernames).
*   **Talking Points**:
    *   Demonstrate how without sanitization, passing raw dictionary payloads to MongoDB filters leads to authentication bypass.
    *   Explain the recursive sanitization algorithm implemented in this project.

### Slide 11: Session Management & CSRF Protection
*   **Title**: Session Security Controls
*   **Key Points**:
    *   Cryptographically signed session cookies.
    *   Enforcement of `HttpOnly`, `SameSite=Lax`, and `Secure` (in production) flags.
    *   Session lifetime limited to 30 minutes.
    *   Synchronizer Token Pattern for CSRF protection on forms.
*   **Talking Points**:
    *   Explain the role of cookie flags: `HttpOnly` blocks XSS read access; `SameSite=Lax` mitigates cross-site cookie attachment.
    *   Explain how CSRF tokens prevent unauthorized form submissions from external sites.

### Slide 12: Frontend Design & UX
*   **Title**: Modern Cybersecurity UI
*   **Key Points**:
    *   Dark, cyber-themed design with neon gradients and glassmorphism.
    *   Real-time password complexity checklist.
    *   Dynamic progress bar for password strength indication.
    *   Responsive layouts for mobile, tablet, and desktop screens.
*   **Talking Points**:
    *   Showcase how a clean, informative UI improves security compliance by encouraging users to choose stronger passwords.
    *   Mention the instant feedback checklist for password requirements.

### Slide 13: Security Testing & Validation
*   **Title**: Automated Security Test Suite
*   **Key Points**:
    *   Complete testing coverage using **pytest**.
    *   Tests covering: hashing logic, lockout execution, session flags, NoSQL injection, and authentication flows.
    *   Harness script `tests/run_all_tests.py` for automated verification.
*   **Talking Points**:
    *   Discuss the importance of test automation in security.
    *   The test suite uses a dedicated, isolated test database (`secure_auth_test_db`) that teardowns itself after test completion.

### Slide 14: Security Analysis & Results
*   **Title**: Defense-in-Depth Analysis
*   **Key Points**:
    *   Tests confirm successful password hash generation and verification.
    *   Automated attempts past the lockout limit successfully trigger lockout warnings.
    *   Injection queries are neutralized before database transmission.
    *   System performs robustly under validation criteria.
*   **Talking Points**:
    *   Analyze how the security controls work together.
    *   The project meets all academic requirements and passes every functional security check.

### Slide 15: Conclusion & Future Work
*   **Title**: Project Summary & Roadmap
*   **Key Points**:
    *   Successfully created a secure, modern, and production-quality authentication platform.
    *   **Future Enhancements**:
        *   Multi-Factor Authentication (MFA) via TOTP.
        *   OAuth 2.0 Integration.
        *   JWT support for APIs.
        *   Password breach checking via HaveIBeenPwned API.
    *   Questions & Comments?
*   **Talking Points**:
    *   Summarize key achievements.
    *   Open the floor for questions from the examination panel.
