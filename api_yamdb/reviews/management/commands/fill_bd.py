import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.management.commands import func_csv

BASE_DIR = settings.BASE_DIR

csv_to_func = {
    'category.csv': func_csv.category_create,
    'genre.csv': func_csv.genre_create,
    'titles.csv': func_csv.titles_create,
    'users.csv': func_csv.users_create,
    'review.csv': func_csv.review_create,
    'comments.csv': func_csv.comments_create,
    'genre_title.csv': func_csv.genre_title_create,
}


class Command(BaseCommand):
    help = 'Загружает данные из CSV-файла (.../static/data/)'

    def handle(self, *args, **options):
        for filename, row in csv_to_func.items():
            path = os.path.join(BASE_DIR, 'static/data/') + filename
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    csv_to_func[filename](row)
        self.stdout.write('Запись прошла успешно...')
