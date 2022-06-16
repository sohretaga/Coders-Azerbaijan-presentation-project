from django.contrib import admin
from . import models

# Register your models here.

class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'sent_date')


admin.site.register(models.Contact, ContactAdmin)
