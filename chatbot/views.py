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
    "return policy": "You can return items within 2 days of delivery. Please make sure the item is in its original condition.",
    "refund policy": "Refunds are processed within 5–7 business days after we receive the returned item.",
    "how to return": "To return an item, you can call 'to be declared later!' > or ypu can email ee@ee.com",
    "contact support": "You can contact our support team at ee@ee.com.",
    "shipping time": "Standard shipping takes 3–5 business days. Express options are also available at checkout.",
    "payment methods": "We accept Visa, Mastercard, PayPal, Apple Pay, and Google Pay.",
    "exchange policy": "We currently do not offer direct exchanges. You may return the item and place a new order.",
    "cancel order": "Orders can be canceled within 2 hours of placing them. Please contact support if you need help.",
    "opening hours": "Our customer service is available from 9 AM to 6 PM, Monday to Friday.",
    "privacy policy": "Your privacy is important to us. Please read our full privacy policy on our website.",   
   "leave a review": 'We appreciate your feedback! Please <a href="http://127.0.0.1:8000/review" target="_blank" rel="noopener noreferrer" style="color: #007bff; text-decoration: underline;">leave a review</a>.',
    "leave a feedback": 'We appreciate your feedback! Please <a href="http://127.0.0.1:8000/review" target="_blank" rel="noopener noreferrer" style="color: #007bff; text-decoration: underline;">leave a feedback</a>.',
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