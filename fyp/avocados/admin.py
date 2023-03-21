from django.contrib import admin
from .image import Images
from .contract import Contract

# Register your models here.
admin.site.register(Images)
admin.site.register(Contract)