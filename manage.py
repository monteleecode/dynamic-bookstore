import csv, sys, os
from db import db
from app import app
from models import Book
from models import User
from models import BookRental
from models import Category

from sqlalchemy.sql import func
from datetime import datetime, timedelta
from random import random, randint as rndm

def import_book_and_category():
      with open("data/books.csv", "r", encoding="utf-8", errors="replace") as b:
            reader = csv.DictReader(b)
            for row in reader:
                  possible_category = db.session.execute(db.select(Category).where(Category.name ==
                  row["category"])).scalar()
                  if not possible_category:
                        category_obj = Category(name=row["category"])
                        db.session.add(category_obj)
                  else:
                        category_obj = possible_category
                  row["category"] = category_obj
                  book = Book(**row)
                  db.session.add(book)
def import_user():
      with open("data/users.csv", "r", encoding="utf-8", errors="replace") as u:
            reader = csv.DictReader(u)
            for row in reader:
                  user_obj = User(name=row["name"])            
                  db.session.add(user_obj)

def import_bookrental():
      with open("data/bookrentals.csv", "r", encoding="utf-8", errors="replace") as r:
            reader = csv.DictReader(r)
            for row in reader:
                  possible_book = db.session.execute(db.select(Book).where(Book.upc ==
                  row["book_upc"])).scalar()
                  possible_user = db.session.execute(db.select(User).where(User.name ==
                  row["user_name"])).scalar()
                  if not possible_book or not possible_user:
                        pass
                  else:
                        if not row["rented"]:
                              rented_parsed = None
                        else:
                              rented_parsed = datetime.strptime(row["rented"], "%Y-%m-%d %H:%M")
                        if not row["returned"]:
                              returned_parsed = None
                        else:
                              returned_parsed = datetime.strptime(row["returned"], "%Y-%m-%d %H:%M")

                        book_rental = BookRental(user = possible_user, book = possible_book, rented = rented_parsed, returned = returned_parsed)
                        db.session.add(book_rental)

                  


def create_rental():
      now = datetime.now()
      # A book was rented sometime between 10 days ago and 24 days and 4 hours ago
      # Minutes and seconds stay the same
      random_past_offset = timedelta(days=rndm(10, 25), hours=rndm(0, 5))
      rented_on = now - random_past_offset

      # Decide whether the book was returned (50% chance)
      returned = random() > 0.5
      # If returned, compute a random day (between 2 and 8 days after rental date)
      if not returned:
            returned_on = None
      else:
            returned_on = rented_on + timedelta(days=rndm(2, 9), hours=rndm(0, 100),
      minutes=rndm(0, 100))

      stmt = db.select(User).order_by(func.random())
      user = db.session.execute(stmt).scalar()

      book = db.session.execute(db.select(Book).where(~Book.rentals.any() | Book.rentals.any(BookRental.returned_on < datetime.now())).order_by(func.random())).scalar()
      br = BookRental(user=user, book=book, rented=rented_on, returned=returned_on)
      db.session.add(br)

if __name__ == "__main__":

      with app.app_context():
            if len(sys.argv) > 1:
                  if sys.argv[1] == "recreate":
                        db.drop_all()
                        db.create_all()
                  if sys.argv[1] == "import":
                        import_user()
                        import_book_and_category()
                        import_bookrental()
                        db.session.commit()
                  # if sys.argv[1] == "rental":
                  #       if not sys.argv[2]:
                  #             raise ValueError("please give me a integer")
                  #       for i in range(int(sys.argv[2])):
                  #             create_rental()
                  #       db.session.commit()


                        
                        
                        

