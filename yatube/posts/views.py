from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from yatube.settings import AMOUNT_POSTS_ON_PAGE

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import easy_paginator


@cache_page(60 * 20)
def index(request):
    post_list = Post.objects.all()
    page_obj = easy_paginator(post_list, request, AMOUNT_POSTS_ON_PAGE)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_post_list = Post.objects.filter(group=group)
    page_obj = easy_paginator(group_post_list, request, AMOUNT_POSTS_ON_PAGE)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    profile_post_list = author.posts.all()
    page_obj = easy_paginator(profile_post_list, request, AMOUNT_POSTS_ON_PAGE)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not post_id and post.author != request.user:
        return redirect('posts:post_detail', post_id)
    else:
        if post.author == request.user:
            form = PostForm(request.POST or None,
                            files=request.FILES or None,
                            instance=post)
            if form.is_valid():
                form.save()
                return redirect('posts:post_detail', post_id)
            context = {'form': form, 'post': post}
            return render(request, 'posts/post_create.html', context)
        else:
            return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_foll_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': easy_paginator(post_foll_list, request,),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(
        user=request.user,
        author=author,
    )
    if not follower.exists() and request.user != author:
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=author)
