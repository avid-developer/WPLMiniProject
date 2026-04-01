# WPL Mini Project

Diet & Calorie Tracker is a Django-based mini project for the Web Programming Lab. It lets users sign up, log meals, set a daily calorie target, review history, and view a weekly summary.

## Features

- User authentication with signup, login, and logout
- Add, edit, and delete meal entries
- Daily calorie target tracking
- Dashboard with today's progress and a weekly chart
- History page with date filters and client-side search
- Responsive UI styled with Bootstrap and custom CSS
- jQuery-based quick-add interactions and AJAX chart loading

## Tech Stack

- Django
- HTML5 and CSS3
- Bootstrap
- jQuery
- SQLite

## Run Locally

1. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

2. Activate it:

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the server:

   ```bash
   python manage.py runserver
   ```

6. Open `http://127.0.0.1:8000/`

## Lab Concepts Used

- HTML5 forms with date/time and number inputs
- CSS styling and responsive layout
- Bootstrap components and grid system
- jQuery event handling and AJAX
- Python and Django backend logic
- Form processing in Django
- SQLite database integration
