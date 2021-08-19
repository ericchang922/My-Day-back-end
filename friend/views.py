from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from api.response import *
from api.models import Friend, Account, Relation, PersonalTimetable
from friend.serializers import FriendSerializer

from datetime import datetime


# Create your views here.
class FriendViewSet(ModelViewSet):
    queryset = Friend.objects.filter(relation_id=0)
    serializer_class = FriendSerializer

    @action(detail=False, methods=['POST'])
    def add(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')
        try:
            user = Account.objects.get(pk=uid)
            friend = Account.objects.get(pk=friend_id)
            invite = Relation.objects.get(pk=3)
            be_invited = Relation.objects.get(pk=4)

            Friend.objects.create(user=user, related_person=friend, relation=invite)
            Friend.objects.create(user=friend, related_person=user, relation=be_invited)

            return success(request=request)
        except IntegrityError:
            return err(Msg.Err.Friend.already_sent_request, 'FR-A-001', request)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)

    @action(detail=False, methods=['PATCH'])
    def add_reply(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')
        relation_id = data.get('relationId')

        if relation_id not in [1, 5]:
            return not_found(Msg.NotFound.relation, request)

        be_invited = Friend.objects.filter(user=uid, related_person=friend_id, relation_id=4)
        invite = Friend.objects.filter(related_person=uid, user=friend_id, relation_id=3)

        if be_invited.exists() and invite.exists():
            if relation_id == 1:
                be_invited.update(relation_id=relation_id)
                invite.update(relation_id=relation_id)
                return success(request=request)
            else:
                be_invited.delete()
                invite.delete()
                return success(request=request)
        else:
            return not_found(Msg.NotFound.friend_request, request)

    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')

        user_friendship = Friend.objects.filter(user=uid, related_person=friend_id, relation_id__in=[1, 2])
        friend_friendship = Friend.objects.filter(related_person=uid, user=friend_id, relation_id__in=[1, 2])

        if user_friendship.exists() and friend_friendship.exists():
            user_friendship.delete()
            friend_friendship.delete()
            return success(request=request)
        else:
            return not_found(Msg.NotFound.friend, request)

    @action(detail=False, methods=['PATCH'])
    def add_best(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')

        friendship = Friend.objects.filter(user_id=uid, related_person=friend_id, relation_id__in=[1, 2])
        just_friend = friendship.filter(relation_id=1)

        if friendship.exists() and just_friend.exists():
            just_friend.update(relation_id=2)
            return success(request=request)
        elif not friendship.exists():
            return not_found(Msg.NotFound.friend, request)
        else:
            return err(Msg.Err.Friend.already_best_friend, 'FR-D-001', request)

    @action(detail=False, methods=['PATCH'])
    def delete_best(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')

        friend = Friend.objects.filter(user_id=uid, related_person=friend_id, relation_id=2)
        if friend.exists():
            friend.update(relation_id=1)
            return success(request=request)
        else:
            return not_found(Msg.NotFound.best_friend, request)

    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        friend_id = data.get('friendId')

        friend = Friend.objects.filter(user_id=uid, related_person=friend_id, relation_id__in=[1, 2])
        if friend.exists():
            personal_timetable = PersonalTimetable.objects.filter(user_id=friend_id,
                                                                  semester_start__lte=datetime.now(),
                                                                  semester_end__gte=datetime.now())

            public = Account.objects.get(user_id=friend_id).is_public
            public_to_friend = Friend.objects.filter(user_id=friend_id, related_person=uid).first().is_public_timetable

            not_public_schedule = (public == 0 or (public == 1 and public_to_friend == 0))
            timetable_no = 0 if not personal_timetable.exists() or not_public_schedule \
                else personal_timetable.first().timetable_no.serial_no

            return success({
                'photo': friend.first().related_person.photo,
                'friendName': friend.first().related_person.name,
                'timetableId': timetable_no,
            }, request)
        else:
            return not_found(Msg.NotFound.friend, request)

    @action(detail=False)
    def friend_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        friend = Friend.objects.filter(user_id=uid, relation_id=1)
        return success({
            'friend': [
                {
                    'photo': f.related_person.photo,
                    'friendId': f.related_person.pk,
                    'friendName': f.related_person.name,
                    'relationId': f.relation_id,
                }
                for f in friend
            ]
        }, request)

    @action(detail=False)
    def best_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        friend = Friend.objects.filter(user_id=uid, relation_id=2)
        return success({
            'friend': [
                {
                    'photo': f.related_person.photo,
                    'friendId': f.related_person.pk,
                    'friendName': f.related_person.name,
                }
                for f in friend
            ]
        }, request)

    @action(detail=False)
    def make_invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        friend = Friend.objects.filter(user_id=uid, relation_id=4)
        return success({
            'friend': [
                {
                    'photo': f.related_person.photo,
                    'friendId': f.related_person.pk,
                    'friendName': f.related_person.name,
                }
                for f in friend
            ]
        }, request)
