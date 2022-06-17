from django.contrib import admin
from community.models import Post, Category, Comment

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)