Video E-Commerce Web Application
This Django web application is designed for managing video content, user authentication, and e-commerce functionalities. It allows users to sign up, log in, browse video products, add them to the shopping cart, and proceed to checkout for payment. Admin users have additional privileges to manage categories, products, and users.

Features
Authentication: Users can sign up, log in, and log out using their email and password. Account activation is done via OTP sent to the user's email.

User Roles: The application supports different user roles, including regular users and admin users. Admin users have additional privileges for managing categories, products, and users.

Product Management: Admin users can add, edit, and delete video products. Each product includes details such as name, description, price, category, and availability status.

Category Management: Admin users can manage categories for organizing video products. They can add, edit, and delete categories.

Shopping Cart: Users can add video products to their shopping cart and view the items in their cart. They can also remove items from the cart.

Checkout: Users can proceed to checkout from their shopping cart. Payment integration is done via the Paytm payment gateway.

Email Verification: Functionality for sending OTPs to users' email addresses for account verification and password reset.

Installation
Clone the repository:


git clone <repository_url>
Install dependencies:


pip install -r requirements.txt
Apply migrations:


python manage.py migrate
Run the development server:


python manage.py runserver
Access the application at http://localhost:8000

Usage
Visit the homepage to browse video products and sign up/log in to access additional features.
Admin users can manage categories and products from the admin panel (/admin).
Add video products to the shopping cart and proceed to checkout for payment.
Regular users can view their orders and manage their account settings.
Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvement, please open an issue or submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.
