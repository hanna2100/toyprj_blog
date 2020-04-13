from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(blank=True)

    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/blog/category/{}/'.format(self.slug)
    
    class Meta: #admin 페이지에서 Categorys 로 문법이 잘못 출력되는걸 고침
        verbose_name_plural = 'categories'


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/blog/tag/{}/'.format(self.slug)

    
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
    #tag
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return '{} :: {}'.format(self.title, self.author)

    
    def get_absolute_url(self):
        return '/blog/{}/'.format(self.pk)


