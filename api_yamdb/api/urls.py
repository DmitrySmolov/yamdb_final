from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
    UserViewSet,
    SignUpViewSet,
    token,
    ReviewViewSet,
    CommentViewSet
)

router = DefaultRouter()
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'users', UserViewSet, basename='users')
router.register(r'auth/signup', SignUpViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

auth_urls = [
    path('signup/', SignUpViewSet, name='signup'),
    path('token/', token, name='token'),
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(auth_urls)),
    path('v1/users/me/', UserViewSet, name="get_profile")
]
