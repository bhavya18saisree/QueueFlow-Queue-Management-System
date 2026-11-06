# QueueFlow – Queue Management System

A web-based Queue Management System developed using Django, Python, MySQL, HTML, CSS, JavaScript, and Bootstrap.

## Project Overview

QueueFlow helps administrators manage multiple queues, generate customer tokens, monitor waiting lists, and manage customer service operations through a centralized dashboard.

## Key Features

- **Manager Dashboard:** View queue statistics and operational insights.
- **Multiple Queue Management:** Create and manage separate queues.
- **Token Generation:** Generate unique tokens for customers.
- **Queue Tracking:** Monitor waiting, serving, served, and cancelled tokens.
- **Queue Operations:** Call the next customer and manage token statuses.
- **Analytics:** View queue statistics and graphical reports.
- **Responsive Interface:** User-friendly interface built with Bootstrap.
- **Secure Configuration:** Environment variables used for sensitive credentials.

## Technologies Used

- Python
- Django
- MySQL
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

## Project Structure

```text
QueueManagement/
│
├── project/
├── queues/
│   └── migrations/
├── templates/
├── static/
│   ├── css/
│   └── js/
├── .gitignore
├── manage.py
└── README.md
```

## Setup Instructions

1. Clone the repository:

   `git clone https://github.com/bhavya18saisree/QueueFlow-Queue-Management-System.git`

2. Navigate to the project folder:

   `cd QueueFlow-Queue-Management-System`

3. Create and activate a virtual environment:

   `python -m venv venv`

4. Install dependencies:

   `pip install -r requirements.txt`

5. Create a `.env` file in the project root and configure:

   - `DJANGO_SECRET_KEY`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`

6. Create the MySQL database named `queue_management_db`.

7. Apply migrations:

   `python manage.py migrate`

8. Start the development server:

   `python manage.py runserver`

9. Open `http://127.0.0.1:8000/` in your browser.

## Security Note

Sensitive credentials are stored in a local `.env` file. The `.env` file is excluded from GitHub using `.gitignore`.

## Author

Developed as a Queue Management System project.