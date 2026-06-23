from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """읽기는 모두 허용, 수정·삭제는 작성자 본인만."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
