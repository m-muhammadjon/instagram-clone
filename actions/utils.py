import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import Action


def create_action(user, verb, target=None):
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        ac = Action.objects.filter(user=user, verb=verb, target_ct=target_ct, target_id=target.id)
        # delete same actions
        for i in ac:
            i.delete()
    action = Action(user=user, verb=verb, target=target)
    action.save()
    return True
