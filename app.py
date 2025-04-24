from sqlalchemy import insert, select
from sqlalchemy.orm import sessionmaker
import customtkinter as ctk

from models import engine, Book

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
            width=100
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



def main():
    book_worm_app = BookWormApp()
    book_worm_app.mainloop()


if __name__ == "__main__":
    main()
