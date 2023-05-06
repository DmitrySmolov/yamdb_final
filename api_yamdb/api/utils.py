from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator

from api_yamdb.settings import DEFAULT_FROM_EMAIL


def generate_confirmation_code(user):
    confirmation_code = default_token_generator.make_token(user)
    return confirmation_code


def send_email_with_verification_code(user):
    user.confirmation_code = generate_confirmation_code(user)
    user.save()
    email = user.email
    username = user.username
    confirmation_code = user.confirmation_code
    send_mail(
        subject='Письмо подтверждения',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[email, ],
        message=(f'Привет, {username}! '
                 'Это письмо содержит код подтверждения. Вот он:\n'
                 f'<b>{confirmation_code}</b>.\n'
                 'Чтоб получить токен, отправьте запрос\n'
                 'с полями username и confirmation_code'
                 'на /api/v1/auth/token/.'),
    )
