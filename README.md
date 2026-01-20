# Product & Cart Management API – Backend Assignment
## Overview

The Product & Cart Management API is an extension of the User Management API, which allows for product browsing and user purchasing behavior. The system is designed to handle a variety of tasks related to products, user cart functionality, and wishlists. It supports Admin and User access to manage products, carts, and wishlists.

# Key Features

** Admin Product Management: Admin users can create, read, update, and delete products in the system.

** User Product Access: Authenticated users can browse available products and view detailed product information.

** Cart Functionality: Users can add, remove, and manage items in their shopping cart.

** Wishlist Management: Users can create and maintain a personal wishlist that persists across sessions.
 
** User Management: Includes user signup, login, OTP verification, password reset, and user profile management.
 
** Admin Panel: Admin users can manage user accounts, including viewing, creating, editing, and blocking users.

# Tech Stack

The Product & Cart Management API is built using the following technologies:

** Backend Framework: Django

** Database: PostgreSQL

** Authentication: Session-based Authentication
 
** Environment: Python 3.x, Django 4.x, PostgreSQL 12.x

# Features
1. Product Management (Admin Access)

Create Product: Admins can add new products, including details such as name, description, price, stock, and category.

Edit Product: Admins can edit product information like name, description, price, and stock.

Delete Product: Admins can delete products from the database.

View Products: Admins can view all available products with detailed information.

2. Product Access (User Access)

View Products: Authenticated users can browse and view all products available in the system.

View Product Details: Users can view detailed product information (price, description, stock, etc.).

3. Cart Functionality (User Access)

Add to Cart: Authenticated users can add items to their cart, specifying product quantity.

Remove from Cart: Users can remove items from their cart.

View Cart: Users can view their current cart, including product details, quantities, and total price.

Persist Cart Data: Cart data is user-specific and persists between sessions.

4. Wishlist Functionality

Add to Wishlist: Users can add products to their wishlist.

Remove from Wishlist: Users can remove items from their wishlist.

View Wishlist: Users can view the products they have added to their wishlist.

Persist Wishlist Data: Wishlist data is saved and available across sessions.

5. User Management

Signup & OTP Verification: Users can sign up with their email, and an OTP is sent for verification.

Login & Authentication: Users can log in and manage sessions securely.

Forgot Password: Users can reset their password using an OTP sent to their email.

Edit Profile: Users can update their profile information, such as username and email.

6. Admin Panel

Admin Login: Admins can securely log into the system.

View All Users: Admins can view a list of all users and search user data.

Create, Edit, Block Users: Admins can create new users, update their details, and block users who should no longer have access.