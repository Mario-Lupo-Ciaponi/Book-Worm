from sqlalchemy import insert, select, column
from sqlalchemy.orm import sessionmaker
import customtkinter as ctk
from tkinter import messagebox

from models import engine, Book
from exceptions import EmptyFieldError, NegativeYearError

Session = sessionmaker(bind=engine)


class Repo:
    def __init__(self, session: Session):
        self.session: Session = session

    def add_book(
        self,
        title: str,
        author: str,
        genre: str,
        year: int=None,
        isbn: str=None,
        description: str=None
    ):
        stmt = insert(Book).values(
            title=title,
            author=author,
            genre=genre,
            year=year,
            isbn=isbn,
            description=description
        )

        self.session.execute(stmt)
        self.session.commit()

    def get_all_books(self):
        stmt = select(Book)

        result = self.session.execute(stmt)

        return result.scalars().all()

# ------ ^ Repo class


class BookWormApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Book Worm")
        self.geometry("500x500")

        self.columnconfigure((0, 1, 2), weight=1)


        # Label that will show up at the top
        self.book_worm_label = ctk.CTkLabel(
            self,
            text="BookWorm - Your Personal Library",
            font=("Helvetica", 20, "bold")
        )
        self.book_worm_label.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="n",
            pady=(20, 10))

        self.label_for_search = ctk.CTkLabel(
            self,
            text="Search:"
        )
        self.label_for_search.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        self.search_entry = ctk.CTkEntry(
            self,
        )
        self.search_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            sticky="we"
        )

        self.button_for_search = ctk.CTkButton(
            self,
            text="Search"
        )
        self.button_for_search.grid(
            row=1,
            column=2,
            padx=10,
            pady=10,
            sticky="w"
        )

        self.add_book_button = ctk.CTkButton(
            self,
            text="+ Add book",
            width=100,
            command=self.open_add_book_window
        )
        self.add_book_button.grid(
            row=2,
            column=2,
            padx=20,
            pady=10,
        )

        self.label_for_booklist = ctk.CTkLabel(
            self,
            text="Booklist:",
            font=("Helvetica", 17, "bold")
        )
        self.label_for_booklist.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="n",
            pady=(20, 5)
        )

        self.scrollable_frame_books = ctk.CTkScrollableFrame(
            self,
            width=400,
        )
        self.scrollable_frame_books.grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="n",
            pady=(20, 5)
        )

        self.add_books_to_scrollable_frame()

    def add_books_to_scrollable_frame(self):
        for book in self.scrollable_frame_books.winfo_children():
            book.destroy()

        with Session() as session:
            repo = Repo(session)

            books = repo.get_all_books()

            for book in books:
                book_for_frame = ctk.CTkLabel(
                    self.scrollable_frame_books,
                    text=f"Title: {book.title};\n"
                         f"Author: {book.author};\n"
                         f"Genre: {book.genre};\n"
                         f"Year: {book.year};\n"
                         f"ISBN: {book.isbn}\n",
                )
                book_for_frame.pack()


    def open_add_book_window(self):
        def add_book():
            title = entry_for_title.get()
            author = entry_for_author.get()
            genre = entry_for_genre.get()
            year = entry_for_year.get()
            isbn = entry_for_isbn.get()

            try:
                if not title or not author or not genre:
                    raise EmptyFieldError

                if year:
                    year = int(year) # If it is not a number, it will throw a ValueError that will be caught

                    if year < 0:
                        raise NegativeYearError # The app does not support BC yet
            except EmptyFieldError:
                messagebox.showerror("Empty Field Error!", "Not all required fields are filled in!")
            except ValueError:
                messagebox.showerror("Invalid Year Error!", "The year must be an integer number!")
            except NegativeYearError:
                messagebox.showerror("Negative Year Error!", "The year must be positive!")
            else:
                with Session() as session:
                    repo = Repo(session)

                    repo.add_book(
                        title,
                        author,
                        genre,
                        year if year else None,
                        isbn if isbn else None
                    )

                    self.add_books_to_scrollable_frame()
                    messagebox.showinfo("Successfully added", f'"{title}" added successfully to library!')


        add_book_window = ctk.CTkToplevel()
        add_book_window.title("Add book to library")
        add_book_window.geometry("440x400")

        add_book_window.columnconfigure((0, 1), weight=1)

        add_book_label = ctk.CTkLabel(
            add_book_window,
            text="Add New Book:",
            font=("Helvetica", 20, "bold")
        )
        add_book_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="n",
            pady=(20, 10)
        )

        title_label = ctk.CTkLabel(
            add_book_window,
            text="Title:"
        )
        title_label.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        entry_for_title = ctk.CTkEntry(
            add_book_window,
        )
        entry_for_title.grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        author_label = ctk.CTkLabel(
            add_book_window,
            text="Author:"
        )
        author_label.grid(
            row=2,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        entry_for_author = ctk.CTkEntry(
            add_book_window,
        )
        entry_for_author.grid(
            row=2,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        genre_label = ctk.CTkLabel(
            add_book_window,
            text="Genre:"
        )
        genre_label.grid(
            row=3,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        entry_for_genre = ctk.CTkEntry(
            add_book_window,
        )
        entry_for_genre.grid(
            row=3,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        year_label = ctk.CTkLabel(
            add_book_window,
            text="Year:"
        )
        year_label.grid(
            row=4,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        entry_for_year = ctk.CTkEntry(
            add_book_window,
            placeholder_text="Optional"
        )
        entry_for_year.grid(
            row=4,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        isbn_label = ctk.CTkLabel(
            add_book_window,
            text="ISBN:"
        )
        isbn_label.grid(
            row=5,
            column=0,
            padx=10,
            pady=10,
            sticky="e"
        )

        entry_for_isbn = ctk.CTkEntry(
            add_book_window,
            placeholder_text="Optional"
        )
        entry_for_isbn.grid(
            row=5,
            column=1,
            padx=10,
            pady=10,
            sticky="w"
        )

        add_book_button = ctk.CTkButton(
            add_book_window,
            text="Add book",
            command=add_book
        )
        add_book_button.grid(
            row=6,
            column=0,
            columnspan=2,
            pady=20,
            sticky="s"
        )

        add_book_window.mainloop()



def main():
    book_worm_app = BookWormApp()
    book_worm_app.mainloop()


if __name__ == "__main__":
    main()
