# 📚 BookWorm

A desktop-based Book Library Manager built with Python using `customtkinter` for the interface and `SQLAlchemy` for database management. This tool allows users to add, edit, and search books with features like form validation, duplicate ISBN prevention, and keyboard navigation.

---

## ✨ Features

- 🔍 **Search and filter books** by title
- ➕ **Add new books** with validation for required fields and numeric year
- ✏️ **Edit existing books**, supporting partial updates
- 🗑️ **Delete books** from the library
- ✅ Form validation with error messages and red border highlighting
- 🎯 Smooth keyboard navigation (`Tab`, `Shift+Tab`, `Enter`)
- 🧠 Uses SQLite database via SQLAlchemy ORM
- 🧼 Auto-clearing form fields after submission
- 🖥️ Clean, modern GUI using `customtkinter`

---

## 📦 Requirements

- Python 3.8+
- `customtkinter`
- `sqlalchemy`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

1. Clone this repository or download the code.
2. Make sure `models.py` is in the same directory and defines a `Book` class and SQLAlchemy `Base`.
3. Run the application:

```bash
python main.py
```

---

## 📂 File Structure

```graphql
.
├── alembic/         # Alembic migrations folder
├── venv/            # Python virtual environment (not included in version control)
├── alembic.ini      # Alembic configuration file
├── exceptions.py    # Custom exception definitions
├── LICENSE          # License for the project
├── main.py          # Main application logic with UI
├── models.py        # SQLAlchemy models and DB setup
├── requirements.txt # Python dependencies
└── README.md        # Project documentation

```

---

## 📘 Book Entry Fields

| Field       | Required | Example           |
|-------------|----------|-------------------|
| Title       | ✅       | "1984"            |
| Author      | ✅       | "George Orwell"   |
| Genre       | ✅       | "Dystopian"       |
| Description | ❌       | "Classic novel"   |
| Year        | ❌       | 1949              |
| ISBN        | ❌       | 9780451524935     |


---

## 🛠️ Tech Stack

- GUI: customtkinter
- ORM: SQLAlchemy
- DB: PostgreSQL (via SQLAlchemy)

---

## 🎮 Keyboard Shortcuts

- Ctrl+n — Add new book window
- Ctrl+s - Open statistic window
- Ctrl+t - Toggle theme
- Enter — Submit form (when focused on entry)
- Tab/Shift+Tab — Navigate between fields

---

## ✅ To-Do / Improvements

- Add book cover support (image files)
- Export/import book list to CSV or JSON
- Pagination or scrollable book list

---

## 🧑‍💻 Author

Developed by Mario Lupo Ciaponi — feel free to modify, contribute, or fork!

# 📝 License

This project is open-source under the MIT License.
