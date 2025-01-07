from flask import Flask, render_template, request, jsonify
from pathlib import Path
from db import db
from models import Book
from models import User
from models import BookRental
from models import Category
from datetime import datetime

app = Flask(__name__)
# This will make Flask use a 'sqlite' database with the filename provided
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask_book.db"
# This will make Flask store the database file in the path provided
app.instance_path = Path(".").resolve()
db.init_app(app)


# @app.route("/")
# def home():
#       return render_template("home.html")


@app.route("/")
def home():
 return jsonify({"a": [1, 23, 56], "b": "hello"})


@app.route("/books")
def books():
      statement = db.select(Book).order_by(Book.id)
      records = db.session.execute(statement)
      books = records.scalars()
      if not books:
            return "NOT FOUND!", 404 
      return render_template("books.html", books = books)
@app.route("/books/<int:id>")
def book_rental(id):
      statement = db.select(Book).where(Book.id == id)
      records = db.session.execute(statement)
      books = records.scalar()
      if not books:
            return "NOT FOUND!", 404 
      return render_template("book_rental.html", book = books)

@app.route("/available")
def books_available():
      book_ids_stmt = db.select(BookRental.book_id).where(BookRental.rented < datetime.now()).where(BookRental.returned == None)
      book_ids = [id for id in db.session.execute(book_ids_stmt).scalars()]
      never_rented_books_stmt = db.select(Book).where(Book.id.notin_(book_ids)).order_by(Book.title)
      books = db.session.execute(never_rented_books_stmt).scalars()
      if not books:
            return "NOT FOUND!", 404 
      return render_template("books.html", books = books)

@app.route("/rented")
def books_rented():
      book_ids_stmt = db.select(BookRental.book_id).where(BookRental.rented < datetime.now()).where(BookRental.returned == None)
      book_ids = [id for id in db.session.execute(book_ids_stmt).scalars()]
      # We can now use `.in_` to select objects with IDs in a list of values
      ordered_books_stmt = db.select(Book).where(Book.id.in_(book_ids)).order_by(Book.title)
      books = db.session.execute(ordered_books_stmt).scalars()
      if not books:
            return "NOT FOUND!", 404  
      return render_template("books.html", books = books)


@app.route("/users")
def users():
      statement = db.select(User).order_by(User.name)
      records = db.session.execute(statement)
      results = records.scalars()
      if not results:
            return "NOT FOUND!", 404  
      return render_template("users.html", users = results)

@app.route("/users/<int:id>")
def user_rental(id):
      statement = db.select(User).where(User.id == id)
      results = db.session.execute(statement).scalar()
      if not results:
            return "NOT FOUND!", 404    
      return render_template("user_rental.html", user = results)

@app.route("/category")
def category():
      statement = db.select(Category).order_by(Category.name)
      records = db.session.execute(statement)
      results = records.scalars()
      if not results:
            return "NOT FOUND!", 404  
      return render_template("category.html", categories = results)

@app.route("/category/<string:name>")
def category_detail(name):
      statement = db.select(Book).where(Book.category.has(Category.name == name))
      results = db.session.execute(statement).scalars()
      if not results:
            return "NOT FOUND!", 404  
      return render_template("books.html", books = results)

@app.route("/api/books")
def api_books():
      statement = db.select(Book).order_by(Book.title)
      records = db.session.execute(statement)
      books = records.scalars()
      books_list = []
      if not books:
            return "NOT FOUND!", 404 
      for book in books:
            books_list.append(book.to_dict())

      return  jsonify(books_list)

@app.route("/api/books/<int:id>")
def api_book(id):
      statement = db.select(Book).where(Book.id == id)
      records = db.session.execute(statement)
      book = records.scalar()
      
      if not book:
            return "NOT FOUND!", 404
      book_updated = book.to_dict()

      # rent_stmt = db.select(BookRental).where(BookRental.book_id == id)
      # rent_records = db.session.execute(rent_stmt).scalars()
      rent_records = book.rentals
      sum_rented = 0
      sum_returned = 0
      for rent in rent_records:
            if rent.rented:
                  sum_rented += 1
            if rent.returned:
                  sum_returned += 1
      if sum_rented == sum_returned:
            book_updated["available"] = True
      else:
            book_updated["available"] = False
      return  jsonify(book_updated)

@app.route("/api/books", methods=["POST"])
def create_book():
      data = request.get_json()
      # Validation functions
      is_positive_number = lambda num: isinstance(num, (int, float)) and num >= 0
      is_non_empty_string = lambda s: isinstance(s, str) and len(s) > 0
      is_valid_rating = lambda num: isinstance(num, int) and 1 <= num <= 5
      # Field mapping
      required_fields = {
      "title": is_non_empty_string,
      "price": is_positive_number,
      "available": is_positive_number,
      "rating": is_valid_rating,
      "url": is_non_empty_string,
      "upc": is_non_empty_string,
      "category": is_non_empty_string,
      }

      # Field validation
      for field in required_fields:
      # The field is missing
            if field not in data:
                  return {"error": f"Missing field: {field}"}, 400
            else:
                  # Extract the validation function
                  func = required_fields[field]
                  # Extract the value
                  value = data[field]
                  # Validate the value
                  if not func(value):
                        return {"error": f"Invalid value for field {field}: {value}"}, 400
      category = db.session.execute(db.select(Category).where(Category.name == data["category"])).scalar()
      if not category:
            category = Category(name = data["category"])
            db.session.add(category)
      
      book = db.session.execute(db.select(Book).where(Book.title == data["title"])).scalar()
      if book:
            return "Book existed", 403
      new_book = Book(title = data["title"], price = data["price"], available = data["available"], rating = data["rating"], url = data["url"], upc = data["upc"], category = category )
      db.session.add(new_book)
      db.session.commit()

      statement = db.select(Book).where(Book.title == data["title"])
      records = db.session.execute(statement)
      book_added = records.scalar().to_dict()
      return jsonify(book_added)

@app.route("/api/books/<int:id>/rent", methods=["POST"])
def create_book_rental(id):
      data = request.get_json()
      user = db.session.execute(db.select(User).where(User.id == data["user_id"])).scalar()
      if not user:
            return "No such user!", 403
      book = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
      if not book:
            return "NOT FOUND!", 404

      rent_records = book.rentals
      sum_rented = 0
      sum_returned = 0
      for rent in rent_records:
            if rent.rented:
                  sum_rented += 1
            if rent.returned:
                  sum_returned += 1
      if sum_rented != sum_returned:
            return "Rented!", 403
      
      new_rental = BookRental(user=user, book=book, rented=datetime.now(), returned=None)
      db.session.add(new_rental)
      db.session.commit()

      return jsonify(new_rental.to_dict())

@app.route("/api/books/<int:id>/return", methods=["PUT"])
def create_book_return(id):
      book = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
      if not book:
            return "NOT FOUND!", 404
      rent_records = book.rentals
      sum_rented = 0
      sum_returned = 0
      for rent in rent_records:
            if rent.rented:
                  sum_rented += 1
            if rent.returned:
                  sum_returned += 1
      if sum_rented == sum_returned:
            return "The Book is not rented!", 403
      for rent in rent_records:
            if not rent.returned:
                  rent.returned = datetime.now()
                  db.session.add(rent)
                  db.session.commit()
            else:
                  pass
      
      rent_records_dict = [rent.to_dict() for rent in rent_records]

      return jsonify(rent_records_dict)
      


if __name__ == "__main__":
      app.run(debug=True, port=8500)