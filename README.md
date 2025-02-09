#  Our Product Vision
**FOR** businesses and entrepreneurs **WHO** need a simple and efficient way to sell products online,
**THE** Online Shop Simulation is an interactive e-commerce platform **THAT** demonstrates essential online store functions, from product browsing to secure checkout.
**UNLIKE** complex enterprise e-commerce solutions, the focus of our product is to provide a clear, hands-on simulation of core e-commerce operations,
**OUR** platform enables users to explore customer experiences, backend management, and real-time updates, making it easier for businesses to understand the key components of a successful online store.


# User Stories

## Types of users:

* Individuals who need Sell he's own Product  (**Seller**)
* Individuals who are willing to Buying anu product (**Customer**)


### Authentication

* **As a** user **I want to** Sign up to the platform  using my email
* **As a** user **I want to** Sign up using Google account
* **As a** user **I want to** Login using credintials (email and password)
* **As a** user **I want to** Login using Google account
* **As a** user **I want to** Reset password using email
* **As a** user **I want to** Logout from the website


## Seller Stories

* **As a** Seller **I want to** manage product inventory **so that** I can keep track of stock availability and avoid overselling.  
* **As a** Seller **I want to** receive payment confirmations **so that** I can verify transactions before shipping products.  
* **As a** Seller **I want to** update product details, including descriptions, images, and prices **so that** customers can make informed purchase decisions.  
* **As a** Seller **I want to** access sales reports and analytics **so that** I can track performance and make data-driven business decisions.  
* **As a** Seller **I want to** set up product filters and categories **so that** customers can easily find the products they need.  
* **As a** Seller **I want to** manage customer inquiries and support requests **so that** I can address their concerns and improve satisfaction.  


## Customer Stories

* **As a** Customer **I want to** be able to view my profile.
* **As a** Customer **I want to** be able to add and edit my personal information.
* **As a** Customer **I want to** have the ability to reset my password.
* **As a** Customer **I want to** browse and search for products **so that** I can find items that match my needs easily.  
* **As a** Customer **I want to** filter and sort products based on different attributes **so that** I can quickly narrow down my choices.  
* **As a** Customer **I want to** add products to my shopping cart **so that** I can review and purchase multiple items at once.  
* **As a** Customer **I want to** securely complete my purchase through a streamlined checkout process **so that** I can confidently place my order.  
* **As a** Customer **I want to** receive real-time stock availability updates **so that** I know if a product is in stock before purchasing.  
* **As a** Customer **I want to** get order confirmation **so that** I can stay informed about my purchase status.  
* **As a** Customer **I want to** create an account and save my preferences **so that** I can have a personalized shopping experience.  
* **[TBD]** **As a** Customer **I want to** leave reviews and ratings on products **so that** I can help other buyers make informed decisions.  



# Set Up Virtual Environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

Start Django Project:
django-admin startproject ecommerce_backend .

Create an App (core):
python manage.py startapp core

#to link the front in settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Frontend or other origins
]
 

## remove files and folders from tracking

to remove files and folders that in gitignorefrom tracking run this command

```bash
git rm -r --cached .
```
