from rest_framework.routers import SimpleRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import SignUpView
from django.urls import path

urlpatterns = [
    path('login/', obtain_auth_token, name = 'login'),
    path('signup/', SignUpView.as_view(), name = "signup")
]