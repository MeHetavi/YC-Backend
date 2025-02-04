from django.urls import path
from .views import RegisterUser, LoginUser, UpdateUserView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register', RegisterUser.as_view(), name='register'),
    path('login', LoginUser.as_view(), name='login'),
    # path('logout', LogoutUser.as_view(), name='logout'),
    path('edit', UpdateUserView.as_view(), name='edit'),
]
