from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Friend, Account, Relation,  FriendList,GetFriend, PersonalTimetable
from friend.serializers import FriendSerializer
from datetime import datetime
import base64


# Create your views here.

class FriendViewSet(ModelViewSet):
    queryset = Friend.objects.all()
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

            return Response({
                'response': True,
                'message': '成功送出邀請'
            })
        except IntegrityError:
            return Response({
                'response': False,
                'message': '已邀請過'
            })
        except ObjectDoesNotExist:
            return Response({
                'response': False,
                'message': '沒有這個人'
            })

    @action(detail=False, methods=['PATCH'])
    def add_best(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')

        friend = Friend.objects.filter(user_id=uid, related_person=friend_id, relation_id=1)
        if friend.exists():
            best_friend = Relation.objects.get(pk=2)
            friend.update(relation=best_friend)
            return Response({
                'response': True,
                'message': '成功'
            })
        return Response({
            'response': False,
            'message': '對方非朋友'
        })

    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        friend_id = data.get('friendId')

        friend = GetFriend.objects.filter(user_id=uid, related_person=friend_id, relation_id__in=[1, 2])
        if friend.exists():
            personal_timetable = PersonalTimetable.objects.filter(user_id=friend_id,
                                                                  semester_start__lte=datetime.now(),
                                                                  semester_end__gte=datetime.now())

            public = Account.objects.get(user_id=friend_id).is_public
            public_to_friend = Friend.objects.filter(user_id=friend_id,related_person=uid).first().is_public_timetable

            timetable_no = 0
            if personal_timetable.exists():
                timetable_no = personal_timetable.values('timetable_no')[0]['timetable_no']
                if public == 0 or (public == 1 and public_to_friend == 0):
                    timetable_no = 0

            return Response({
                'photo': friend.first().photo,
                'friendName': friend.first().name,
                'timetableId': timetable_no,
            })
        return Response({
            'response': False,
            'message': '沒有此好友'
        })

    @action(detail=False)
    def friend_list(self, request):
        data = request.query_params

        uid = data.get('uid')

        friend = FriendList.objects.filter(user_id=uid, relation_id=1)
        return Response({
            'friend': [
                {
                    'photo': f.photo,
                    'friendId': f.related_person,
                    'friendName': f.name,
                    'relationId': f.relation_id,
                }
                for f in friend
            ]
        })

    @action(detail=False)
    def best_list(self, request):
        data = request.query_params

        uid = data.get('uid')

        friend = FriendList.objects.filter(user_id=uid, relation_id=2)
        return Response({
            'friend': [
                {
                    'photo': f.photo,
                    'friendId': f.related_person,
                    'friendName': f.name,
                }
                for f in friend
            ]
        })

    @action(detail=False)
    def make_invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')

        friend = FriendList.objects.filter(user_id=uid, relation_id=4)
        return Response({
            'friend': [
                {
                    'photo': f.photo,
                    'friendId': f.related_person,
                    'friendName': f.name,
                }
                for f in friend
            ]
        })

    @action(detail=False, methods=['PATCH'])
    def add_reply(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')
        relation_id = int(data.get('relationId'))

        user_status = Friend.objects.filter(user=uid, related_person=friend_id)
        related_person_status = Friend.objects.filter(related_person=uid, user=friend_id)

        if user_status.exists() and related_person_status.exists():
            if relation_id == 1:
                user_status.update(relation=1)
                related_person_status.update(relation=1)
                return Response({
                    'response': True,
                    'message': '已接受邀請'
                })
            elif relation_id == 5:
                user_status.delete()
                related_person_status.delete()
                return Response({
                    'response': True,
                    'message': '拒絕成功'
                })
            return Response({
                'response': False,
                'message': '關係編號錯誤'
            })
        return Response({
            'response': False,
            'message': '沒有好友邀請關係'
        })


    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')

        user_friendship = Friend.objects.filter(user=uid, related_person=friend_id)
        friend_friendship = Friend.objects.filter(related_person=uid, user=friend_id)
        if user_friendship.exists() and friend_friendship.exists():
            user_friendship.delete()
            friend_friendship.delete()
            return Response({
                'response': True,
                'message': '刪除成功'
            })
        return Response({
            'response': False,
            'message': '沒有好友關係'
        })

    @action(detail=False, methods=['PATCH'])
    def delete_best(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')

        friend = Friend.objects.filter(user_id=uid, related_person=friend_id, relation_id=2)
        if friend.exists():
            friend.update(relation=1)
            return Response({
                'response': True,
                'message': '成功'
            })
        return Response({
            'response': False,
            'message': '沒有此摯友'
        })
