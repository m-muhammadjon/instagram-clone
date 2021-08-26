from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from taggit.models import Tag

from .forms import PostCreationForm, CommentForm, PostEditionForm
from common.decorators import ajax_required
from actions.utils import create_action
from .models import Post, Comment


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostCreationForm(data=request.POST, files=request.FILES)
        # print('req')
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            ext = str(request.FILES.get('post')).split('.')[-1]
            # check the file extension is video extension
            if ext.lower() == 'mp4':
                new_post.type = 'video'
            new_post.save()
            form._save_m2m()
            type_msg = 'photo' if new_post.type == 'image' else 'video'
            create_action(request.user, f'posted {type_msg}', new_post)
            messages.success(request, 'Post created')
            return redirect('homepage')
    else:
        form = PostCreationForm()

    return render(request, 'post_create.html', {'form': form})


def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    comments = post.comments.filter(active=True).order_by('-created')
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.user = request.user
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, 'post_detail.html', {'post': post,
                                                'comments': comments,
                                                'form': comment_form})


def edit(request, id):
    post = get_object_or_404(Post, id=id)
    if post.user != request.user:
        return redirect('homepage')
    else:
        print('iya')
        form = PostEditionForm(instance=post)
        if request.method == 'POST':
            print('post')
            form = PostEditionForm(data=request.POST, files=request.FILES, instance=post)
            if form.is_valid():
                print('valid')
                form.save()
                return redirect(post.get_absolute_url())

    return render(request, 'post_edit.html', {'form': form, 'post': post})


@login_required
def delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    messages.success(request, 'Post deleted successfully')
    return redirect('homepage')


@login_required
@ajax_required
@require_POST
def create_comment(request):
    # print(request.POST)
    post_id = request.POST.get('id')
    body = request.POST.get('body')
    comment = Comment.objects.create(body=body, post_id=post_id, user=request.user)
    create_action(request.user, 'commented', Post.objects.get(id=post_id))
    return JsonResponse({'status': 'ok', 'date': comment.created})


@login_required
@ajax_required
@require_POST
def post_like(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    # print(request.POST)
    if post_id and action:
        try:
            post = get_object_or_404(Post, id=post_id)
            if action == 'like':
                post.likes.add(request.user)
                create_action(request.user,  'liked', post)
            else:
                post.likes.remove(request.user)
            print('req keldi')
            return JsonResponse({'status': 'ok'})
        except:
            pass

    return JsonResponse({'status': 'error'})


@login_required
def explore(request, tag_slug=None):
    posts = Post.objects.all().order_by('-created')
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])

    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range
            # return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    if request.is_ajax():
        print('ajax request')
        return render(request, 'list-ajax.html', {'posts': posts})

    return render(request, 'explore.html', {'posts': posts, 'tag': tag})
