from users.models import User
from reviews.models import Category, Genre, Title, Review, Comment, GenreTitle


def category_create(row):
    Category.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def genre_create(row):
    Genre.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def titles_create(row):
    Title.objects.get_or_create(
        id=row[0],
        name=row[1],
        year=row[2],
        category_id=row[3],
    )


def users_create(row):
    User.objects.get_or_create(
        id=row[0],
        username=row[1],
        email=row[2],
        role=row[3],
        bio=row[4],
        first_name=row[5],
        last_name=row[6],
    )


def review_create(row):
    title, _ = Title.objects.get_or_create(id=row[1])
    Review.objects.get_or_create(
        id=row[0],
        title=title,
        text=row[2],
        author_id=row[3],
        score=row[4],
        pub_date=row[5]
    )


def comments_create(row):
    review, _ = Review.objects.get_or_create(id=row[1])
    Comment.objects.get_or_create(
        id=row[0],
        review=review,
        text=row[2],
        author_id=row[3],
        pub_date=row[4],
    )


def genre_title_create(row):
    title, _ = Title.objects.get_or_create(id=row[1])
    genre, _ = Genre.objects.get_or_create(id=row[2])
    GenreTitle.objects.get_or_create(
        id=row[0],
        title=title,
        genre=genre,
    )
