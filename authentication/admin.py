from django.contrib import admin
from authentication.models import User

# admin.site.register(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "created_at", "updated_at", "uuid")
