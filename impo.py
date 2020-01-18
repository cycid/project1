import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://efywljzbctnors:1163807423bed5e3b9e21e470bdab0b4e1721147755110f4b73851df62bb6a29@ec2-176-34-184-174.eu-west-1.compute.amazonaws.com:5432/dapnjtf2ckbqbq")
db = scoped_session(sessionmaker(bind=engine))

db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR UNIQUE, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR)");
def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year":year})
        
    db.commit()

if __name__ == "__main__":
    main()
#CREATE TABLE reviews(isbn VARCHAR NOT NULL, users VARCHAR NOT NULL, text VARCHAR NOT NULL, rating INTEGER)
0385537131
key: LMkmCT1hycZRWqvDAZnmJA