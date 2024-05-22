from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager

class CustomUser(AbstractUser):

    first_name = None
    last_name = None
    username = None
    username = models.CharField("Nome",("username"), max_length=254, unique=False)
    email = models.EmailField(("email"), max_length=254, unique=True)

    USERNAME_FIELD = "email"          #The form field will have the input id declared as "username_id", even though it is a Email field
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return self.username
    
