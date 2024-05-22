from django.urls import path 
from . import views

urlpatterns = [
   path("signup/signup", views.AccountCreateView.as_view() , name="signup"),
]
