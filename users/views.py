from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterEmailSerializer, SendPhoneCodeSerializer, VerifyPhoneCodeSerializer,
    LoginEmailSerializer, SetRoleSerializer, UserSerializer, tokens_for_user, UserReadOnlySerializer
)

User = get_user_model()


class RegisterEmailView(generics.CreateAPIView):
    serializer_class = RegisterEmailSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        tokens = tokens_for_user(user)
        return Response({'user': UserSerializer(user, context={'request': request}).data, 'tokens': tokens}, status=status.HTTP_201_CREATED)



class SendPhoneCodeView(generics.CreateAPIView):
    serializer_class = SendPhoneCodeSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({'detail': 'Код отправлен'}, status=status.HTTP_200_OK)


class VerifyPhoneCodeView(generics.CreateAPIView):
    serializer_class = VerifyPhoneCodeSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        tokens = tokens_for_user(user)
        return Response({'user': UserSerializer(user).data, 'tokens': tokens}, status=status.HTTP_200_OK)


class LoginEmailView(generics.GenericAPIView):
    serializer_class = LoginEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data['user']
        tokens = tokens_for_user(user)
        return Response({'user': UserSerializer(user).data, 'tokens': tokens}, status=status.HTTP_200_OK)


class SetRoleView(generics.UpdateAPIView):
    serializer_class = SetRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user



class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserReadOnlySerializer
    permission_classes = [permissions.AllowAny]