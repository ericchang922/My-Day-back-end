from django.core.exceptions import ObjectDoesNotExist

from api.message import Msg
from api.models import Account, Friend, GroupMember
from group.serializers import CreateGroupRequestSerializer


def new_group_request(data):
    try:
        Account.objects.get(user_id=data['founder'])
    except ObjectDoesNotExist:
        return Msg.NotFound.account

    serializer = CreateGroupRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    friends = serializer.validated_data.pop('friend')
    founder = serializer.validated_data['founder']

    for friend in friends:
        if not Friend.objects.filter(user_id=founder, related_person=friend['friendId'],
                                     relation_id__in=[1, 2]).exists():
            return Msg.NotFound.friend

    group = serializer.save()
    group_members = [
        GroupMember(user=founder, group_no=group, status_id=4, inviter=founder)
    ]

    for friend in friends:
        user = Account.objects.get(pk=friend['friendId'])
        group_member = GroupMember(user=user, group_no=group, status_id=2, inviter=founder)
        group_members.append(group_member)
    GroupMember.objects.bulk_create(group_members)
    return group
