from sqlalchemy import DECIMAL, Boolean, Float, Numeric, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from db import db


class Book(db.Model):
      id = mapped_column(Integer, primary_key=True)
      title = mapped_column(String)
      price = mapped_column(DECIMAL(10, 2))
      available = mapped_column(Integer, default=0)
      rating = mapped_column(Integer, default=0)
      upc = mapped_column(String, default=0)
      url = mapped_column(String, default=0)
      category = mapped_column(String, default=0)
      category_id = mapped_column(Integer, ForeignKey("category.id"))
      category = relationship("Category", back_populates="books")
      rentals = relationship("BookRental", back_populates="book")
      def to_dict(self):
            return {
                  "id": self.id,
                  "title": self.title,
                  "price": float(self.price),
                  "available": int(self.available),
                  "rating": float(self.rating),
                  "upc": self.upc,
                  "url": self.url,
                  "category": self.category.name
            }

class Category(db.Model):
      id = mapped_column(Integer, primary_key=True)
      name = mapped_column(String)
      books = relationship("Book", back_populates="category")

class User(db.Model):
      name = mapped_column(String)
      id = mapped_column(Integer, primary_key=True)
      rented = relationship("BookRental", back_populates="user")

class BookRental(db.Model):
      id = mapped_column(Integer, primary_key=True)
      user_id = mapped_column(Integer, ForeignKey("user.id"))
      book_id = mapped_column(Integer, ForeignKey("book.id"))
      rented = mapped_column(DateTime(timezone=True), nullable=False)
      returned = mapped_column(DateTime(timezone=True), nullable=True)
      user = relationship("User", back_populates="rented")
      book = relationship("Book", back_populates="rentals")
      def to_dict(self):
            return {
                  "id": self.id,
                  "user": self.user.name,
                  "book": self.book.title,
                  "rented": self.rented,
                  "returned": self.returned
            }
