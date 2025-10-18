# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
User = get_user_model()

GOOGLE_CLIENT_ID = '339282383851-r5a3uhs4rsfudl28s49uvkhh15v1ot6a.apps.googleusercontent.com'

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    token = request.data.get('id_token')
    if not token:
        return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo.get('email')
        name = idinfo.get('name')
        sub = idinfo.get('sub')  # уникальный google user id

        user, created = User.objects.get_or_create(email=email, defaults={'username': name})

        # Можно здесь генерировать JWT или DRF token
        # Пример с DRF token:
        from rest_framework.authtoken.models import Token
        token_obj, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token_obj.key, 'user_id': user.id, 'email': user.email})
    except ValueError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
