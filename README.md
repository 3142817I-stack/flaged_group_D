# flaged_group_D
flag game 

## Getting Started 

This project uses **Python 3.11**. You don’t need to install Django or any
other packages globally – everything lives in a virtual environment.

1. **Install Python 3.11** if you don’t already have it. The `python` or
   `python3` command should point to a 3.11 interpreter.

2. **Make a virtual environment** in the project root and turn it on.
   Use the command that matches your platform/shell:

   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - **macOS/Linux (bash, zsh, etc.):**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

   After activation your prompt should start with `(.venv)`.

3. **Install the required packages:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

   This will pull in Django 2.2.28 and `bcrypt`. The file does **not** list
   Python itself – it can’t be installed by `pip`.

   Now you are ready to start coding.

## Database Setup

After installing the requirements, set up the database and populate it with initial data:

1. **Run database migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Populate the database with dummy data:**

   ```bash
   python manage.py populate_db
   ```

   This command will:
   - Create 23 dummy users with varying scores
   - Create all 195 UN member countries with their continents
   - Countries are ordered alphabetically (Afghanistan = ID 1, Zimbabwe = ID 195)

3. **Create a superuser to access the admin panel:**

   ```bash
   python manage.py createsuperuser
   ```

   Enter a username, email, and password when prompted.

4. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

5. **Access the admin panel:**

   Open your browser and go to: `http://127.0.0.1:8000/admin/`

   Log in with the superuser credentials you created. You'll see:
   - **Users** - View all dummy users with their scores
   - **Flags** - View all 195 UN countries with their continents

---
