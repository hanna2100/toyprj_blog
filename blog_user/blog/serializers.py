from rest_framework import serializers 
from .models import Post, Category, Tag 

class PostSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Post 
        fields = ['title', 'content', 'head_image', 'created', 'author', 'category', 'tags']
