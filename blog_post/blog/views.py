from django.shortcuts import render, redirect
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
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
        context['comment_form'] = CommentForm()

        return context

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    #fields = '__all__' 포스트에 있는거 다 수정하고 싶으면 이거 쓰면 됨. 하지만 우리는 날짜와 작성자를 바꾸면 안되기에 all을 쓰면 안됨
    fields = [
        'title', 'content', 'head_image', 'category', 'tags'
    ]

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


def new_comment(request, pk):
    post = Post.objects.get(pk=pk)
    
    if request.method == 'POST':
        commnet_form = CommentForm(request.POST)
        if commnet_form.is_valid():
            comment = commnet_form.save(commit = False) # post와 user을 채워야하므로 일단은 false
            comment.post = post
            comment.author = request.user
            comment.save()

            return redirect(comment.get_absolute_url())

    else:
        return redirect('/blog/')

class CommentUpdate(UpdateView):
    model = Comment
    form_class = CommentForm

    def get_object(self, queryset=None):
        comment = super(CommentUpdate, self).get_object()
        if comment.author != self.request.user:
            raise PermissionError("You don't have permission to edit comment.")
        return comment

def delete_comment(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.user == comment.author:
        post = comment.post
        comment.delete()

        return redirect(post.get_absolute_url() + '#comment-list')
    
    else:
        return redirect('/blog/')