from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from openai import OpenAI

client = OpenAI(
    api_key=settings.KLUSTER_API_KEY,
    base_url="https://api.kluster.ai/v1"
)

def chatbot_page(request):
    return render(request, 'chatbot/chat.html')


def chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')

        try:
            completion = client.chat.completions.create(
                model="klusterai/Meta-llama-3.1-8B-Instruct-Turbo",
                messages=[{"role": "user", "content": user_message}]
            )
            answer = completion.choices[0].message.content.strip()
            return JsonResponse({'response': answer})
        except Exception as e:
            return JsonResponse({'response': f'Error: {str(e)}'})

    return JsonResponse({'response': 'Invalid request'})