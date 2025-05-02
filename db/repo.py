from sqlalchemy import select, delete, update, insert, func

from .models import Book

from datetime import datetime, timedelta



class Repo:
    def __init__(self, session):
        self.session = session

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

    def get_all_genres(self):
        stmt = select(Book.genre).distinct(Book.genre)

        result = self.session.execute(stmt)

        return result.scalars().all()

    def filter_by_genre(self, genre):
        stmt = select(Book).where(Book.genre == genre)

        result = self.session.execute(stmt)

        return result.scalars().all()

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
        """
            SELECT
                *
            FROM
                books
            WHERE
                title = {title}
            LIMIT
                1;
        """
        stmt = select(Book).where(Book.title == title).limit(1)
        result = self.session.execute(stmt)

        return result.scalars().first()

    def get_books_by_title_contain(self, title: str):
        stmt = select(Book).where(Book.title.ilike(f"%{title}%"))
        result = self.session.execute(stmt)

        return result.scalars().all()

    def get_books_by_author_contain(self, author: str):
        stmt = select(Book).where(Book.author.ilike(f"%{author}%"))
        result = self.session.execute(stmt)

        return result.scalars().all()

    def get_books_by_year(self, year: int):
        stmt = select(Book).where(Book.year == year)
        result = self.session.execute(stmt)

        return result.scalars().all()

    def get_books_by_genre_contain(self, genre: str):
        stmt = select(Book).where(Book.genre.ilike(f"%{genre}%"))
        result = self.session.execute(stmt)

        return result.scalars().all()

    def get_books_by_description_contain(self, description: str):
        stmt = select(Book).where(Book.description.ilike(f"%{description}%"))
        result = self.session.execute(stmt)

        return result.scalars().all()

    def get_books_by_isbn_contain(self, isbn: str):
        stmt = select(Book).where(Book.isbn.ilike(f"%{isbn}%"))
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

    def update_book(self, id, new_title, new_author, new_genre, new_description, new_year, new_isbn):
        values = {}
        if new_title: values["title"] = new_title
        if new_author: values["author"] = new_author
        if new_genre: values["genre"] = new_genre
        if new_description: values["description"] = new_description
        if new_year: values["year"] = new_year
        if new_isbn: values["isbn"] = new_isbn

        stmt = (update(Book)
                .where(Book.id == id)
                .values(
                    **values
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