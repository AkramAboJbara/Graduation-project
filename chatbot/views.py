from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from openai import OpenAI
from .models import Review

client = OpenAI(
    api_key=settings.KLUSTER_API_KEY,
    base_url="https://api.kluster.ai/v1" 
)

FAQ_RESPONSES = {
    # Order Management
    "cancel order": "You can cancel your order within 2 hours of placing it through your account dashboard. After this window, your order may already be in processing. Need help? Our support team is happy to assist!",
    
    "change order": "We can modify your order within 1 hour of placement - just visit 'My Orders' in your account. Need to change the shipping address or items? Act fast! For urgent changes, contact our support team immediately.",

    "track order": "Track your package in real-time! You'll find a tracking link in your order confirmation email. Alternatively, log into your account and visit 'Order History' for the latest shipping updates.",

    # Returns & Refunds
    "return policy": "Our hassle-free return policy gives you 30 days to return most items. For a smooth return: items must be unused, in original packaging with tags attached. Some exclusions apply - see our full policy for details.",

    "how to return": "Starting a return is easy! 1) Contact us at returns@example.com or call (123) 456-7890 2) We'll email you a prepaid return label 3) Pack your item securely and drop it off. Simple!",

    "refund policy": "We process refunds within 3-5 business days after receiving your return. You'll receive an email confirmation once completed. Refunds typically appear in your account within 5-7 business days, depending on your payment method.",

    "exchange policy": "Currently, we don't offer direct exchanges. We recommend returning the item (free within 30 days) and placing a new order. This ensures you get your preferred item as quickly as possible!",

    # Payments & Shipping
    "payment methods": "We accept all major payment options for your convenience: Visa, Mastercard, American Express, Discover, PayPal, Apple Pay, Google Pay, and secure bank transfers.",

    "shipping time": """
    Here's our standard shipping timeline:
    - Standard: 3-5 business days (free on orders $50+)
    - Express: 2 business days ($9.99)
    - Overnight: Next business day ($19.99)
    International orders typically arrive within 7-14 business days.""",

    "shipping cost": """
    Our shipping rates:
    - Free for orders over $50
    - Standard: $4.99 (3-5 days)
    - Express: $9.99 (2 days)
    - Overnight: $19.99 (next day)
    Rates are calculated at checkout based on your location and cart contents.""",

    # Customer Support
    "contact support": """
    We're here to help! Reach us through:
    📧 Email: support@example.com 
    📞 Phone: (123) 456-7890
    💬 Live Chat: Available on our website
    Hours: Monday-Friday, 9AM-6PM EST
    Average response time: Under 2 hours!""",

    "opening hours": """
    Our customer care hours:
    Monday-Friday: 9:00 AM - 6:00 PM EST
    Saturday: 10:00 AM - 4:00 PM EST
    Sunday: Closed
    Holiday hours may vary - we'll notify you in advance!""",

    # Account Management
    "create account": "Join our community in just 30 seconds! Click 'Sign Up' at the top right corner. Benefits include: faster checkout, order tracking, exclusive deals, and personalized recommendations.",

    "reset password": "Forgot your password? No worries! Click 'Forgot Password' on the login page, enter your email, and we'll send a secure reset link valid for 24 hours. Can't find it? Check your spam folder!",

    # Policies
    "privacy policy": "Your privacy matters to us. We strictly protect your personal information and never share or sell customer data. For complete details, visit our Privacy Policy page on the website.",

    "terms of service": "Our Terms of Service ensure a safe, fair shopping experience for everyone. You can review the complete terms on our website's legal section.",

    # Feedback
    "leave a review": 'We value your opinion! Share your experience with us by <a href="https://www.example.com/reviews" target="_blank" style="color: #0066cc; font-weight: 500;">leaving a review</a>. Your feedback helps us improve!',

    "leave a feedback": 'Your thoughts matter! Help us serve you better by <a href="https://www.example.com/feedback" target="_blank" style="color: #0066cc; font-weight: 500;">sharing your feedback</a>. Survey participants get 10% off their next order!',

    # Added new common questions
    "damaged item": "Oh no! We're sorry to hear that. Please contact us within 48 hours of delivery at support@example.com with photos of the damaged item and your order number. We'll make it right!",
    
    "missing item": "We apologize for the incomplete order. Please check your packing slip and email us at support@example.com with your order number and the missing item details. We'll resolve this immediately!",
    
    "price match": "We offer price matching within 7 days of purchase! Found a better price? Email us the competitor's current listing at pricematch@example.com with your order details for review.",
    
    "gift wrapping": "Yes! We offer beautiful gift wrapping for $4.99 per item. Select this option at checkout and include a personalized gift message if you'd like."
}

@csrf_exempt
def chatbot_page(request):
    return render(request, 'chatbot/chat.html')


@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip().lower()
        response = None
        for keyword, answer in FAQ_RESPONSES.items():
            if keyword in user_message:
                response = answer
                break

        if not response:
            try:
                completion = client.chat.completions.create(
                    model="klusterai/Meta-llama-3.1-8B-Instruct-Turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                response = completion.choices[0].message.content.strip()
            except Exception as e:
                response = f"Sorry, there was an error processing your request: {str(e)}"

        return JsonResponse({'response': response})

    return JsonResponse({'response': 'Invalid request'})


def review_page(request):
    return render(request, 'chatbot/review.html')

def submit_review(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')
        rating = request.POST.get('rating')

        try:
            Review.objects.create(
                email=email,
                message=message,
                rating=int(rating)
            )
            html_response = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <title>Thank You</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
                <style>
                    body {
                        font-family: 'Inter', sans-serif;
                        background: linear-gradient(to right, #e0ecff, #f7f9fc);    
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #333;
                    }
                    .thankyou-container {
                        background: white;
                        padding: 40px;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                        max-width: 400px;
                        text-align: center;
                        animation: fadeIn 0.8s ease-in-out;
                    }
                    h2 {
                        color: #28a745;
                        margin-bottom: 15px;
                    }
                    p {
                        font-size: 16px;
                        margin-bottom: 25px;
                        color: #555;
                    }
                    .btn-back {
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: 600;
                        transition: background-color 0.3s;
                    }
                    .btn-back:hover {
                        background-color: #0056b3;
                    }
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                </style>
            </head>
            <body>
                <div class="thankyou-container">
                    <h2>Thank You!</h2>
                    <p>We appreciate your feedback and will use it to improve our service.</p>
                    <a href="" class="btn-back">Back to Chat</a>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html_response)

        except Exception as e:
            return HttpResponse(f"<h3>Error submitting review: {str(e)}</h3><br><a href='/review/' class='btn-back'>Try Again</a>")

    return redirect('chatbot_page')

def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')  # latest first
    return render(request, 'review_list.html', {'reviews': reviews})