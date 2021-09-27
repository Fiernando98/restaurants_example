from rest_framework import routers

from apps.users.views import UsersViewSet, PasswordResetViewSet

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, 'users')
router.register(r'password_reset', PasswordResetViewSet, 'password-reset')

urlpatterns = router.urls
