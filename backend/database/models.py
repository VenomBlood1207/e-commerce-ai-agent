"""
SQLAlchemy models for the e-commerce database
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Order(Base):
    """Orders table model"""
    __tablename__ = "orders"
    
    order_id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    order_status = Column(String)
    order_purchase_timestamp = Column(DateTime)
    order_approved_at = Column(DateTime)
    order_delivered_carrier_date = Column(DateTime)
    order_delivered_customer_date = Column(DateTime)
    order_estimated_delivery_date = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("OrderPayment", back_populates="order")
    reviews = relationship("OrderReview", back_populates="order")

class OrderItem(Base):
    """Order items table model"""
    __tablename__ = "order_items"
    
    order_id = Column(String, ForeignKey("orders.order_id"), primary_key=True)
    order_item_id = Column(Integer, primary_key=True)
    product_id = Column(String, ForeignKey("products.product_id"))
    seller_id = Column(String, ForeignKey("sellers.seller_id"))
    shipping_limit_date = Column(DateTime)
    price = Column(Float)
    freight_value = Column(Float)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    seller = relationship("Seller", back_populates="order_items")

class OrderPayment(Base):
    """Order payments table model"""
    __tablename__ = "order_payments"
    
    order_id = Column(String, ForeignKey("orders.order_id"), primary_key=True)
    payment_sequential = Column(Integer, primary_key=True)
    payment_type = Column(String)
    payment_installments = Column(Integer)
    payment_value = Column(Float)
    
    # Relationships
    order = relationship("Order", back_populates="payments")

class OrderReview(Base):
    """Order reviews table model"""
    __tablename__ = "order_reviews"
    
    review_id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.order_id"))
    review_score = Column(Integer)
    review_comment_title = Column(Text)
    review_comment_message = Column(Text)
    review_creation_date = Column(DateTime)
    review_answer_timestamp = Column(DateTime)
    
    # Relationships
    order = relationship("Order", back_populates="reviews")

class Customer(Base):
    """Customers table model"""
    __tablename__ = "customers"
    
    customer_id = Column(String, primary_key=True)
    customer_unique_id = Column(String)
    customer_zip_code_prefix = Column(String)
    customer_city = Column(String)
    customer_state = Column(String)
    
    # Relationships
    orders = relationship("Order", back_populates="customer")

class Seller(Base):
    """Sellers table model"""
    __tablename__ = "sellers"
    
    seller_id = Column(String, primary_key=True)
    seller_zip_code_prefix = Column(String)
    seller_city = Column(String)
    seller_state = Column(String)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="seller")

class Product(Base):
    """Products table model"""
    __tablename__ = "products"
    
    product_id = Column(String, primary_key=True)
    product_category_name = Column(String, ForeignKey("product_category_name_translation.product_category_name"))
    product_name_length = Column(Integer)
    product_description_length = Column(Integer)
    product_photos_qty = Column(Integer)
    product_weight_g = Column(Float)
    product_length_cm = Column(Float)
    product_height_cm = Column(Float)
    product_width_cm = Column(Float)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    category_translation = relationship("ProductCategoryTranslation", back_populates="products")

class ProductCategoryTranslation(Base):
    """Product category translations table model"""
    __tablename__ = "product_category_name_translation"
    
    product_category_name = Column(String, primary_key=True)
    product_category_name_english = Column(String)
    
    # Relationships
    products = relationship("Product", back_populates="category_translation")

class Geolocation(Base):
    """Geolocation table model"""
    __tablename__ = "geolocation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    geolocation_zip_code_prefix = Column(String)
    geolocation_lat = Column(Float)
    geolocation_lng = Column(Float)
    geolocation_city = Column(String)
    geolocation_state = Column(String)
