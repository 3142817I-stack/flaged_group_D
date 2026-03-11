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

4. **Start coding!**

   Run Django management commands, run tests, whatever your project needs.

---
