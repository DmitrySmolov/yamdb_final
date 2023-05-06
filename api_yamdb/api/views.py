from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.permissions import (IsAdminOrSuperuserPermission,
                             ReviewPermission,
                             TitlePermission,)
from api.serializers import (AdminUserSerializer,
                             CategorySerializer,
                             ConfirmationCodeSerializer,
                             CommentSerializer,
                             GenreSerializer,
                             ReviewSerializer,
                             TitleSerializer,
                             TokenSerializer,
                             TitleCreateSerializer,
                             UserSerializer)
from api.utils import send_email_with_verification_code
from reviews.models import Category, Genre, Review, Title
from users.models import User


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg("reviews__score")
    ).order_by("name")
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (TitlePermission,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleCreateSerializer


class CategoryViewSet(CreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (TitlePermission,)
    lookup_field = 'slug'


class GenreViewSet(CreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (TitlePermission,)
    lookup_field = 'slug'


class UserViewSet(viewsets.ModelViewSet):
    """Работа с пользователями. Только для администратора."""
    queryset = User.objects.all()
    permission_classes = (
        permissions.IsAuthenticated,
        IsAdminOrSuperuserPermission,
    )
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post',
                         'patch', 'delete')

    def get_serializer_class(self):
        if (
            self.request.user.role != 'admin'
            or self.request.user.is_superuser
        ):
            return UserSerializer
        return AdminUserSerializer

    @action(
        detail=False,
        url_path='me',
        methods=['GET', 'PATCH', 'POST'],
        permission_classes=[permissions.IsAuthenticated, ],
        queryset=User.objects.all()
    )
    def me(self, request):
        """
        Профиль пользователя. Можно редактировать.
        Поле role редактирует только администратор.
        """
        user = request.user
        if request.method == 'POST':
            return Response(
                {"detail": "Method Not Allowed"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignUpViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """Регистрация нового пользователя. Полечуние кода подтверждения."""
    queryset = User.objects.all()
    serializer_class = ConfirmationCodeSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        data = (request.data).dict()
        user = User.objects.filter(**data)
        serializer = ConfirmationCodeSerializer(data=data)
        if user.exists():
            send_email_with_verification_code(user.first())
            return Response(serializer.initial_data, status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.filter(**serializer.data)
        send_email_with_verification_code(user.first())
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(http_method_names=['POST', ])
def token(request):
    """Выдает токен авторизации."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    user = get_object_or_404(User, **data)
    refresh = RefreshToken.for_user(user)
    return Response(
        {'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED
    )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewPermission, )

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReviewPermission, )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review=review)
