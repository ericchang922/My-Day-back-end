from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import  Account, Group, GroupMember, GroupList,GroupInviteList,GetGroup,GetGroupNoVote,GroupLog
from api.serializers import GroupSerializer, CreateGroupRequestSerializer

# Create your views here.
class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=False, methods=['POST'])
    def create_group(self, request):
        data = request.data
        serializer = CreateGroupRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        friends = serializer.validated_data.pop('friend')
        founder = serializer.validated_data['founder']
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
            '建立群組結果': '成功'
        })

    @action(detail=False, methods=['PATCH'])
    def edit_group(self, request):
        uid = request.query_params.get('uid')
        groupNum = request.query_params.get('groupNum')
        title = request.query_params.get('title')
        typeId = request.query_params.get('typeId')

        grm = GroupMember.objects.filter(group_no=groupNum, user_id=uid, status_id__in=[1,4])

        if grm.count() > 0:
            gr = Group.objects.get(serial_no=groupNum)

            if typeId == None:
                typeId = gr.type_id
            if title == None:
                title = gr.group_name

            gr.group_name = title
            gr.type_id = typeId
            gr.save()

            GroupLog.objects.create(do_time=datetime.now(), group_no=gr, user_id=uid,
                                    trigger_type='U', do_type_id=1)

            return Response({
                '編輯群組結果': '成功'
            })
        else:
            return Response({
                '編輯群組結果': '失敗，您不屬於此群組'
            })

    @action(detail=False, methods=['POST'])
    def invite_friend(self, request):
        uid = request.query_params.get('uid')
        friendId = request.query_params.get('friendId')
        groupNum = request.query_params.get('groupNum')
        groupNum = Group.objects.get(pk=groupNum)

        inviter_status = GroupMember.objects.filter(group_no=groupNum, user_id=uid).first().status_id
        if inviter_status == 4:
            GroupMember.objects.create(group_no=groupNum, user_id=friendId, status_id=2, inviter_id=uid)
            return Response({
                '群組邀請結果': '成功'
            })
        else:
            return Response({
                '群組邀請結果': '您非管理者，無法邀請他人'
            })

    @action(detail=False, methods=['PATCH'])
    def member_status(self, request):
        uid = request.query_params.get('uid')
        groupNum = request.query_params.get('groupNum')
        statusId = int(request.query_params.get('statusId'))
        gr = GroupMember.objects.filter(group_no=groupNum, user_id=uid)

        if gr.count() > 0:
            if statusId == 1:
                gr.update(status_id=statusId, join_time=datetime.now())
                return Response({
                    '加入群組結果': '加入成功'
                })
            elif statusId == 3:
                gr.delete()
                return Response({
                    '加入群組結果': '拒絕成功'
                })
        else:
            groupNum = Group.objects.get(serial_no=groupNum)
            GroupMember.objects.create(group_no=groupNum, user_id=uid,
                                       status_id=1, join_time=datetime.now(), inviter_id=uid)
            return Response({
                '加入群組結果': '自行加入成功'
            })

    @action(detail=False)
    def _list(self, request):
        uid = request.query_params.get('uid')
        gr = GroupList.objects.filter(user_id=uid, status_id__in=[1,4])

        if gr.count() > 0:
            return Response({
                'list': [
                    {
                        'groupID': g.group_no,
                        'title': g.group_name,
                        'typeId': g.type_id,
                        'peopleCount': g.cnt,
                    }
                    for g in gr
                ]
            })
        else:
            return Response({
                '沒有群組'
            })


    @action(detail=False)
    def get(self, request):
        uid = request.query_params.get('uid')
        groupNum = request.query_params.get('groupNum')
        gr = GroupMember.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1,4])

        if gr.count() > 0:
            getgr = GetGroup.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])
            if getgr.count() > 0:
                return Response({
                    'title': getgr.first().group_name,
                    'typeId': getgr.first().type_id,
                    'vote': [
                        {
                            'title': g.title,
                            'voteNum': g.votenum,
                            'isVoteType': g.votetype,
                        }
                        for g in getgr
                    ]
                })
            else:
                getgr = GetGroupNoVote.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])
                return Response({
                    'title': getgr.first().group_name,
                    'typeId': getgr.first().type_id,
                })
        else:
            return Response({
                '您不屬於此群組'
            })


    @action(detail=False)
    def member_list(self, request):
        uid = request.query_params.get('uid')
        groupNum = request.query_params.get('groupNum')
        gr = GroupMember.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])

        if gr.count() > 0:
            gr = GroupList.objects.filter(group_no=groupNum)
            return Response({
                'founderName': gr.first().foundername,
                'member': [
                    {
                        'memberName': g.name,
                        'statusId': g.status_id,
                    }
                    for g in gr
                ]
            })
        else:
            return Response({
                '您不屬於此群組'
            })


    @action(detail=False)
    def invite_list(self, request):
        uid = request.query_params.get('uid')
        gr = GroupInviteList.objects.filter(user_id=uid,status_id=2)

        if gr.count() > 0:
            return Response({
                'groupContent': [
                    {
                        'groupId': g.group_no,
                        'title': g.group_name,
                        'typeId': g.type_id,
                        'inviteName': g.inviter_name,
                    }
                    for g in gr
                ]
            })
        else:
            return Response({
                '沒有群組邀請'
            })


    @action(detail=False, methods=['Delete'])
    def quit_group(self, request):
        uid = request.query_params.get('uid')
        groupNum = request.query_params.get('groupNum')

        ugr = GroupMember.objects.filter(user_id=uid, group_no=groupNum)
        gr = GroupMember.objects.filter(group_no=groupNum, status_id=4)

        if ugr.first().status_id == 4 and gr.count() == 1:
            return Response({
                '退出群組結果': '您是唯一管理者，需先指定另一位管理者才能退出'
            })
        else:
            ugr.delete()
            return Response({
                '退出群組結果': '退出成功'
            })


    @action(detail=False, methods=['PATCH'])
    def setting_manager(self, request):
        uid = request.query_params.get('uid')
        friendId = request.query_params.get('friendId')
        groupNum = request.query_params.get('groupNum')
        statusId = request.query_params.get('statusId')
        ugr = GroupMember.objects.filter(user_id=uid, group_no=groupNum)

        if ugr.first().status_id != 4:
            return Response({
                '設定群組管理者結果':'您非管理者無法指定他人為管理者'
            })
        else:
            gr = GroupMember.objects.filter(user_id=friendId, group_no=groupNum)
            gr.update(status_id=4)

            return Response({
                '設定群組管理者結果':'成功'
            })

