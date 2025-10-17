from rest_framework import serializers
from django.db import transaction
from .models import (
    Category, Favorite, SubCategory, Service, ServicePhoto,
    SearchHistory, Review, ReviewPhoto, Chat, Message, UserSettings
)

from django.contrib.auth import get_user_model
User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'photo', 'description', 'created_at','updated_at']
        ref_name = 'ServiceCategorySerializer'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'name', 'description', 'created_at']
        ref_name = 'ServiceSubCategorySerializer'




class ServicePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePhoto
        fields = ['id', 'photo']
        read_only_fields = ['id']


class ServiceListSerializer(serializers.ModelSerializer):
    photos = ServicePhotoSerializer(many=True, read_only=True)
    subcategories = SubCategorySerializer(many=True, read_only=True)
    executor = serializers.SerializerMethodField() 

    class Meta:
        model = Service
        fields = [
            'id', 'executor', 'title', 'category', 'subcategories',
            'price', 'experience', 'phone_number', 'popularity', 'created_at', 'photos', 'currency',
        ]
        ref_name = 'ServiceListSerializer'

    def get_executor(self, obj):
        
        user = obj.executor
        if not user:
            return None

        full_name = f"{user.first_name} {user.last_name}".strip() or None

        return {
            'id': user.id,
            'username': user.username,
            'full_name': full_name,
            'role': getattr(user, 'role', None),
            'avatar': getattr(user, 'avatar', None),
            'phone_number': getattr(user, 'phone_number', None),
            'email': getattr(user, 'email', None),
        }


class ServiceDetailSerializer(serializers.ModelSerializer):
    photos = ServicePhotoSerializer(many=True, read_only=True)
    subcategories = SubCategorySerializer(many=True, read_only=True)
    executor = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['executor', 'created_at', 'updated_at', 'popularity']
        ref_name = 'ServiceDetailSerializer'

    def get_executor(self, obj):
        user = obj.executor
        if not user:
            return None

        return {
            'id': user.id,
            'username': user.username,
            'full_name': getattr(user, 'full_name', None),
            'role': getattr(user, 'role', None),
            'avatar': getattr(user, 'avatar', None),
            'phone_number': getattr(user, 'phone_number', None),
            'email': getattr(user, 'email', None),
        }

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj in user.favorites.all()


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    subcategories = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), many=True)

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'category', 'subcategories', 'description',
            'price', 'experience', 'phone_number', 'photos'
        ]
        ref_name = 'ServiceCreateUpdateSerializer'

    def validate_subcategories(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Максимум 5 подкатегорий")
        return value

    def validate_photos(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Минимум 1 фото")
        if len(value) > 6:
            raise serializers.ValidationError("Максимум 6 фото")
        return value

    @transaction.atomic
    def create(self, validated_data):
        photos = validated_data.pop('photos', [])
        subcategories = validated_data.pop('subcategories', [])
        user = self.context['request'].user
        service = Service.objects.create(executor=user, **validated_data)
        if subcategories:
            service.subcategories.set(subcategories)
        for p in photos:
            ServicePhoto.objects.create(service=service, photo=p)
        return service

    @transaction.atomic
    def update(self, instance, validated_data):
        photos = validated_data.pop('photos', None)
        subcategories = validated_data.pop('subcategories', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if subcategories is not None:
            instance.subcategories.set(subcategories)
        instance.save()
        if photos is not None:
            instance.photos.all().delete()
            for p in photos:
                ServicePhoto.objects.create(service=instance, photo=p)
        return instance

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'user', 'query', 'created_at']
        read_only_fields = ['user', 'created_at']
        ref_name = 'SearchHistorySerializer'



class ReviewPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewPhoto
        fields = ['id', 'photo']
        read_only_fields = ['id']
        ref_name = 'ReviewPhotoSerializer'

class ReviewSerializer(serializers.ModelSerializer):
    photos = ReviewPhotoSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'service', 'author', 'text', 'created_at', 'photos']
        read_only_fields = ['author', 'created_at']
        ref_name = 'ReviewSerializerCustom'

    def get_author(self, obj):
        a = obj.author
        return {'id': a.id, 'username': a.username}

class ReviewCreateSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.ImageField(), required=False)

    class Meta:
        model = Review
        fields = ['id', 'service', 'text', 'photos']
        read_only_fields = ['id']
        ref_name = 'ReviewCreateSerializer'

    def validate_photos(self, value):
        if len(value) > 6:
            raise serializers.ValidationError("Максимум 6 фото")
        return value

    @transaction.atomic
    def create(self, validated_data):
        photos = validated_data.pop('photos', [])
        author = self.context['request'].user
        review = Review.objects.create(author=author, **validated_data)
        for p in photos:
            ReviewPhoto.objects.create(review=review, photo=p)
        return review



class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'photo', 'created_at']
        read_only_fields = ['sender', 'created_at']
        ref_name = 'MessageSerializerCustom'

    def get_sender(self, obj):
        s = obj.sender
        return {'id': s.id, 'username': s.username}

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )
    class Meta:
        model = Chat
        fields = ['id', 'participants', 'service', 'created_at', 'messages']
        read_only_fields = ['created_at']
        ref_name = 'ChatSerializerCustom'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        self.fields['participants'].queryset = get_user_model().objects.all()



class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['id', 'user', 'notifications']
        read_only_fields = ['user']
        ref_name = 'UserSettingsSerializer'

class FavoriteCreateSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ['service']

class FavoriteListSerializer(serializers.ModelSerializer):
    service = ServiceListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'service', 'created_at']


