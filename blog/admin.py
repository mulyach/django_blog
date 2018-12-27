from django.contrib import admin

from .models import Category,Article,Image,ItemCounter,WebCounter,Comment,Signature

admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Image)
admin.site.register(ItemCounter)
admin.site.register(WebCounter)
admin.site.register(Comment)
admin.site.register(Signature)
