
from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

DB_PATH = os.environ.get("BOOKS_DB", "books.db")


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0)
            )
        """)

        count = connection.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        if count == 0:
            connection.executemany(
                "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
                [
                    ("Python Programming", "John Smith", 450.00),
                    ("Web Development Basics", "Alice Brown", 550.00),
                    ("Data Structures and Algorithms", "Robert Lee", 650.00),
                ],
            )


@app.route("/", methods=["GET", "POST"])
def index():
    message = request.args.get("message", "")

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        price_text = request.form.get("price", "").strip()

        try:
            price = float(price_text)
            if not title or not author or price < 0:
                raise ValueError
        except ValueError:
            return redirect(url_for(
                "index", message="Enter a valid title, author and price."
            ))

        with get_db() as connection:
            connection.execute(
                "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
                (title, author, price),
            )

        return redirect(url_for("index", message="Book added successfully."))

    search = request.args.get("search", "").strip()

    with get_db() as connection:
        if search:
            books = connection.execute(
                """SELECT * FROM books
                   WHERE title LIKE ? OR author LIKE ?
                   ORDER BY id DESC""",
                (f"%{search}%", f"%{search}%"),
            ).fetchall()
        else:
            books = connection.execute(
                "SELECT * FROM books ORDER BY id DESC"
            ).fetchall()

    return render_template(
        "index.html", books=books, search=search, message=message
    )


@app.post("/delete/<int:book_id>")
def delete_book(book_id):
    with get_db() as connection:
        connection.execute("DELETE FROM books WHERE id = ?", (book_id,))

    return redirect(url_for("index", message="Book deleted successfully."))


initialize_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
