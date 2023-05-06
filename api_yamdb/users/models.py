from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Модель для работы с пользователями"""
    CHOICES = (

        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),

    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z')])
    email = models.EmailField(
        verbose_name='email адрес',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=15, choices=CHOICES, default='user')
    confirmation_code = models.CharField(
        max_length=255, blank=True, null=True
    )
    password = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'username'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name="unique_fields"
            ),
        ]

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __str__(self) -> str:
        return self.username
