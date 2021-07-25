from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from datetime import datetime
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Account, Group, GroupMember, GroupList, GroupInviteList, GroupVote, GroupLog, \
    Friend, GroupScheduleTime, FriendList, GroupLogDetail
from group.functions import new_group_request
from group.serializers import GroupSerializer


# Create your views here.
class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=False, methods=['POST'])
    def create_group(self, request):
        data = request.data
        data['is_temporary_group'] = 0

        result = new_group_request(data)
        if result == -1:
            return Response({'response': False, 'message': '帳號不存在'})
        elif result == -2:
            return Response({'response': False, 'message': '僅能邀請好友'})
        return Response({
            'response': True,
            'message': '成功'
        })

    @action(detail=False, methods=['PATCH'])
    def edit_group(self, request):
        data = request.data

        uid = data.get('uid')
        group_num = data.get('groupNum')
        title = data.get('title')
        type_id = data.get('typeId')

        group_member = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id__in=[1, 4])

        if group_member.exists():
            group = Group.objects.get(serial_no=group_num)

            if not type_id:
                type_id = group.type_id
            if not title:
                title = group.group_name

            group.group_name = title
            group.type_id = type_id
            group.save()

            GroupLog.objects.create(do_time=datetime.now(), group_no=group, user_id=uid,
                                    trigger_type='U', do_type_id=1, new='編輯群組資訊')

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
        friend_id = data.get('friendId')
        group_num = data.get('groupNum')

        try:
            user_in_account = Account.objects.get(user_id=uid)
            friend_in_account = Account.objects.get(user_id=friend_id)
            group_num = Group.objects.get(pk=group_num)

            group_manager = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id=4)
            friendship = Friend.objects.filter(user_id=uid, related_person=friend_id, relation_id__in=[1, 2])

            if group_manager.exists() and friendship.exists():
                GroupMember.objects.create(group_no=group_num, user_id=friend_id, status_id=2, inviter_id=uid)
                return Response({
                    'response': True,
                    'message': '成功'
                })
            elif not friendship.exists():
                return Response({
                    'response': False,
                    'message': '僅能邀請好友'
                })
            else:
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
        group_num = data.get('groupNum')
        status_id = int(data.get('statusId'))

        group_member = GroupMember.objects.filter(group_no=group_num, user_id=uid)
        if group_member.exists() and status_id in [1, 3]:
            if status_id == 1:
                group_member.update(status_id=1, join_time=datetime.now())
                return Response({
                    'response': True,
                    'message': '加入成功'
                })
            elif status_id == 3:
                group_member.delete()
                return Response({
                    'response': True,
                    'message': '拒絕成功'
                })
        try:
            user = Account.objects.get(user_id=uid)
            group = Group.objects.get(serial_no=group_num)
            if status_id != 1:
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
        group = GroupList.objects.filter(user_id=uid, status_id__in=[1, 4], is_temporary_group=0)

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
        group_num = data.get('groupNum')

        group = GroupScheduleTime.objects.filter(serial_no=group_num, end_time__gte=datetime.now())
        group_member = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])

        if not group.exists():
            return Response({
                'response': False,
                'message': '群組不存在'
            })
        elif not group_member.exists():
            return Response({
                'response': False,
                'message': '您不屬於此群組'
            })

        group_vote = GroupVote.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])
        return Response({
            'title': group.first().group_name,
            'typeId': group.first().type_id,
            'vote': [
                {
                    'title': g.title,
                    'voteNum': g.vote_num,
                    'isVoteType': bool(g.vote_type),
                }
                for g in group_vote
            ]
        })

    @action(detail=False)
    def member_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')
        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])
        if user_in_group.exists():
            group = GroupList.objects.filter(group_no=group_num)
            return Response({
                'founderPhoto': group.first().founder_photo,
                'founderName': group.first().founder_name,
                'founderId': group.first().founder,
                'member': [
                    {
                        'memberPhoto': g.member_photo,
                        'memberName': g.name,
                        'memberId': g.user_id,
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
    def invite_friend_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')
        friend_status_id = int(data.get('friendStatusId'))
        if friend_status_id not in [1, 2]:
            return Response({'response':False, 'message':'狀態編號錯誤'})

        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])

        if user_in_group.exists():
            group_member = GroupMember.objects.filter(group_no=group_num)
            friend = FriendList.objects.filter(user_id=uid, relation_id=friend_status_id)\
                .exclude(related_person__in=group_member.values_list('user_id'))

            return Response({
                'friend': [
                    {
                        'photo': g.photo,
                        'friendId': g.related_person,
                        'friendName': g.name
                    }
                    for g in friend
                ]
            })
        else:
            return Response({'response':False, 'message':'你不是群組成員'})

    @action(detail=False)
    def invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group = GroupInviteList.objects.filter(user_id=uid, status_id=2, is_temporary_group=0)

        return Response({
            'groupContent': [
                {
                    'groupId': g.group_no,
                    'title': g.group_name,
                    'typeId': g.type_id,
                    'inviterPhoto': g.inviter_photo,
                    'inviterName': g.inviter_name,
                }
                for g in group
            ]
        })

    @action(detail=False, methods=['DELETE'])
    def quit_group(self, request):
        data = request.data

        uid = data.get('uid')
        group_num = data.get('groupNum')

        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])
        group_manager = GroupMember.objects.filter(group_no=group_num, status_id=4)
        group_member = GroupMember.objects.filter(group_no=group_num, status_id__in=[1, 2])

        if not user_in_group.exists():
            return Response({
                'response': False,
                'message': '已不是此群組的成員'
            })
        elif user_in_group.first().status_id == 4 and group_manager.count() == 1 and group_member.count() > 0:
            return Response({
                'response': False,
                'message': '您是唯一管理者，需先指定另一位管理者才能退出'
            })

        user_in_group.delete()
        return Response({
            'response': True,
            'message': '退出成功'
        })

    @action(detail=False, methods=['PATCH'])
    def setting_manager(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')
        group_num = data.get('groupNum')
        status_id = int(data.get('statusId'))

        try:
            user_in_account = Account.objects.get(user_id=uid)
            friend_in_account = Account.objects.get(user_id=friend_id)
        except ObjectDoesNotExist:
            return Response({
                'response': False,
                'message': '資料不存在'
            })

        if status_id not in [1, 4]:
            return Response({
                'response': False,
                'message': '狀態編號錯誤'
            })

        user_is_manager = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id=4)
        group_member = GroupMember.objects.filter(user_id=friend_id, group_no=group_num)
        if user_is_manager.exists() and group_member.exists():
            group_member.update(status_id=status_id)
            return Response({
                'response': True,
                'message': '成功'
            })
        elif not group_member.exists():
            return Response({
                'response': False,
                'message': '此人不是群組成員'
            })
        else:
            return Response({
                'response': False,
                'message': '非群組管理者，無法設定'
            })

    @action(detail=False)
    def get_log(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')

        group = GroupScheduleTime.objects.filter(serial_no=group_num, end_time__gte=datetime.now())
        user_in_group = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id__in=[1, 4])
        if group.exists() and user_in_group.exists():
            group_log = GroupLogDetail.objects.filter(group_no=group_num)
            return Response({
                'groupContent':
                    [
                        {
                            'doTime': g.do_time,
                            'name': g.name,
                            'logContent': g.content
                        }
                        for g in group_log
                    ]
            })
        else:
            return Response({'response': False, 'message': '沒有群組紀錄'})
