from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

# Create your models here.
    
class Post(models.Model):
    title = models.CharField(max_length=30)
    content = MarkdownxField()
    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True) #many to many 에서는 null=true 쓰면 안됨

    def get_markdown_content(self):
        return markdown(self.content)

    class Meta:
        ordering = ['-created',]

class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(blank=True)
    
    class Meta: #admin 페이지에서 Categorys 로 문법이 잘못 출력되는걸 고침
        verbose_name_plural = 'categories'


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = MarkdownxField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_markdown_content(self):
        return markdown(self.text)
        