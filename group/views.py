import base64

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Account, Group, GroupMember, GroupList, GroupInviteList, GetGroup, GetGroupNoVote, GroupLog, \
    Friend
from group.serializers import GroupSerializer, CreateGroupRequestSerializer

# Create your views here.
class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=False, methods=['POST'])
    def create_group(self, request):
        data = request.data

        if not Account.objects.filter(user_id=data['founder']).exists():
            return Response({'response': False, 'message': '帳號不存在'})

        serializer = CreateGroupRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        friends = serializer.validated_data.pop('friend')
        founder = serializer.validated_data['founder']

        for friend in friends:
            if not Friend.objects.filter(user_id=founder, related_person=friend['friendId'],
                                         relation_id__in=[1, 2]).exists():
                return Response({'response': False, 'message': '僅能邀請好友'})

        group = serializer.save()
        group_members = [
            GroupMember(user=founder, group_no=group, status_id=4, inviter_id=founder.user_id)
        ]

        for friend in friends:
            user = Account.objects.get(pk=friend['friendId'])
            group_member = GroupMember(user=user, group_no=group, status_id=2, inviter_id=founder.user_id)
            group_members.append(group_member)
        GroupMember.objects.bulk_create(group_members)

        return Response({
            'response': True,
            'message': '成功'
        })

    @action(detail=False, methods=['PATCH'])
    def edit_group(self, request):
        data = request.data

        uid = data.get('uid')
        groupNum = data.get('groupNum')
        title = data.get('title')
        typeId = data.get('typeId')

        group_member = GroupMember.objects.filter(group_no=groupNum, user_id=uid, status_id__in=[1, 4])

        if group_member.exists():
            group = Group.objects.get(serial_no=groupNum)

            if not typeId:
                typeId = group.type_id
            if not title:
                title = group.group_name

            group.group_name = title
            group.type_id = typeId
            group.save()

            GroupLog.objects.create(do_time=datetime.now(), group_no=group, user_id=uid,
                                    trigger_type='U', do_type_id=1)

            return Response({
                'response': True,
                'message': '成功'
            })
        else:
            return Response({
                'response': False,
                'message': '失敗，您不屬於此群組'
            })

    @action(detail=False, methods=['POST'])
    def invite_friend(self, request):
        data = request.data

        uid = data.get('uid')
        friendId = data.get('friendId')
        groupNum = data.get('groupNum')
        try:
            user_in_account = Account.objects.get(user_id=uid)
            friend_in_account = Account.objects.get(user_id=friendId)
            groupNum = Group.objects.get(pk=groupNum)

            friendship = Friend.objects.filter(user_id=uid, related_person=friendId, relation_id__in=[1, 2])
            group_manager = GroupMember.objects.filter(group_no=groupNum, user_id=uid, status_id=4)
            if friendship.exists() and group_manager.exists():
                GroupMember.objects.create(group_no=groupNum, user_id=friendId, status_id=2, inviter_id=uid)
                return Response({
                    'response': True,
                    'message': '成功'
                })
            elif group_manager.exists():
                return Response({
                    'response': False,
                    'message': '僅能邀請好友'
                })
            return Response({
                'response': False,
                'message': '您非此群組管理者，無法邀請朋友'
            })
        except IntegrityError:
            return Response({
                'response': False,
                'message': '已邀請過'
            })
        except ObjectDoesNotExist:
            return Response({
                'response': False,
                'message': '資料不存在'
            })

    @action(detail=False, methods=['PATCH'])
    def member_status(self, request):
        data = request.data

        uid = data.get('uid')
        groupNum = data.get('groupNum')
        statusId = int(data.get('statusId'))

        group_member = GroupMember.objects.filter(group_no=groupNum, user_id=uid)
        if group_member.exists() and statusId in [1, 3]:
            if statusId == 1:
                group_member.update(status_id=1, join_time=datetime.now())
                return Response({
                    'response': True,
                    'message': '加入成功'
                })
            elif statusId == 3:
                group_member.delete()
                return Response({
                    'response': True,
                    'message': '拒絕成功'
                })
        try:
            user = Account.objects.get(user_id=uid)
            group = Group.objects.get(serial_no=groupNum)
            if statusId != 1:
                return Response({
                    'response': False,
                    'message': '狀態編號錯誤'
                })
            GroupMember.objects.create(group_no=group, user_id=uid,
                                       status_id=1, join_time=datetime.now(), inviter_id=uid)
            return Response({
                'response': True,
                'message': '自行加入成功'
            })
        except ObjectDoesNotExist:
            return Response({
                'response': False,
                'message': '資料不存在'
            })

    @action(detail=False)
    def group_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group = GroupList.objects.filter(user_id=uid, status_id__in=[1,4], is_temporary_group=0)

        return Response({
            'groupContent': [
                {
                    'groupID': g.group_no,
                    'title': g.group_name,
                    'typeId': g.type_id,
                    'peopleCount': g.cnt,
                }
                for g in group
            ]
        })

    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        groupNum = data.get('groupNum')
        group = GroupMember.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])
        get_group = GetGroup.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])
        group_has_vote = 1 if get_group.count() > 0 else 0

        if group.count() == 0:
            return Response({
                'response': False,
                'message': '您不屬於此群組'
            })
        elif get_group.count() == 0:
            get_group = GetGroupNoVote.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])

        return Response({
            'title': get_group.first().group_name,
            'typeId': get_group.first().type_id,
            'vote': [
                {
                    'title': g.title,
                    'voteNum': g.votenum,
                    'isVoteType': g.votetype,
                }
                for g in get_group if group_has_vote
            ]
        })

    @action(detail=False)
    def member_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        groupNum = data.get('groupNum')
        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])
        if user_in_group.count() > 0:
            group = GroupList.objects.filter(group_no=groupNum)
            return Response({
                'founderPhoto': base64.b64encode(group.first().founder_photo),
                'founderName': group.first().founder_name,
                'member': [
                    {
                        'memberPhoto': base64.b64encode(g.member_photo),
                        'memberName': g.name,
                        'statusId': g.status_id,
                    }
                    for g in group
                ]
            })
        else:
            return Response({
                'response': False,
                'message': '您不屬於此群組'
            })

    @action(detail=False)
    def invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        gr = GroupInviteList.objects.filter(user_id=uid,status_id=2, is_temporary_group=0)

        return Response({
            'groupContent': [
                {
                    'groupId': g.group_no,
                    'title': g.group_name,
                    'typeId': g.type_id,
                    'inviterPhoto': base64.b64encode(g.inviter_photo),
                    'inviterName': g.inviter_name,
                }
                for g in gr
            ]
        })

    @action(detail=False, methods=['Delete'])
    def quit_group(self, request):
        data = request.data

        uid = data.get('uid')
        groupNum = data.get('groupNum')

        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=groupNum)
        group_manager = GroupMember.objects.filter(group_no=groupNum, status_id=4)
        group_member = GroupMember.objects.filter(group_no=groupNum, status_id__in=[1, 2])

        if user_in_group.exists():
            if user_in_group.first().status_id == 4 and group_manager.count() == 1 and group_member.count() > 0:
                return Response({
                    'response': False,
                    'message': '您是唯一管理者，需先指定另一位管理者才能退出'
                })
            else:
                user_in_group.delete()
                return Response({
                    'response': True,
                    'message': '退出成功'
                })
        return Response({
            'response': False,
            'message': '您已不是此群組的成員'
        })

    @action(detail=False, methods=['PATCH'])
    def setting_manager(self, request):
        data = request.data

        uid = data.get('uid')
        friendId = data.get('friendId')
        groupNum = data.get('groupNum')
        statusId = data.get('statusId')

        try:
            user_in_account = Account.objects.get(user_id=uid)
            friend_in_account = Account.objects.get(user_id=friendId)
        except ObjectDoesNotExist:
            return Response({
                'response': False,
                'message': '資料不存在'
            })

        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=groupNum)
        if user_in_group.exists():
            if user_in_group.first().status_id != 4:
                return Response({
                    'response': False,
                    'message': '您非管理者無法指定他人為管理者'
                })
            else:
                group_member = GroupMember.objects.filter(user_id=friendId, group_no=groupNum)
                group_member.update(status_id=4)

                return Response({
                    'response': True,
                    'message':'成功'
                })
        return Response({
            'response': False,
            'message': '此人不在群組'
        })

