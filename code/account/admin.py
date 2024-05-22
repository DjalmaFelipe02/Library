from django.contrib import admin
from .models import CustomUser

# Register your models here.

@admin.register(CustomUser)
class AccountAdmin(admin.ModelAdmin):
    readonly_fields =('username','email','password','last_login','date_joined')

