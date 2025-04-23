from sqlalchemy import insert, select
from sqlalchemy.orm import sessionmaker

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


def instruction():
    print("Actions:\n1) Add book;\n2) See added books\n3) Quit\n")

def main():
    print("Hello and welcome!\n")

    instruction()

    while True:
        try:
            option = int(input("Your option(e.g. '1', '2' and ect.): "))
        except ValueError:
            print("The input must be an input!")
        else:
            if 0 > option or option > 3:
                print("The input must be between 1 and 3!")
                continue
            if option == 1:
                print()

                try:
                    title = input("Title: ")
                    author = input("Author: ")
                    genre = input("Genre: ")
                    year = input("Year(integer): ")#None,
                    isbn = input("ISBN: ") #None,
                    description = input("Description: ") #None

                    year = int(year) if year else None
                    isbn = isbn if isbn else None
                    description = description if description else None
                except ValueError:
                    print("Year must be an integer number!")
                    continue
                else:
                    with Session() as session:
                        repo = Repo(session)

                        repo.add_book(title, author, genre, year, isbn, description)
                        print(f"'{title}' added successfully!")
            elif option == 2:
                print()

                with Session() as session:
                    repo = Repo(session)

                    books = repo.get_all_books()

                    for b in books:
                        print(f"Title: {b.title}\n"
                              f"Author: {b.author}\n"
                              f"Genre: {b.genre}\n"
                              f"Year: {b.year if b.year else 'no year'}\n"
                              f"ISBN: {b.isbn if b.isbn else 'no ISBN'}\n"
                              f"Description: {b.description if b.description else 'no description'}\n")
            else:
                break



if __name__ == "__main__":
    main()
