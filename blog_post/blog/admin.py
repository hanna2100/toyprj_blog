from django.contrib import admin
from .models import Post, Category, Tag, Comment
# Register your models here.

#카테고리 생성시 slug를 자동으로 생성시켜 주는 class
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)