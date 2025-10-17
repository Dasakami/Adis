from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PhoneVerificationCode
from .utils import send_sms_code_to_number

User = get_user_model()

def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class UserSerializer(serializers.ModelSerializer):
    favorites = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'first_name', 'last_name', 'role', 'is_phone_verified', 'favorites', 'location']
        read_only_fields = ['is_phone_verified', 'favorites']
        ref_name = "UserSerializerCustom"

class UserReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'first_name', 'last_name', 'role', 'is_phone_verified', 'location']
        read_only_fields = fields



class RegisterEmailSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        user.is_email_verified = True 
        user.save()
        return user

class SendPhoneCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        send_sms_code_to_number(phone_number)
        return {'phone_number': phone_number}


class VerifyPhoneCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, data):
        phone = data['phone_number']
        code = data['code']
        qs = PhoneVerificationCode.objects.filter(phone_number=phone, code=code, is_used=False).order_by('-created_at')
        if not qs.exists():
            raise serializers.ValidationError("Неверный код")
        code_obj = qs.first()
        if code_obj.is_expired():
            raise serializers.ValidationError("Код просрочен")
        data['code_obj'] = code_obj
        return data

    def create(self, validated_data):
        code_obj = validated_data['code_obj']
        phone = validated_data['phone_number']
        user, created = User.objects.get_or_create(phone_number=phone, defaults={'is_phone_verified': True})
        if not user.is_phone_verified:
            user.is_phone_verified = True
            user.save()
        code_obj.is_used = True
        code_obj.save()
        return user

class LoginEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")
        data['user'] = user
        return data

class SetRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
