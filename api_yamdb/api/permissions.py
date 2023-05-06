from rest_framework import permissions


class IsAdminOrSuperuserPermission(permissions.BasePermission):
    """Доступ разрешен только для администратора и Суперпользователя."""
    message = 'Ваши полномочия здесь все...'

    def has_permission(self, request, view):
        if request.user.is_admin or request.user.is_superuser:
            return True
        return False


class IsModeratorPermission(permissions.BasePermission):
    """Доступ разрешен только для Модератора."""
    message = 'Ваши полномочия здесь все...'

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_moderator:
            return True
        return False


class TitlePermission(permissions.BasePermission):
    """
    Права доступа для администратора и супер юзера
    на добавление и удаление категорий, жанров и произведений.
    """
    message = 'Ваши полномочия здесь все...'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_admin or request.user.is_superuser:
            return True
        return False


class ReviewPermission(permissions.BasePermission):
    """
    Права доступа для авторов, администратора и модератора
    на изменение отзывов и комментариев.
    """
    message = 'Изменение чужого контента запрещено!'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)
