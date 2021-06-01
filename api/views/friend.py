from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Friend, Account, Relation,  FriendList,GetFriend, PersonalTimetable
from api.serializers import FriendSerializer
from datetime import datetime
import base64


# Create your views here.

class FriendViewSet(ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer

    @action(detail=False, methods=['POST'])
    def add(self, request):
        uid = request.query_params.get('uid')
        friendId = request.query_params.get('friendId')

        user = Account.objects.get(pk=uid)
        friend = Account.objects.get(pk=friendId)
        invite = Relation.objects.get(pk=3)
        be_invited = Relation.objects.get(pk=4)

        try:
            Friend.objects.create(user=user, related_person=friend, relation=invite)
            Friend.objects.create(user=friend, related_person=user, relation=be_invited)

            return Response({
                '加好友結果': '成功'
            })
        except IntegrityError:
            return Response({
                '加好友結果': '已邀請過'
            })

    @action(detail=False, methods=['PATCH'])
    def add_best(self, request):
        uid = request.query_params.get('uid')
        friendId = request.query_params.get('friendId')

        fr = Friend.objects.filter(
            user__user_id=uid,
            related_person__user_id=friendId,
        )
        best_friend = Relation.objects.get(pk=2)
        fr.update(relation=best_friend)

        return Response({
            '新增摯友結果': '成功'
        })

    @action(detail=False)
    def get(self, request):
        uid = request.query_params.get('uid')
        friendId = request.query_params.get('friendId')

        fr = GetFriend.objects.filter(user_id=uid, related_person=friendId)
        pt = PersonalTimetable.objects.filter(user_id=friendId,
                                              semester_start__lte=datetime.now(),
                                              semester_end__gte=datetime.now())

        pl = Account.objects.get(user_id=friendId).is_public
        plt = Friend.objects.filter(user_id=friendId,related_person=uid).first().is_public_timetable

        ptn = fr.first().is_public_timetable
        if pl == 1:
            ptn = 0
        if pl == 0 and plt == 1:
            ptn = 0
        if pt.count() == 0:
            ptn = None

        return Response({
            'photo': base64.b64encode(fr.first().photo).decode(),
            'friendName': fr.first().name,
            'timetableId': ptn,
        })

    @action(detail=False)
    def _list(self, request):
        uid = request.query_params.get('uid')
        fr = FriendList.objects.filter(user_id=uid, relation_id=1)

        if fr.count() > 0:
            return Response({
                'friend': [
                    {
                        'photo': base64.b64encode(f.photo).decode(),
                        'friendId': f.related_person,
                        'friendName': f.name,
                        'relationId': f.relation_id,
                    }
                    for f in fr
                ]
            })
        else:
            return Response({
                '尚未有朋友'
            })

    @action(detail=False)
    def best_list(self, request):
        uid = request.query_params.get('uid')
        fr = FriendList.objects.filter(user_id=uid, relation_id=2)

        if fr.count() > 0:
            return Response({
                'friend': [
                    {
                        'photo': base64.b64encode(f.photo).decode(),
                        'friendId': f.related_person,
                        'friendName': f.name,
                    }
                    for f in fr
                ]
            })
        else:
            return Response({
                '沒有摯友'
            })

    @action(detail=False)
    def make_invite_list(self, request):
        uid = request.query_params.get('uid')
        fr = FriendList.objects.filter(user_id=uid, relation_id=4)

        if fr.count() > 0:
            return Response({
                'friend': [
                    {
                        'photo': base64.b64encode(f.photo).decode(),
                        'friendId': f.related_person,
                        'friendName': f.name,
                    }
                    for f in fr
                ]
            })
        else:
            return Response({
                '沒有好友邀請'
            })




    @action(detail=False, methods=['PATCH'])
    def add_reply(self, request):
        uid = request.query_params.get('uid')
        friendId = request.query_params.get('friendId')
        relationId = int(request.query_params.get('relationId'))

        if relationId == 1:
            fr = Friend.objects.filter(user=uid, related_person=friendId)
            fr.update(relation=1)

            fr = Friend.objects.filter(related_person=uid, user=friendId)
            fr.update(relation=1)
            return Response({
                '加好友回覆結果': '已接受邀請'
            })
        elif relationId == 5:
            fr = Friend.objects.filter(user=uid, related_person=friendId)
            fr.delete()
            fr = Friend.objects.filter(related_person=uid, user=friendId)
            fr.delete()
            return Response({
                '加好友回覆結果': '拒絕成功'
            })


    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        uid = request.query_params.get('uid')
        friendId = request.query_params.get('friendId')

        fr = Friend.objects.filter(user=uid, related_person=friendId)
        fr.delete()
        fr = Friend.objects.filter(related_person=uid, user=friendId)
        fr.delete()

        return Response({
            '刪除好友結果': '刪除成功'
        })

    @action(detail=False, methods=['PATCH'])
    def delete_best(self, request):
        uid = request.query_params.get('uid')
        friendId = request.query_params.get('friendId')

        fr = Friend.objects.filter(user_id=uid, related_person=friendId)
        fr.update(relation=1)

        return Response({
            '刪除摯友結果': '成功'
        })