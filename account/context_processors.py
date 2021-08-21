from actions.models import Action


def navbar(request):
    context = dict()

    if request.user.is_authenticated:
        following_ids = request.user.following.values_list('id', flat=True)
        follower_ids = request.user.followers.values_list('id', flat=True)
        post_ids = request.user.posts.values_list('id', flat=True)
        actions = Action.objects.filter(target_ct__app_label='post', verb='commented', target_id__in=post_ids).exclude(user=request.user) | \
                  Action.objects.filter(target_ct__app_label='post', verb='liked', target_id__in=post_ids).exclude(user=request.user)
        if following_ids or follower_ids:
            actions = Action.objects.filter(user_id__in=following_ids).exclude(user=request.user) | \
                      Action.objects.filter(target_ct__app_label='auth', target_id=request.user.id).exclude(user=request.user)| \
                      Action.objects.filter(target_ct__app_label='post', verb='commented', target_id__in=post_ids).exclude(user=request.user) | \
                      Action.objects.filter(target_ct__app_label='post', verb='liked', target_id__in=post_ids).exclude(user=request.user)
        actions = actions.select_related('user', 'user__profile').prefetch_related('target')
        context['actions'] = actions
        context['post_ids'] = post_ids
        for i in actions:
            if not i.target:
                i.delete()
    return context
