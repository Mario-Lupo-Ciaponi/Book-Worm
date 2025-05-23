import sqlalchemy.exc
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
import customtkinter as ctk
from tkinter import messagebox

from db.models import engine, Book
from db.repo import Repo

from exceptions import EmptyFieldError, NegativeYearError

Session = sessionmaker(bind=engine)


class BookWormApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Book Worm")

        self.update_idletasks()
        width = 500
        height = 655

        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)


        self.geometry(f"{width}x{height}+{x}+{y}")

        self.theme = "dark"
        ctk.set_appearance_mode(self.theme)

        self.bind("<Escape>", self.close_window)
        self.bind_all("<Control-n>", self.open_add_book_window)
        self.bind_all("<Control-s>", self.open_statistics_window)
        self.bind_all("<Control-t>", self.toggle_theme)

        self.columnconfigure((0, 1, 2), weight=1)
        self.order_option = ctk.StringVar(value="No order")

        # Label that will show up at the top

        self.book_worm_label = self.add_header_label(
            self,
            0,
            "📚BookWorm - Your Personal Library",
            20,
            3,
            20,
            18
        )

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

        self.search_choice = ctk.StringVar(value="title")

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
        self.search_entry.bind("<Return>", self.on_search_enter)

        self.button_for_search = ctk.CTkButton(
            self,
            text="🔍 Search",
            command=self.search_book,
        )
        self.button_for_search.grid(
            row=1,
            column=2,
            padx=10,
            pady=10,
            sticky="w",
        )

        self.search_option_menu = ctk.CTkOptionMenu(
            self,
            values=["title", "author", "genre", "year", "description", "isbn"],
            variable=self.search_choice,
        )
        self.search_option_menu.grid(
            row=2,
            column=1
        )

        self.add_book_button = ctk.CTkButton(
            self,
            text="+ Add book",
            width=100,
            command=self.open_add_book_window
        )
        self.add_book_button.grid(
            row=3,
            column=2,
            padx=20,
            pady=(20, 10),
        )

        self.label_for_booklist = self.add_header_label(
            self,
            4,
            "Booklist:",
            17,
            3,
            20,
            0
        )

        self.scrollable_frame_books = ctk.CTkScrollableFrame(
            self,
            width=400,
        )
        self.scrollable_frame_books.grid(
            row=5,
            column=0,
            columnspan=3,
            sticky="n",
            pady=(10, 5)
        )

        self.prepare_books()

        self.statistics_button = ctk.CTkButton(
            self,
            text="📈Statistics",
            command=self.open_statistics_window,
            width=100
        )
        self.statistics_button.grid(
            row=6,
            column=2,
            pady=10
        )

        self.order_label = ctk.CTkLabel(
            self,
            text="Order by:"
        )
        self.order_label.grid(
            row=7,
            column=0,
            sticky="e",
        )

        self.combo_box_for_order = ctk.CTkComboBox(
            self,
            values=["No order",
                    "Title(A-Z)", "Title(Z-A)",
                    "Author(A-Z)", "Author(Z-A)",
                    "Year(Latest)", "Year(Earliest)",
                    "Added on(Latest)", "Added on(Earliest)"],
            variable=self.order_option,
            width=160,
            command=self.prepare_books
        )
        self.combo_box_for_order.grid(
            row=7,
            column=1,
            sticky="w",
            padx=20
        )

        self.genre_chosen_var = ctk.StringVar(value="No genre")
        self.filter_by_genre_combo_box = ctk.CTkComboBox(
            self,
            values=self.genres,
            variable=self.genre_chosen_var,
            command=self.filter_by_genre
        )
        self.filter_by_genre_combo_box.grid(
            row=8,
            column=1,
            pady=10
        )

        self.toggle_theme_button = ctk.CTkButton(
            self,
            text="☀️",
            width=30,
            command=self.toggle_theme
        )
        self.toggle_theme_button.grid(
            row=9,
            column=2,
            pady=10
        )

    @property
    def genres(self):
        with Session() as session:
            repo = Repo(session)

            genres = repo.get_all_genres()
            genres.append("No genre")

            return genres

    def toggle_theme(self, event=None):
        if self.theme == "dark":
            self.theme = "light"
            ctk.set_appearance_mode(self.theme)

            self.toggle_theme_button.configure(text="🌙")
        else:
            self.theme = "dark"
            ctk.set_appearance_mode(self.theme)

            self.toggle_theme_button.configure(text="☀️")

    @staticmethod
    def make_empty_entries(window):
        for widget in window.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, len(widget.get()))

    @staticmethod
    def get_all_entries(window: ctk.CTkToplevel):
        entries = []

        for widget in window.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                entries.append(widget)

        return entries

    @staticmethod
    def add_header_label(master, row, text_of_label, font_size, columnspan, upper_pady, lower_pady):
        label = ctk.CTkLabel(
            master,
            text=text_of_label,
            font=("Segoe UI", font_size, "bold")
        )
        label.grid(
            row=row,
            column=0,
            columnspan=columnspan,
            sticky="n",
            pady=(upper_pady, lower_pady))

        return label

    @staticmethod
    def add_entry_and_entry(master, row, text_of_label, width, placeholder=None):
        label = ctk.CTkLabel(
            master,
            text=text_of_label
        )
        label.grid(
            column=0,
            row=row,
            pady=10,
            padx=10,
            sticky="e"
        )

        entry = ctk.CTkEntry(
            master,
            width=width,
            placeholder_text=placeholder or "",
            justify="center"
        )
        entry.grid(
            row=row,
            column=1,
            sticky="w"
        )

        return entry


    def bind_arrow_keys_to_entry(self, window: ctk.CTkToplevel):
        entries = self.get_all_entries(window)

        for i, entry in enumerate(entries):
            if i > 0:
                entry.bind("<Up>", self.move_on_previous_entry)
            if i < len(entries) - 1:
                entry.bind("<Down>", self.move_on_next_entry)

    @staticmethod
    def check_if_book_exists_by_title(title: str):
        with Session() as session:
            repo = Repo(session)

            books = repo.get_all_books()

            titles = [b.title for b in books]

            if title in titles:
                return True

            return False

    def remove_book_from_scrollable_frame(self):
        for book in self.scrollable_frame_books.winfo_children():
            book.destroy()

    def search_book(self):
        try:
            with Session() as session:
                repo = Repo(session)

                mapper_for_searching_options = {
                    "title": repo.get_books_by_title_contain,
                    "author": repo.get_books_by_author_contain,
                    "genre": repo.get_books_by_genre_contain,
                    "year": repo.get_books_by_year,
                    "description": repo.get_books_by_description_contain,
                    "isbn": repo.get_books_by_isbn_contain
                }

                search_entry_value = self.search_entry.get().strip()

                if not search_entry_value:
                    books = repo.get_all_books()
                else:
                    search_value_option = self.search_choice.get()

                    if search_entry_value == "year":
                        search_entry_value = int(search_entry_value)

                        if 0 > search_entry_value:
                            raise NegativeYearError

                    books = mapper_for_searching_options[search_value_option](search_entry_value)

                self.add_books_to_scrollable_frame(books)
        except (ValueError, NegativeYearError):
            messagebox.showerror("Invalid year!", "Year must be a postivie integer number!")

    def delete_book(self, title: str):
        user_answer = messagebox.askyesno("Are you sure?", f'Are you sure you want to delete "{title}"?')

        if user_answer:
            with Session() as session:
                repo = Repo(session)

                repo.delete_book_by_title(title)

                self.prepare_books()

                messagebox.showinfo("Successful deletion!", f'"{title}" was deleted successfully!')

    def edit_book(self, book):
        def update_book(event=None):
            new_title = title_entry.get().strip()
            new_author = author_entry.get().strip()
            new_genre = genre_entry.get().strip()
            new_description = description_entry.get().strip()
            new_year = year_entry.get().strip()
            new_isbn = isbn_entry.get().strip()

            try:
                if new_year:
                    new_year = int(new_year)

                    if new_year < 0:
                        raise NegativeYearError

                with Session() as session:
                    repo = Repo(session)

                    repo.update_book(
                        book.id,
                        new_title,
                        new_author,
                        new_genre,
                        new_description,
                        new_year,
                        new_isbn)

                    self.prepare_books()
                    messagebox.showinfo("Successful update!", "The book was successfully updated!")

                    self.make_empty_entries(edit_window)
            except ValueError or NegativeYearError:
                messagebox.showerror("Invalid year!", "Year must be a positive integer number!")
            except sqlalchemy.exc.IntegrityError:
                messagebox.showerror("ISBN already used", f"{new_isbn} is already used!")


        title_of_book = book.title

        edit_window = ctk.CTkToplevel()

        width = 400
        height = 410

        edit_window.title(f'Edit "{title_of_book}"')
        edit_window.geometry(f"{width}x{height}")
        edit_window.bind("<Return>", update_book)

        edit_window.columnconfigure((0, 1), weight=1)

        placeholder_text = "leave blank if no edit is needed"
        width_of_entries = 220

        edit_label = self.add_header_label(
            edit_window,
            0,
            f'Edit - "{title_of_book}"',
            20,
            2,
            20,
            10
        )

        title_entry = self.add_entry_and_entry(
            edit_window,
            1,
            "Title:",
            width_of_entries,
            placeholder_text)
        title_entry.focus_set()


        author_entry = self.add_entry_and_entry(
            edit_window,
            2,
            "Author:",
            width_of_entries,
            placeholder_text
        )

        genre_entry = self.add_entry_and_entry(
            edit_window,
            3,
            "Genre:",
            width_of_entries,
            placeholder_text
        )

        description_entry = self.add_entry_and_entry(
            edit_window,
            4,
            "Description:",
            width_of_entries,
            placeholder_text
        )

        year_entry = self.add_entry_and_entry(
            edit_window,
            5,
            "Year:",
            width_of_entries,
            placeholder_text
        )

        isbn_entry = self.add_entry_and_entry(
            edit_window,
            6,
            "ISBN:",
            width_of_entries,
            placeholder_text
        )

        edit_button = ctk.CTkButton(
            edit_window,
            command=update_book,
            text="Edit"
        )
        edit_button.grid(
            row=7,
            column=0,
            columnspan=2,
            pady=20,
            sticky="s"
        )

        self.bind_arrow_keys_to_entry(edit_window)

    def change_book_read_status(self, book):
        with Session() as session:
            repo = Repo(session)
            repo.update_book_read_status(book)

            self.prepare_books()

    def filter_by_genre(self, event=None):
        genre_option = self.genre_chosen_var.get()

        if genre_option == "No genre":
            self.prepare_books()
        elif genre_option not in self.genres:
            messagebox.showerror("Invalid Genre!", "Invalid genre option!")
            return

        with Session() as session:
            repo = Repo(session)

            books = repo.filter_by_genre(genre_option)

            self.add_books_to_scrollable_frame(books)



    def prepare_books(self, event=None):
        with Session() as session:
            repo = Repo(session)
            order_option = self.order_option.get()

            if "No order" in order_option:
                books = repo.get_all_books()
            elif "Title" in order_option:
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

    @staticmethod
    def show_books_information(book):
        title_of_book = book.title
        author_of_book = book.author
        genre_of_book = book.genre
        year_of_book = book.year
        description_of_book = book.description
        isbn_of_book = book.isbn
        is_read = book.is_read
        added_on = book.added_on

        width = 400
        height = 500

        padding = 10

        book_detail_window = ctk.CTkToplevel()
        book_detail_window.title(title_of_book)
        book_detail_window.geometry(f"{width}x{height}")

        book_title_label = ctk.CTkLabel(
            book_detail_window,
            text=title_of_book,
            font=("Segoe UI", 20, "bold")
        )
        book_title_label.pack(
            pady=(20, 10)
        )

        book_author_label = ctk.CTkLabel(
            book_detail_window,
            text=f"Author:\n{author_of_book}"
        )
        book_author_label.pack(
            pady=padding
        )

        book_genre_label = ctk.CTkLabel(
            book_detail_window,
            text=f"Genre:\n{genre_of_book}"
        )
        book_genre_label.pack(
            pady=padding
        )

        book_year_label = ctk.CTkLabel(
            book_detail_window,
            text=f"Year:\n{year_of_book if year_of_book else "No year"}"
        )
        book_year_label.pack(
            pady=padding
        )

        book_description_label = ctk.CTkLabel(
            book_detail_window,
            text=f"Description:\n{description_of_book if description_of_book else "No description"}",
            wraplength=400
        )
        book_description_label.pack(
            pady=padding
        )

        book_isbn_label = ctk.CTkLabel(
            book_detail_window,
            text=f"ISBN:\n{isbn_of_book if isbn_of_book else "No ISBN"}",
            wraplength=400
        )
        book_isbn_label.pack(
            pady=padding
        )

        book_is_read_label = ctk.CTkLabel(
            book_detail_window,
            text=f"Is read:\n{"Yes" if is_read else "No"}",
            wraplength=400
        )
        book_is_read_label.pack(
            pady=padding
        )

        book_added_on_label = ctk.CTkLabel(
            book_detail_window,
            text=f"Added on:\n{added_on.strftime("%d %B, %Y at %H:%M")}",
            wraplength=400
        )
        book_added_on_label.pack(
            pady=padding
        )

    def add_books_to_scrollable_frame(self, books: Book):
        self.remove_book_from_scrollable_frame()

        if not books:
            ctk.CTkLabel(
                self.scrollable_frame_books,
                text="No Books found!",
                pady=80,
                font=("Segoe UI", 20)
            ).pack()

        for book in books:
            book_for_frame = ctk.CTkLabel(
                self.scrollable_frame_books,
                text=f"Title: {book.title}\n"
                     f"Author: {book.author}\n"
                     f"Genre: {book.genre}\n"
                     f"ISBN: {book.isbn if book.isbn else "No ISBN"}",
                font=("Helvetica", 15)
            )
            book_for_frame.pack(pady=(20, 9))

            width_for_buttons = 60

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

            more_details_button = ctk.CTkButton(
                self.scrollable_frame_books,
                command=lambda b=book: self.show_books_information(b),
                text="Details",
                width=width_for_buttons,
                fg_color="green",
            )
            more_details_button.pack(pady=5)

            edit_button = ctk.CTkButton(
                self.scrollable_frame_books,
                command=lambda b=book: self.edit_book(b),
                text="Edit",
                width=width_for_buttons,
            )
            edit_button.pack(pady=5)

            delete_button = ctk.CTkButton(
                self.scrollable_frame_books,
                command=lambda b=book: self.delete_book(b.title),
                text="Delete",
                width=width_for_buttons,
                fg_color="red"
            )
            delete_button.pack(pady=(5, 15))

    def open_add_book_window(self, event=None):
        def mark_all_required_empty_fields():
            count = 1
            for widget in add_book_window.winfo_children():
                if isinstance(widget, ctk.CTkEntry) and not widget.get():
                    widget.configure(border_color="red")
                    count += 1

                if count == 3:
                    break

        def mark_single_entry(entry):
            entry.configure(border_color="red")

        def add_book(event=None):
            title = entry_for_title.get().strip()
            author = entry_for_author.get().strip()
            genre = entry_for_genre.get().strip()
            year = entry_for_year.get().strip()
            description = entry_for_description.get().strip()
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
                        description if description else None,
                        year if year else None,
                        isbn if isbn else None
                    )

                    self.prepare_books()
                    messagebox.showinfo("Successfully added", f'"{title}" added successfully to library!')
                    self.make_empty_entries(add_book_window)
            except EmptyFieldError:
                mark_all_required_empty_fields()
            except (ValueError, NegativeYearError):
                mark_single_entry(entry_for_year)
            except sqlalchemy.exc.IntegrityError:
                mark_single_entry(entry_for_isbn)

        add_book_window = ctk.CTkToplevel()
        add_book_window.title("Add book to library")
        add_book_window.bind("<Return>", add_book)

        width = 440
        height = 495

        x = 25
        y = (self.winfo_screenheight() // 2) - (height // 2)

        add_book_window.geometry(f"{width}x{height}+{x}+{y}")

        add_book_window.columnconfigure((0, 1), weight=1)

        width_of_entries = 220

        add_book_label = self.add_header_label(
            add_book_window,
            0,
            "Add New Book:",
            20,
            2,
            20,
            10
        )

        required_field_label = ctk.CTkLabel(
            add_book_window,
            text="--- Required fields ---",
            font=("Helvetica", 13)
        )
        required_field_label.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="s",
            pady=(0, 10)
        )

        entry_for_title = self.add_entry_and_entry(
            add_book_window,
            2,
            "Title:",
            width_of_entries
        )
        entry_for_title.focus_set()

        entry_for_author = self.add_entry_and_entry(
            add_book_window,
            3,
            "Author:",
            width_of_entries
        )

        entry_for_genre = self.add_entry_and_entry(
            add_book_window,
            4,
            "Genre:",
            width_of_entries
        )

        optional_field_label = ctk.CTkLabel(
            add_book_window,
            text="--- Optional fields ---",
            font=("Helvetica", 13)
        )
        optional_field_label.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="s",
            pady=(10, 10)
        )

        entry_for_description = self.add_entry_and_entry(
            add_book_window,
            6,
            "Description:",
            width_of_entries
        )

        entry_for_year = self.add_entry_and_entry(
            add_book_window,
            7,
            "Year:",
            width_of_entries,
            "e.g. 2025"
        )

        entry_for_isbn = self.add_entry_and_entry(
            add_book_window,
            8,
            "ISBN:",
            width_of_entries
        )

        add_book_button = ctk.CTkButton(
            add_book_window,
            text="Add book",
            command=add_book
        )
        add_book_button.grid(
            row=9,
            column=0,
            columnspan=2,
            pady=20,
            sticky="s"
        )

        self.bind_arrow_keys_to_entry(add_book_window)

    @staticmethod
    def open_statistics_window(event=None):
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
            font=("Segoe UI", 20, "bold")
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
            text=f"📘Total number of books:\n{total_books_count}"
        )
        total_books_label.pack(
            pady=padding_y,
        )


        count_of_read_unread_books_label = ctk.CTkLabel(
            statistics_window,
            text=f"📈Count of read/unread books:\n"
                 f"{read_count} ({read_percentage:.0f}%) / {unread_count} ({unread_percentage:.0f}%)"
        )
        count_of_read_unread_books_label.pack(
            pady=padding_y,
        )

        read_unread_progress_bar = ctk.CTkProgressBar(
            statistics_window,
            orientation="horizontal",
            fg_color="gray",
            progress_color="green",
        )
        read_unread_progress_bar.pack(
            pady=5
        )
        read_unread_progress_bar.set(read_percentage/100)

        most_common_genre_label = ctk.CTkLabel(
            statistics_window,
            text=f"📚Most common genre:\n{most_common_genre}"
        )
        most_common_genre_label.pack(
            pady=padding_y
        )

        most_recent_book_label = ctk.CTkLabel(
            statistics_window,
            text=f"📕Oldest book:\n{most_recent_book}"
        )
        most_recent_book_label.pack(
            pady=padding_y
        )

        latest_book_label = ctk.CTkLabel(
            statistics_window,
            text=f"📖Newest book:\n{latest_book}"
        )
        latest_book_label.pack(
            pady=padding_y
        )

        average_publication_year_label = ctk.CTkLabel(
            statistics_window,
            text=f"📅Average publication year:\n{average_publication_year:.0f}"
        )
        average_publication_year_label.pack(
            pady=padding_y
        )

        books_added_in_the_past_month_label = ctk.CTkLabel(
            statistics_window,
            text=f"🧮Books added in the past month:\n{books_added_in_the_past_month}"
        )
        books_added_in_the_past_month_label.pack(
            pady=padding_y
        )

    def on_search_enter(self, event=None):
        self.search_book()

    @staticmethod
    def move_on_next_entry(event):
        event.widget.tk_focusNext().focus()
        return "break"

    @staticmethod
    def move_on_previous_entry(event=None):
        event.widget.tk_focusPrev().focus()
        return "break"

    def close_window(self, event=None):
        answer = messagebox.askyesno("Are you sure?", "Are you sure you want ot quit BookWorm?")

        if answer:
            self.destroy()
