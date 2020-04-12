from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Post(models.Model):
    #제목, 내용
    title = models.CharField(max_length=30)
    content = models.TextField()
    #이미지
    head_image = models.ImageField(upload_to='blog/%Y/%m/%d/', blank=True)
    #작성일, 작성자
    created = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    #카테고리
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{} :: {}'.format(self.title, self.author)

    
    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)


