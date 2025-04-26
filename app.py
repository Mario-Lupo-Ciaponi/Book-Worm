from sqlalchemy import insert, select, delete, column, func
from sqlalchemy.orm import sessionmaker
import customtkinter as ctk
from tkinter import messagebox

from models import engine, Book
from exceptions import EmptyFieldError, NegativeYearError, BookDoesNotExistError

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
    ):
        stmt = insert(Book).values(
            title=title,
            author=author,
            genre=genre,
            year=year,
            isbn=isbn,
        )

        self.session.execute(stmt)
        self.session.commit()

    def get_all_books(self):
        stmt = select(Book)

        result = self.session.execute(stmt)

        return result.scalars().all()

    def get_book_by_title(self, title: str):
        stmt = select(Book).where(Book.title == title).limit(1)
        result = self.session.execute(stmt)

        return result.scalars().first()

    def get_books_by_title(self, title: str):
        stmt = select(Book).where(Book.title == title)
        result = self.session.execute(stmt)

        return result.scalars().all()

    def order_by_year(self, ascending):
        stmt = select(Book).order_by(Book.year.asc()) if ascending else select(Book).order_by(Book.year.desc())
        result = self.session.execute(stmt)

        return result.scalars().all()

    def order_by_title(self, ascending):
        stmt = select(Book).order_by(Book.title.asc()) if ascending else select(Book).order_by(Book.title.desc())
        result = self.session.execute(stmt)

        return result.scalars().all()

    def order_by_author(self, ascending):
        stmt = select(Book).order_by(Book.author.asc()) if ascending else select(Book).order_by(Book.author.desc())
        result = self.session.execute(stmt)

        return result.scalars().all()

    def order_by_added_on(self, ascending):
        stmt = select(Book).order_by(Book.added_on.asc()) if ascending else select(Book).order_by(Book.added_on.desc())
        result = self.session.execute(stmt)

        return result.scalars().all()

    def delete_book_by_title(self, title: str):
        stmt = delete(Book).where(Book.title == title)

        self.session.execute(stmt)
        self.session.commit()
# ------ ^ Repo class


class BookWormApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Book Worm")

        self.update_idletasks()
        width = 500
        height = 520

        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)


        self.geometry(f"{width}x{height}+{x}+{y}")

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
            placeholder_text="Enter Title of Book here"
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
            text="Search",
            command=self.search_book
        )
        self.button_for_search.grid(
            row=1,
            column=2,
            padx=10,
            pady=10,
            sticky="w",
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

        with Session() as session:
            repo = Repo(session)

            books = repo.get_all_books()

            self.add_books_to_scrollable_frame(books)


        self.option_value = ctk.StringVar(value="Title(A-Z)")
        self.combo_box_for_order = ctk.CTkComboBox(
            self,
            values=["Title(A-Z)", "Title(Z-A)",
                    "Author(A-Z)", "Author(Z-A)",
                    "Year(Latest)", "Year(Earliest)",
                    "Added on(Latest)", "Added on(Earliest)"],
            variable=self.option_value,
            width=160,
        )
        self.combo_box_for_order.grid(
            row=5,
            column=1,
            sticky="e",
            padx=20
        )

        self.order_by_button = ctk.CTkButton(
            self,
            text="Order by",
            width=100,
            command=self.order_in_frame
        )
        self.order_by_button.grid(
            row=5,
            column=2,
            pady=20,
            sticky="w"
        )


    @staticmethod
    def check_if_book_exists_by_title(title: str):
        with Session() as session:
            repo = Repo(session)

            books = repo.get_all_books()

            titles = [b.title for b in books]

            if title in titles:
                return True

            return False

    def order_in_frame(self):
        with Session() as session:
            repo = Repo(session)
            books = ""
            order_option = self.option_value.get()

            if "Title" in order_option:
                books = repo.order_by_title(True if "A-Z" in order_option else False)
            elif "Author" in order_option:
                books = repo.order_by_author(True if "A-Z" in order_option else False)
            elif "Year" in order_option:
                books = repo.order_by_year(True if "Earliest" in order_option else False)
            elif "Added on" in order_option:
                books = repo.order_by_added_on(True if "Earliest" in order_option else False)
            else:
                messagebox.showerror("Invalid option!", "Invalid order option!")
                return

            self.add_books_to_scrollable_frame(books)

    def remove_book_from_scrollable_frame(self):
        for book in self.scrollable_frame_books.winfo_children():
            book.destroy()

    def search_book(self):
        try:
            title = self.search_entry.get().strip()

            if not title:
                raise EmptyFieldError
            if not self.check_if_book_exists_by_title(title):
                messagebox.showerror("No book found!", f'"{title}" was not found!')
                raise BookDoesNotExistError
        except EmptyFieldError:
            messagebox.showerror("Empty field!", "The search field must not be empty!")
        except BookDoesNotExistError:
            messagebox.showerror("Book does not exist!", f'"{title}" does not exist in the library!')
        else:
            with Session() as session:
                repo = Repo(session)

                self.remove_book_from_scrollable_frame()

                books = repo.get_books_by_title(title)

                self.add_books_to_scrollable_frame(books)

    def delete_book(self, title: str):
        user_answer = messagebox.askyesno("Are you sure?", f'Are you sure you want to delete "{title}"?')

        if user_answer:
            with Session() as session:
                repo = Repo(session)

                repo.delete_book_by_title(title)
                books = repo.get_all_books()

                self.add_books_to_scrollable_frame(books)

                messagebox.showinfo("Successful deletion!", f'"{title}" was deleted successfully!')


    def edit_book(self, title_of_book):
        edit_window = ctk.CTkToplevel()

        edit_window.title(f'Edit "{title_of_book}"')
        edit_window.geometry("400x400")

        edit_window.columnconfigure((0, 1), weight=1)

        # Label that will show up at the top
        edit_label = ctk.CTkLabel(
            edit_window,
            text=f'Edit - "{title_of_book}"',
            font=("Helvetica", 20, "bold")
        )
        edit_label.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="n",
            pady=(20, 10))




    def add_books_to_scrollable_frame(self, books: Book):
        self.remove_book_from_scrollable_frame()

        for book in books:
            book_for_frame = ctk.CTkLabel(
                self.scrollable_frame_books,
                text=f"Title: {book.title};\n"
                     f"Author: {book.author};\n"
                     f"Genre: {book.genre};\n"
                     f"Year: {book.year};\n"
                     f"ISBN: {book.isbn}\n"
                     f"Added on: {book.added_on}",

            )
            book_for_frame.pack(pady=(20, 5))

            edit_button = ctk.CTkButton(
                self.scrollable_frame_books,
                command=lambda b=book: self.edit_book(b.title),
                text="Edit",
                width=60
            )
            edit_button.pack(pady=5)

            delete_button = ctk.CTkButton(
                self.scrollable_frame_books,
                command=lambda b=book: self.delete_book(b.title),
                text="Delete",
                width=60,
                fg_color="red"
            )
            delete_button.pack(pady=(5, 0))


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

                    books = repo.get_all_books()

                    self.add_books_to_scrollable_frame(books)
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
