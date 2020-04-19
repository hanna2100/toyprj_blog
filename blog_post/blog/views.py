from django.shortcuts import render, redirect
from .models import Post, Category, Tag
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class PostList(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.order_by('-created')
        
    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        return context

class PostListByTag(PostList):
    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        tag = Tag.objects.get(slug=tag_slug)

        return tag.post_set.order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(PostListByTag, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        tag_slug = self.kwargs['slug']
        context['tag'] = Tag.objects.get(slug=tag_slug)
        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()
        return context

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = [
        'title', 'content', 'head_image', 'category', 'tags'
    ]

    def form_valid(self, form): #원래 있던 함수 오버라이딩
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user #폼 객체의 유저부분을 현재유저로 채우라는 뜻
            return super(type(self), self).form_valid(form)
        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    #fields = '__all__' 포스트에 있는거 다 수정하고 싶으면 이거 쓰면 됨. 하지만 우리는 날짜와 작성자를 바꾸면 안되기에 all을 쓰면 안됨
    fields = [
        'title', 'content', 'head_image', 'category', 'tags'
    ]

class PostListByCateogory(ListView):
    
    def get_queryset(self):
        slug = self.kwargs['slug'] #slug 가져오기
        if slug == '_none':
            category = None
        else :
            category = Category.objects.get(slug=slug)

        return Post.objects.filter(category=category).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        slug = self.kwargs['slug'] #slug 가져오기

        if slug == '_none':
            context['category'] = 'no category'
        else :
            category = Category.objects.get(slug=slug)
            context['category'] = category

        # context['title'] = 'Blog - {}'.format(category.name)
        return context
