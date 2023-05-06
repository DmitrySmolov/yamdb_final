from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User

SCORE_CHOICES = [(i, str(i)) for i in range(1, 11)]


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Категория',
        help_text='Название категории, к которой относится произведение',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
        help_text='Уникальный фрагмент URL-адреса',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Жанр',
        help_text='Название жанра, к которому относится произведение'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
        help_text='Уникальный фрагмент URL-адреса'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Жанр',
        verbose_name_plural = 'Жанры'

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Произведение',
        help_text='Название произведения'
    )
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1600),
            MaxValueValidator(datetime.now().year),
        ],
        verbose_name='Год',
        help_text='Используйте формат для года <YYYY>',
        db_index=True
    )
    description = models.TextField(
        max_length=2000,
        verbose_name='Описание',
        help_text='Краткое содержание произведения',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        'Genre',
        related_name='titles',
        through='GenreTitle',
        verbose_name='Жанр',
        help_text='Название жанра, к которому относится произведение',
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Категория',
        help_text='Название категории, к которому относится произведение',
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class CreatedModel(models.Model):
    pub_date = models.DateTimeField(
        'дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Произведение',
    )
    genre = models.ForeignKey(
        Genre,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='genres',
        verbose_name='Жанр',
    )

    class Meta:
        ordering = ('title', 'genre')
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(CreatedModel):
    text = models.TextField(
        verbose_name='текст отзыва',
        help_text='Введите текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор'
    )
    score = models.PositiveSmallIntegerField(
        choices=SCORE_CHOICES,
        verbose_name='оценка',
        help_text='Дайте оценку произведению от 1 до 10'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review_per_author_title'
            ),
        )

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    text = models.TextField(
        verbose_name='текст комментария',
        help_text='Введите текст комментария'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return self.text[:15]
