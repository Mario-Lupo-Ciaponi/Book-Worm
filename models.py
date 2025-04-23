from sqlalchemy import create_engine, Integer, String, Text
from sqlalchemy.orm import declarative_base, declared_attr, Mapped, mapped_column


connection_string = (
    "postgresql+psycopg2://postgres:Ps1029384756,.@localhost/book_worm_db"
)
engine = create_engine(connection_string)


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s" if cls.__name__.lower()[-1] not in ["s", "x", "z", "ch", "sh"] \
            else cls.__name__.lower() + "es"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )


Base = declarative_base(cls=Base)


class Book(Base):
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    author: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    genre: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    isbn: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
