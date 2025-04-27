import sqlalchemy.exc
from sqlalchemy import insert, select, delete, update, func
from sqlalchemy.orm import sessionmaker
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta

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
        description: str=None,
        year: int=None,
        isbn: str=None,
    ):
        """
            Inserts records into the table books

            Query:
            INSERT INTO
                books(title, author, genre, description, year, isbn)
            VALUES
                (
                *title given*,
                *author given*,
                *genre given*,
                *description given(if needed*,
                *year given(if needed)*,
                *isbn given(if needed)*
                );
        """
        stmt = insert(Book).values(
            title=title,
            author=author,
            genre=genre,
            description=description,
            year=year,
            isbn=isbn,
        )

        self.session.execute(stmt)
        self.session.commit()

    def get_all_books(self):
        """
            Gets all records from the books table

            Query:
            SELECT * FROM books;
        """
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

    def oldest_book(self):
        stmt = select(Book.title).order_by(Book.year).limit(1)
        result = self.session.execute(stmt)

        return result.scalars().first()

    def newest_book(self):
        stmt = select(Book.title).order_by(Book.year.desc()).limit(1)
        result = self.session.execute(stmt)

        return result.scalars().first()

    def get_books_count(self):
        stmt = select(func.count(Book.id))

        count = self.session.scalar(stmt)
        return count

    def get_read_and_unread_count(self):
        read_count_stmt = select(func.count(Book.id)).where(Book.is_read==True)
        unread_count_stmt = select(func.count(Book.id)).where(Book.is_read == False)

        read_count = self.session.scalar(read_count_stmt)
        unread_count = self.session.scalar(unread_count_stmt)

        return read_count, unread_count

    def get_books_count_added_in_the_past_month(self):
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)

        stmt = select(func.count(Book.id)).where(Book.added_on >= one_month_ago)

        result = self.session.scalar(stmt)

        return result

    def get_most_common_genre(self):
        stmt = (select(Book.genre, func.count(Book.id).label("count_of_genre"))
                .group_by(Book.genre)
                .order_by("count_of_genre")
                .limit(1))

        result = self.session.execute(stmt)

        return result.scalars().first()

    def get_average_publication_year(self):
        stmt = select(func.avg(Book.year))

        avg_publication_year = self.session.scalar(stmt)

        return avg_publication_year

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

    def update_book(self, old_title, new_title, new_author, new_genre, new_year, new_isbn):
        stmt = (update(Book)
                .where(Book.title == old_title)
                .values(
                    title=new_title if new_title else Book.title,
                    author=new_author if new_author else Book.author,
                    genre=new_genre if new_genre else Book.genre,
                    year=new_year if new_year else Book.year,
                    isbn=new_isbn if new_isbn else Book.isbn
        ))
        self.session.execute(stmt)
        self.session.commit()

    def update_book_read_status(self, book):
        stmt = update(Book).where(Book.id == book.id).values(is_read=True if not book.is_read else False)
        self.session.execute(stmt)
        self.session.commit()


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
        height = 550

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
            count_of_books = repo.get_books_count()

            self.add_books_to_scrollable_frame(books)

        self.statistics_button = ctk.CTkButton(
            self,
            text="Statistics",
            command=self.open_statistics_window,
            width=100
        )
        self.statistics_button.grid(
            row=5,
            column=2,
            pady=10
        )

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
            row=6,
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
            row=6,
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
        def update_book():
            new_title = title_entry.get().strip()
            new_author = author_entry.get().strip()
            new_genre = genre_entry.get().strip()
            new_year = year_entry.get().strip()
            new_isbn = isbn_entry.get().strip()

            try:
                if new_year:
                    new_year = int(new_year)

                    if new_year < 0:
                        raise NegativeYearError

                with Session() as session:
                    repo = Repo(session)

                    repo.update_book(title_of_book, new_title, new_author, new_genre, new_year, new_isbn)

                    books = repo.get_all_books()

                    self.add_books_to_scrollable_frame(books)
                    messagebox.showinfo("Successful update!", "The book was successfully updated!")
            except ValueError or NegativeYearError:
                messagebox.showerror("Invalid year!", "Year must be a positive integer number!")
            except sqlalchemy.exc.IntegrityError:
                messagebox.showerror("ISBN already used", f"{new_isbn} is already used!")


        edit_window = ctk.CTkToplevel()

        edit_window.title(f'Edit "{title_of_book}"')
        edit_window.geometry("400x400")

        edit_window.columnconfigure((0, 1), weight=1)

        place_holder_text = "leave blank if no edit is needed"
        width_of_entries = 220

        # Label that will show up at the top
        edit_label = ctk.CTkLabel(
            edit_window,
            text=f'Edit - "{title_of_book}"',
            font=("Helvetica", 20, "bold")
        )
        edit_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="n",
            pady=(20, 10))

        title_label = ctk.CTkLabel(
            edit_window,
            text="Title:"
        )
        title_label.grid(
            row=1,
            column=0,
            pady=10,
            padx=10,
            sticky="e"
        )

        title_entry = ctk.CTkEntry(
            edit_window,
            width=width_of_entries,
            placeholder_text=place_holder_text,
            justify="center"
        )
        title_entry.grid(
            row=1,
            column=1,
            sticky="w"
        )

        author_label = ctk.CTkLabel(
            edit_window,
            text="Author:"
        )
        author_label.grid(
            row=2,
            column=0,
            pady=10,
            padx=10,
            sticky="e"
        )

        author_entry = ctk.CTkEntry(
            edit_window,
            width=width_of_entries,
            placeholder_text=place_holder_text,
            justify="center"
        )
        author_entry.grid(
            row=2,
            column=1,
            sticky="w"
        )

        genre_label = ctk.CTkLabel(
            edit_window,
            text="Genre:"
        )
        genre_label.grid(
            row=3,
            column=0,
            pady=10,
            padx=10,
            sticky="e"
        )

        genre_entry = ctk.CTkEntry(
            edit_window,
            width=width_of_entries,
            placeholder_text=place_holder_text,
            justify="center"
        )
        genre_entry.grid(
            row=3,
            column=1,
            sticky="w"
        )

        year_label = ctk.CTkLabel(
            edit_window,
            text="Year:"
        )
        year_label.grid(
            row=4,
            column=0,
            pady=10,
            padx=10,
            sticky="e"
        )

        year_entry = ctk.CTkEntry(
            edit_window,
            width=width_of_entries,
            placeholder_text=place_holder_text,
            justify="center"
        )
        year_entry.grid(
            row=4,
            column=1,
            sticky="w"
        )

        isbn_label = ctk.CTkLabel(
            edit_window,
            text="ISBN:"
        )
        isbn_label.grid(
            row=5,
            column=0,
            pady=10,
            padx=10,
            sticky="e"
        )

        isbn_entry = ctk.CTkEntry(
            edit_window,
            width=width_of_entries,
            placeholder_text=place_holder_text,
            justify="center"
        )
        isbn_entry.grid(
            row=5,
            column=1,
            sticky="w"
        )

        edit_button = ctk.CTkButton(
            edit_window,
            command=update_book,
            text="Edit"
        )
        edit_button.grid(
            row=6,
            column=0,
            columnspan=2,
            pady=20,
            sticky="s"
        )

    def change_book_read_status(self, book):
        with Session() as session:
            repo = Repo(session)
            repo.update_book_read_status(book)

            books = repo.get_all_books()
            self.add_books_to_scrollable_frame(books)

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

            is_read_value = ctk.BooleanVar(value=book.is_read)
            is_read_checkbox = ctk.CTkCheckBox(
                self.scrollable_frame_books,
                text="Read",
                command=lambda b=book: self.change_book_read_status(b),
                variable=is_read_value,
                onvalue=True,
                offvalue=False,
            )
            is_read_checkbox.pack(pady=10)

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
            delete_button.pack(pady=(5, 15))


    def open_add_book_window(self):
        def add_book():
            title = entry_for_title.get().strip()
            author = entry_for_author.get().strip()
            genre = entry_for_genre.get().strip()
            year = entry_for_year.get().strip()
            isbn = entry_for_isbn.get().strip()

            try:
                if not title or not author or not genre:
                    raise EmptyFieldError

                if year:
                    year = int(year) # If it is not a number, it will throw a ValueError that will be caught

                    if year < 0:
                        raise NegativeYearError # The app does not support BC yet

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
            except EmptyFieldError:
                messagebox.showerror("Empty Field Error!", "Not all required fields are filled in!")
            except ValueError:
                messagebox.showerror("Invalid Year Error!", "The year must be an integer number!")
            except NegativeYearError:
                messagebox.showerror("Negative Year Error!", "The year must be positive!")
            except sqlalchemy.exc.IntegrityError:
                messagebox.showerror("ISBN already used!", f"{isbn} ISBN is already used!")

        add_book_window = ctk.CTkToplevel()
        add_book_window.title("Add book to library")

        width = 440
        height = 420

        x = 25
        y = (self.winfo_screenheight() // 2) - (height // 2)

        add_book_window.geometry(f"{width}x{height}+{x}+{y}")

        add_book_window.columnconfigure((0, 1), weight=1)

        padding = 10

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
            padx=padding,
            pady=padding,
            sticky="e"
        )

        entry_for_title = ctk.CTkEntry(
            add_book_window,
        )
        entry_for_title.grid(
            row=1,
            column=1,
            padx=padding,
            pady=padding,
            sticky="w"
        )

        author_label = ctk.CTkLabel(
            add_book_window,
            text="Author:"
        )
        author_label.grid(
            row=2,
            column=0,
            padx=padding,
            pady=padding,
            sticky="e"
        )

        entry_for_author = ctk.CTkEntry(
            add_book_window,
        )
        entry_for_author.grid(
            row=2,
            column=1,
            padx=padding,
            pady=padding,
            sticky="w"
        )

        genre_label = ctk.CTkLabel(
            add_book_window,
            text="Genre:"
        )
        genre_label.grid(
            row=3,
            column=0,
            padx=padding,
            pady=padding,
            sticky="e"
        )

        entry_for_genre = ctk.CTkEntry(
            add_book_window,
        )
        entry_for_genre.grid(
            row=3,
            column=1,
            padx=padding,
            pady=padding,
            sticky="w"
        )

        description_label = ctk.CTkLabel(
            add_book_window,
            text="Description:"
        )
        description_label.grid(
            row=4,
            column=0,
            padx=padding,
            pady=padding,
            sticky="e"
        )

        entry_for_description = ctk.CTkEntry(
            add_book_window,
            placeholder_text="Optional"
        )
        entry_for_description.grid(
            row=4,
            column=1,
            padx=padding,
            pady=padding,
            sticky="w"
        )

        year_label = ctk.CTkLabel(
            add_book_window,
            text="Year:"
        )
        year_label.grid(
            row=5,
            column=0,
            padx=padding,
            pady=padding,
            sticky="e"
        )

        entry_for_year = ctk.CTkEntry(
            add_book_window,
            placeholder_text="Optional"
        )
        entry_for_year.grid(
            row=5,
            column=1,
            padx=padding,
            pady=padding,
            sticky="w"
        )

        isbn_label = ctk.CTkLabel(
            add_book_window,
            text="ISBN:"
        )
        isbn_label.grid(
            row=6,
            column=0,
            padx=padding,
            pady=padding,
            sticky="e"
        )

        entry_for_isbn = ctk.CTkEntry(
            add_book_window,
            placeholder_text="Optional"
        )
        entry_for_isbn.grid(
            row=6,
            column=1,
            padx=padding,
            pady=padding,
            sticky="w"
        )

        add_book_button = ctk.CTkButton(
            add_book_window,
            text="Add book",
            command=add_book
        )
        add_book_button.grid(
            row=7,
            column=0,
            columnspan=2,
            pady=20,
            sticky="s"
        )

    @staticmethod
    def open_statistics_window():
        statistics_window = ctk.CTkToplevel()

        statistics_window.title("Statistics")

        width = 400
        height = 445

        padding_y = 10

        statistics_window.geometry(f"{width}x{height}")

        statistics_window.columnconfigure((0, 1), weight=1)

        book_worm_label = ctk.CTkLabel(
            statistics_window,
            text="Statistics of Library:",
            font=("Helvetica", 20, "bold")
        )
        book_worm_label.pack(
            pady=(20, 10),
        )


        with Session() as session:
            repo = Repo(session)

            total_books_count = repo.get_books_count()
            read_count, unread_count = repo.get_read_and_unread_count()

            read_percentage = (read_count / total_books_count) * 100 if total_books_count else 0
            unread_percentage = (unread_count / total_books_count) * 100 if total_books_count else 0

            most_common_genre = repo.get_most_common_genre()

            most_recent_book = repo.oldest_book()
            latest_book = repo.newest_book()

            average_publication_year = repo.get_average_publication_year()

            books_added_in_the_past_month = repo.get_books_count_added_in_the_past_month()

        total_books_label = ctk.CTkLabel(
            statistics_window,
            text=f"Total number of books:\n{total_books_count}"
        )
        total_books_label.pack(
            pady=padding_y,
        )


        count_of_read_unread_books_label = ctk.CTkLabel(
            statistics_window,
            text=f"Count of read/unread books:\n"
                 f"{read_count} ({read_percentage:.0f}%) / {unread_count} ({unread_percentage:.0f}%)"
        )
        count_of_read_unread_books_label.pack(
            pady=padding_y,
        )

        read_unread_progress_bar = ctk.CTkProgressBar(
            statistics_window,
            orientation="horizontal",
            fg_color="red",
            progress_color="green",
        )
        read_unread_progress_bar.pack(
            pady=5
        )
        read_unread_progress_bar.set(read_percentage/100)

        most_common_genre_label = ctk.CTkLabel(
            statistics_window,
            text=f"Most common genre:\n{most_common_genre}"
        )
        most_common_genre_label.pack(
            pady=padding_y
        )

        most_recent_book_label = ctk.CTkLabel(
            statistics_window,
            text=f"Oldest book:\n{most_recent_book}"
        )
        most_recent_book_label.pack(
            pady=padding_y
        )

        latest_book_label = ctk.CTkLabel(
            statistics_window,
            text=f"Newest book:\n{latest_book}"
        )
        latest_book_label.pack(
            pady=padding_y
        )

        average_publication_year_label = ctk.CTkLabel(
            statistics_window,
            text=f"Average publication year:\n{average_publication_year:.0f}"
        )
        average_publication_year_label.pack(
            pady=padding_y
        )

        books_added_in_the_past_month_label = ctk.CTkLabel(
            statistics_window,
            text=f"Books added in the past month:\n{books_added_in_the_past_month}"
        )
        books_added_in_the_past_month_label.pack(
            pady=padding_y
        )


def main():
    book_worm_app = BookWormApp()
    book_worm_app.mainloop()


if __name__ == "__main__":
    main()
