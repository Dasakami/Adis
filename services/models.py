from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='category_photos/')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return f'{self.name}'


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    def __str__(self):
        return f'{self.name}'

class Service(models.Model):
    EXPERIENCE_CHOICES = [
        ('0-1', 'До 1 года'),
        ('1-2', 'От 1 до 2 лет'),
        ('3-5', 'От 3 до 5 лет'),
        ('6+', 'От 6 лет и более'),
    ]
    CURRENCY_CHOICES = [
        ('SOM', 'Сом'),
        ('RUB', 'Рубль'),
        ('USD', 'Доллар'),
    ]

    executor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategories = models.ManyToManyField(SubCategory, related_name='services')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # или договорная
    experience = models.CharField(max_length=5, choices=EXPERIENCE_CHOICES)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    popularity = models.IntegerField(default=0)
    currency = models.CharField(max_length=155, choices=CURRENCY_CHOICES, default='SOM')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
    
    def __str__(self):
        return f'{self.title}'



class ServicePhoto(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='service_photos/')

    class Meta:
        verbose_name = 'Фотография услуг'
        verbose_name_plural = 'Фотография услуг'

    def __str__(self):
        return f'Фото - {self.service.title}'

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='searches')
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} искал {self.query}'
    
    class Meta:
        verbose_name = 'История поиска'
        verbose_name_plural = 'Истории поисковой системы'

class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'От {self.author.username} к {self.service.title}'

class ReviewPhoto(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='review_photos/')

class Chat(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    photo = models.ImageField(upload_to='chat_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    notifications = models.BooleanField(default=True)


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_items'  
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='favorited_services' 
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'service')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user.username} → {self.service.title}'


from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = [
        ('success', 'Успешно'),
        ('info', 'Информация'),
        ('error', 'Ошибка'),
        ('favorite', 'Добавление в избранное'),
        ('chat', 'Создание чата'),
        ('balance', 'Пополнение баланса'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Получатель'
    )

    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип уведомления'
    )

    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок уведомления',
        blank=True
    )

    message = models.TextField(
        verbose_name='Сообщение',
        blank=True
    )

    related_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_notifications',
        verbose_name='Связанный пользователь (например, кто добавил в избранное или создал чат)'
    )

    related_service = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Связанная услуга'
    )

    related_chat = models.ForeignKey(
        'Chat',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Связанный чат'
    )

    balance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Сумма пополнения'
    )

    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        base = f"[{self.get_type_display()}] для {self.user.username}"
        if self.related_user:
            base += f" от {self.related_user.username}"
        return base

    def render_content(self):
        if self.type == 'favorite':
            return {
                "title": "Вас добавили в избранное!",
                "message": f"{self.related_user.username} добавил(а) вас или вашу услугу в избранное.",
                "action": {
                    "text": "Написать",
                    "chat_id": self.related_chat.id if self.related_chat else None
                }
            }
        elif self.type == 'chat':
            return {
                "title": "Новый чат",
                "message": f"Создан новый чат между вами и {self.related_user.username}.",
                "action": {
                    "text": "Открыть чат",
                    "chat_id": self.related_chat.id if self.related_chat else None
                }
            }
        elif self.type == 'balance':
            return {
                "title": "Баланс пополнен",
                "message": f"Ваш баланс пополнен на {self.balance_amount} сом.",
                "action": None
            }
        elif self.type == 'success':
            return {"title": "Успех", "message": self.message}
        elif self.type == 'error':
            return {"title": "Ошибка", "message": self.message}
        elif self.type == 'info':
            return {"title": "Информация", "message": self.message}
        else:
            return {"title": self.title, "message": self.message}
