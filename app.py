from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
import re  # for simple input validation (allowed characters)

DB_NAME = "todo.db"

app = Flask(__name__)


def get_db_connection():
    """
    CENTRAL DB FUNCTION
    Uses sqlite3 and returns rows as dictionaries.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the tasks table if it does not exist.
    """
    if not Path(DB_NAME).exists():
        conn = get_db_connection()
        conn.execute("""
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                is_done INTEGER NOT NULL DEFAULT 0
            );
        """)
        conn.commit()
        conn.close()


def is_valid_title(title: str) -> bool:
    """
    BASIC SECURITY: input validation for task titles.

    - Not empty
    - Max length 200
    - Only allows letters, numbers, spaces and basic punctuation
      (you can change this rule if you want).
    """
    if not title:
        return False

    if len(title) > 200:
        return False

    # Allowed: letters, numbers, spaces, . , ! ? - _
    pattern = r"^[a-zA-Z0-9 .,!?_-]+$"
    if not re.match(pattern, title):
        return False

    return True


@app.route("/")
def index():
    """
    Show all tasks.
    """
    conn = get_db_connection()
    tasks = conn.execute("SELECT id, title, is_done FROM tasks").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    """
    Add a new task.

    SECURITY:
    - Read input safely
    - Validate it with is_valid_title()
    - Use parameterized query to prevent SQL injection
    """
    title = request.form.get("title", "").strip()

    # BASIC SECURITY: input validation
    if not is_valid_title(title):
        # In a real app you might flash a message,
        # but for now just redirect without saving.
        return redirect(url_for("index"))

    conn = get_db_connection()

    # BASIC SECURITY: parameterized query (the ? placeholder)
    conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    """
    Mark a task as completed.

    SECURITY:
    - task_id must be an integer (<int:task_id> in the route)
    - parameterized query again
    """
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET is_done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    """
    Delete a task.

    SECURITY:
    - task_id is validated by Flask as an integer
    - parameterized query
    """
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(app.run(host="0.0.0.0", port=5000, debug=True)
)
