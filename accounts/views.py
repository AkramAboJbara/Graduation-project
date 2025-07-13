from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from core.models import  User
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from core.serializers import UserSerializer , LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import views as auth_views , get_user_model
from django.urls import reverse, reverse_lazy
from django.views import View
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import random
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.


class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data
            user_data['token'] = token.key
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            user.logged_in = True
            user.save()
            
            token, created = Token.objects.get_or_create(user=user)
            
            user_data = UserSerializer(user).data
            user_data['token'] = token.key
            
            return Response(user_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


User = get_user_model()
class LogoutView(APIView):
    def post(self, request):
        # Get the token from the 'Authorization' header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return Response({"error": "Authorization header is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Token is in the format: 'Token <token>'
        parts = auth_header.split()

        # Ensure the header is properly formatted
        if len(parts) != 2 or parts[0].lower() != 'token':
            return Response({"error": "Invalid token format. Expected 'Token <token>'."}, status=status.HTTP_400_BAD_REQUEST)

        token = parts[1]  # Extract the token

        # Assuming each user has a unique token saved in a field like 'auth_token'
        try:
            user = User.objects.get(auth_token=token)
        except User.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is logged in
        if not getattr(user, "logged_in", True):
            return Response({"error": "User is already logged out."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark the user as logged out
        user.logged_in = False
        user.save()
        
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)




class PasswordResetRequestView(View):
    def get(self, request):
        return render(request, 'password_reset.html')

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            code = str(random.randint(100000, 999999))

            # Store in session
            request.session['reset_email'] = email
            request.session['verification_code'] = code

            # Send the code
            send_mail(
                subject='Your Verification Code',
                message=f'Your password reset verification code is: {code}',
                from_email='abomoh975@gmail.com',
                recipient_list=[email],
            )

            return redirect('verify_code')

        except User.DoesNotExist:
            return render(request, 'password_reset.html', {
                'error': 'No user with that email.'
            })

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

User = get_user_model()

class CodeVerificationView(View):
    def get(self, request):
        return render(request, 'verify_code.html')

    def post(self, request):
        input_code = request.POST.get('code')
        session_code = request.session.get('verification_code')
        email = request.session.get('reset_email')

        if input_code == session_code and email:
            try:
                user = User.objects.get(email=email)

                # Create uid and token
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # Render email template
                html_content = render_to_string('password_reset_email.html', {
                    'protocol': 'http',
                    'domain': request.get_host(),
                    'uidb64': uidb64,
                    'token': token,
                })

                # Send reset email
                msg = EmailMultiAlternatives(
                    subject='Reset Your Password',
                    body="",
                    from_email='abomoh975@gmail.com',
                    to=[email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # Optional: clean up session
                del request.session['verification_code']
                del request.session['reset_email']

                return redirect('password_reset_done')

            except User.DoesNotExist:
                return redirect('password_reset')
        else:
            return render(request, 'verify_code.html', {'error': 'Invalid code. Please try again.'})

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


authentication_classes = [TokenAuthentication]    
