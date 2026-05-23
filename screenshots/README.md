# Screenshots Guide

This folder contains placeholders for the screenshots required in the final project documentation.

## Required Screenshots

To compile a complete submission, capture and save the following screenshots into this directory:

### 1. `login_page.png`
- **Description**: Displays the login form with its custom glassmorphism card styling, email and password input fields, and the login button.
- **How to capture**: Start the server (`python app.py`), visit `http://localhost:5000/login` in your web browser, and capture the page view.

### 2. `signup_page.png`
- **Description**: Displays the signup form showing the live password strength meter, password rules checklist, and account registration fields.
- **How to capture**: Navigate to `http://localhost:5000/signup` and take a screenshot of the empty or partially filled registration form.

### 3. `password_strength_meter.png`
- **Description**: Visual demonstration of the password checker. Displays the progress bar filling up and switching colors (from red to green or cyan) as a strong password is typed.
- **How to capture**: Type a strong password like `C0mpl3x!P@ssw0rd` in the signup screen and capture the feedback checklist showing all green ticks.

### 4. `dashboard.png`
- **Description**: Displays the authenticated user dashboard dashboard showcasing the security statistics cards and recent login audits table.
- **How to capture**: Log in with credentials and capture the `http://localhost:5000/dashboard` view.

### 5. `profile_page.png`
- **Description**: Displays the user profile page showing user metadata, detailed history logs, and the password update form.
- **How to capture**: Navigate to `http://localhost:5000/profile` and capture the screen.

### 6. `failed_login.png`
- **Description**: Visual demonstration of brute-force prevention. Shows the account lockout flash warning message after making 5 consecutive invalid login attempts.
- **How to capture**: Try logging in with an incorrect password 5 times in a row. Take a screenshot of the login screen displaying the lockout warning.

### 7. `security_testing.png`
- **Description**: Displays the console execution output of the automated security test suite.
- **How to capture**: Run `python tests/run_all_tests.py` in your terminal and take a screenshot of the terminal displaying the `ALL TESTS PASSED` status message.

### 8. `mongodb_users.png`
- **Description**: Displays the MongoDB user records in MongoDB Compass, confirming passwords are stored as bcrypt hashes instead of plaintext.
- **How to capture**: Open MongoDB Compass, click on the `secure_auth_db` database, select the `users` collection, and capture the documents.

### 9. `mongodb_login_attempts.png`
- **Description**: Displays audit documents inside the `login_attempts` collection.
- **How to capture**: Select the `login_attempts` collection in MongoDB Compass and capture the logs.

---

*Note: For academic submissions, ensure all screenshots are clean, high-resolution, and cropped to show only the web application window or terminal interface.*
