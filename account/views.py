from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
import json

from .forms import LoginForm, UserRegistrationForm, UserEditionForm, ProfileEditionForm
from common.decorators import ajax_required
from .models import Profile, Contact
from post.models import Post


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})


@login_required
def homepage(request):
    users = User.objects.all()
    follows = request.user.profile.follows.all()
    for follow in follows:
        users = users.exclude(username=follow.username)
    users = users.exclude(username=request.user.username)
    suggestions = users.annotate(popularity=Count('followers')).order_by('-popularity')[:5]
    posts = Post.objects.filter(user__in=request.user.profile.follows.all()).order_by('-created')
    print(posts)
    paginator = Paginator(posts, 8)
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
        return render(request, 'account/list-ajax-home.html', {'posts': posts})
    return render(request, 'account/home.html', {'suggestions': suggestions, 'posts': posts})


def search_users(request):
    if request.method == 'POST':
        search_val = json.loads(request.body).get('searchText')
        users = User.objects.filter(
            username__istartswith=search_val, is_active=True) | User.objects.filter(
            first_name__istartswith=search_val, is_active=True) | User.objects.filter(
            last_name__istartswith=search_val, is_active=True)
        users = users
        data = users.values()
        for i in data:
            username = i.get('username')
            photo = User.objects.get(username=username).profile.photo
            if photo:
                i['photo'] = photo.url
                print(photo.url)

            else:
                i['photo'] = '/static/src/img/default_profile.png'
        return JsonResponse(list(data), safe=False)


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        print(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.email = user_form.cleaned_data['email']
            new_user.first_name = user_form.cleaned_data['first_name']
            new_user.last_name = user_form.cleaned_data['last_name']
            new_user.save()
            Profile.objects.create(user=new_user)
            return redirect('login')

    else:
        user_form = UserRegistrationForm()

    return render(request, 'account/register.html', {'form': user_form})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    mutual = []
    for obj in request.user.profile.follows.all():
        if obj in user.followers.all():
            mutual.append(obj)

    posts = user.posts.all().order_by('-created')

    return render(request, 'account/profile.html', {'user': user, 'mutual': mutual, 'posts': posts})


@login_required
@require_POST
@ajax_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    req_user = request.user.profile
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                req_user.follows.add(user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
                req_user.follows.remove(user)
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})

    return JsonResponse({'status': 'error'})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditionForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditionForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            updated_profile = profile_form.save(commit=False)
            link = str(request.POST.get('website')).split('://')[-1]
            updated_profile.website_name = link
            updated_profile.save()
            messages.success(request, 'Profile saved.')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditionForm(instance=request.user)
        profile_form = ProfileEditionForm(instance=request.user.profile)

    return render(request, 'account/edit-profile.html', {'user_form': user_form, 'profile_form': profile_form})


def suggested(request):
    users = User.objects.all()
    follows = request.user.profile.follows.all()
    for follow in follows:
        users = users.exclude(username=follow.username)
    users = users.exclude(username=request.user.username)
    suggestions = users.annotate(popularity=Count('followers')).order_by('-popularity')

    return render(request, 'account/suggested.html', {'suggestions': suggestions})


@login_required
@ajax_required
@require_POST
def post_save(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    print('post save', request.POST)
    if post_id and action:
        try:
            post = get_object_or_404(Post, id=post_id)
            if action == 'save':
                request.user.profile.saved.add(post)
                print('add')
            else:
                request.user.profile.saved.remove(post)
                print('remove')
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def profile_saved(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    if request.user != user:
        return redirect('homepage')
    saved = user.profile.saved.all()

    return render(request, 'account/saved.html', {'saved': saved, 'user': user})
