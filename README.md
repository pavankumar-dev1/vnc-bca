# VNC BCA College Website — Content Management System

A Flask-based content management system for the Department of Computer Applications (BCA), Vijayanagara College. Public-facing content is stored in a database and managed through a password-protected administration dashboard.

## Highlights

- Admin dashboard with create, edit and delete workflows for website content.
- Content modules for homepage sections, faculty, events, notices, college information, contact details, gallery and website settings.
- SQLAlchemy models with a relational database.
- Form validation and CSRF protection.
- Image and PDF uploads with file validation and generated filenames.
- Seed and legacy-data migration utilities.
- Notice expiry, PDF previews, database backup, SEO settings and global search.
- CSV import/export for supported content modules.
- Optional PWA support and event calendar.

## Technology

- Python
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- Flask-WTF
- SQLite (default local database)

## Project structure

```text
app/
  routes/          Public and admin routes
  __init__.py      Application setup
  models.py        Database models
  forms.py         Forms and validation
  seed.py          Initial content seeding
  migrate_legacy.py
static/
  css/
  images/
  uploads/
templates/
  admin/
  errors/
config.py
run.py
requirements.txt
Procfile
runtime.txt
.env.example
```

## Local setup

**Prerequisites:** Python 3.11 or later.

1. Clone the repository:

   ```bash
   git clone https://github.com/pavankumar-dev1/vnc-bca.git
   cd vnc-bca
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # macOS / Linux
   source .venv/bin/activate
   ```

3. Create a local environment file from the example and configure a unique secret key:

   ```bash
   # Windows PowerShell
   Copy-Item .env.example .env
   # macOS / Linux
   cp .env.example .env
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   Put the generated value in `.env` as `SECRET_KEY`. Review the other settings in `.env.example` before deployment.

4. Install dependencies and run:

   ```bash
   pip install -r requirements.txt
   python run.py
   ```

5. Visit http://127.0.0.1:5000.

## Create the first administrator

The application does **not** create a default administrator account. From a trusted terminal in the project directory, run:

```bash
flask --app run create-admin
```

Follow the prompts to choose a username, role and strong unique password. The password is stored as a hash. Create the account before opening the admin login to the public.

## Important deployment security

- Never deploy with a known or shared administrator password.
- Set a strong, unique `SECRET_KEY` in the deployment environment. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"`.
- Enable secure cookies when serving over HTTPS.
- Keep `.env`, database files, uploaded private data and secrets out of version control.
- Use HTTPS and maintain backups of the production database and uploads.
- If an earlier deployment used the old default administrator credentials, log in from a trusted environment and change or replace that account immediately. This code change does not remove existing accounts from an already-created database.

## Responsible use

This project is intended for the college website and authorized administration. Only upload content and personal information that you are permitted to manage.

## Author

**Pavan Kumar** · [GitHub](https://github.com/pavankumar-dev1) · [LinkedIn](https://www.linkedin.com/in/cyberpavankumar)
