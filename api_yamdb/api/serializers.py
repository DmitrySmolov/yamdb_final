import re

from django.core.exceptions import ValidationError
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    genre = GenreSerializer(many=True, required=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title

    def get_rating(self, obj):
        return obj.reviews.aggregate(Avg('score'))['score__avg']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        action = self.context['view'].action
        if action not in ['list', 'retrieve']:
            representation.pop('rating')
        return representation


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title


class AdminUserSerializer(serializers.ModelSerializer):
    """Сериализатор Администратора."""
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=154,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username', },
        }
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'username не может быть "me"'
            )
        pattern = r'^[\w.@+-]+\Z'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                r'Поле "username" дожно содержать символы: ^[\w.@+-]+\z'
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    username = serializers.RegexField(
        r'^[\w.@+-]+\Z',
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)
        model = User
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username', },
        }
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('username не может быть "me"')
        return value


class ConfirmationCodeSerializer(serializers.ModelSerializer):
    """Сериализатор получения кода подтверждения."""
    username = serializers.RegexField(
        r'^[\w.@+-]+\Z',
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = ('email', 'username')
        model = User
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'username не может быть "me"'
            )
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор получения токена."""
    username = serializers.CharField(
        max_length=150,
        write_only=True
    )
    confirmation_code = serializers.CharField(
        max_length=255,
        write_only=True
    )

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        user1 = User.objects.filter(
            username=user.username,
            confirmation_code=data['confirmation_code']
        ).exists()
        if not user1:
            raise serializers.ValidationError(
                'Нет такого пользователя'
            )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    pub_date = serializers.DateTimeField(
        read_only=True
    )
    score = serializers.IntegerField(
        min_value=1,
        max_value=10,
        error_messages={
            'min_value': 'Оценка не может быть меньше 1 балла.',
            'max_value': 'Оценка не может быть выше 10 баллов.'
        }
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title_id, author=author).exists()
        ):
            raise ValidationError(
                'Вы уже публиковали отзыв на данное произведение.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    pub_date = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
