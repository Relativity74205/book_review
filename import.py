import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

os.environ['DATABASE_URL'] = 'postgres://raumlabbqsxywy:6674bc8e5852944795a65cc1e64f9e7fb0d5a999ade53a25e25924c2800aa6d2@ec2-79-125-127-60.eu-west-1.compute.amazonaws.com:5432/d3hihjkblo9bam'
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def read_data():
    data = []
    file = open('books.csv')

    csv_reader = csv.reader(file, delimiter=',')
    for row in csv_reader:
        data.append(row)

    header = data.pop(0)

    return header, data


def create_table():
    metadata = MetaData()
    books = Table('book', metadata,
                  Column('book_id', Integer, primary_key=True),
                  Column('isbn', String),
                  Column('title', String),
                  Column('author', String),
                  Column('year', Integer),
                  )
    user = Table('user', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('username', String),
                 Column('password_hashed', String))
    review = Table('review', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('review_points', Integer),
                   Column('review_text', String),
                   Column('book_id', Integer),
                   Column('user_id', Integer))
    metadata.create_all(engine)


def insert_data(header, data):
    for values in data:
        values = [int(value) if value.isdigit() else value for value in values]
        entry = dict(zip(header, values))
        db.execute('INSERT INTO book(isbn, title, author, year) '
                   'VALUES (:isbn, :title, :author, :year)', entry)
    db.commit()


def main():
    header, data = read_data()
    create_table()
    insert_data(header, data)


if __name__ == '__main__':
    main()
