🛒 Ecommerce Website – Django + Stripe
A full-featured eCommerce web application built using Django for the backend and Stripe API for secure payment processing. The project includes a product catalog, shopping cart, user authentication, order tracking, and responsive design with Bootstrap.

🔧 Features
User Authentication: Secure login and signup functionality.

Product Browsing: Display products with the ability to select quantity (1-10).

Cart Management: Add products to cart, update quantities, and delete items.

Order Summary: Display item details, quantities, and pricing before checkout.

Stripe Checkout: Integration with Stripe API to process secure payments.

Order History: View past orders with delivery status updates.

Responsive UI: Mobile-friendly design using Bootstrap for all devices.

⚙️ Tech Stack
Backend: Django

Frontend: HTML, CSS, JavaScript, Bootstrap

Payment Gateway: Stripe API

Database: MySQL (configurable)

Environment: .env for secure configuration

🚀 Getting Started
To run the project locally, follow these steps:

1. Clone the repository
bash
Copy
Edit
git clone https://github.com/ROHITT0406/Ecommerce-website.git
cd ecommerce-django-stripe
2. Install dependencies
Make sure you have Python 3.x installed. Then install the required packages:

bash
Copy
Edit
pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file in the root of the project and add your environment variables:

bash
Copy
Edit
SECRET_KEY=your-secret-key
DEBUG=True
STRIPE_TEST_SECRET_KEY=your-stripe-secret-key
STRIPE_TEST_PUBLISHABLE_KEY=your-stripe-publishable-key
DATABASE_URL=sqlite:///db.sqlite3  # or PostgreSQL URL
4. Migrate the database
Run the following command to apply the migrations:

bash
Copy
Edit
python manage.py migrate
5. Run the development server
Start the Django development server:

bash
Copy
Edit
python manage.py runserver
Visit http://127.0.0.1:8000/ in your browser to see the application in action.

