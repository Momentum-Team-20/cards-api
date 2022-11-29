from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Card, Follow

admin.site.register(User, UserAdmin)
admin.site.register(Card)
admin.site.register(Follow)
