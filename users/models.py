from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if not email and not phone_number:
            raise ValueError("Укажите email или телефон")
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not email:
            raise ValueError("Superuser должен иметь email")
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [('executor', 'Исполнитель'), ('client', 'Заказчик')]

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    favorites = models.ManyToManyField('services.Service', blank=True, related_name='favorited_by')

    objects = UserManager()

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []   

    def save(self, *args, **kwargs):
        if not self.username:
            base_username = f"{self.first_name}.{self.last_name}".lower() if self.first_name and self.last_name else f"user{self.pk}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.phone_number or str(self.pk)


class PhoneVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_codes', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 300  # 5 минут
