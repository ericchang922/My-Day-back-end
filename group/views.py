from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from datetime import datetime
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.response import *
from api.models import Account, Group, GroupMember, GroupList, GroupLog, GroupScheduleTime, Friend, Vote
from group.functions import new_group_request
from group.serializers import GroupSerializer


# Create your views here.
class GroupViewSet(ModelViewSet):
    queryset = Group.objects.filter(serial_no=0)
    serializer_class = GroupSerializer

    @action(detail=False, methods=['POST'])
    def create_group(self, request):
        data = request.data
        data['is_temporary_group'] = 0

        result = new_group_request(data)
        if isinstance(result, str):
            return not_found(result, request)
        return success(request=request)

    @action(detail=False, methods=['PATCH'])
    def edit_group(self, request):
        data = request.data

        uid = data.get('uid')
        group_num = data.get('groupNum')
        title = str(data.get('title'))
        type_id = int(data.get('typeId'))

        user_in_group = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id__in=[1, 4])
        if user_in_group.exists():
            group = Group.objects.get(serial_no=group_num)
            if title and title != group.group_name:
                old_title = group.group_name
                group.group_name = title
                group.save()
                GroupLog.objects.create(do_time=datetime.now(), group_no=group, user_id=uid,
                                        trigger_type='U', do_type_id=1,
                                        old=old_title, new=group.group_name)

            if type_id and type_id != group.type_id:
                old_type_name = group.type.type_name
                group.type_id = type_id
                group.save()
                GroupLog.objects.create(do_time=datetime.now(), group_no=group, user_id=uid,
                                        trigger_type='U', do_type_id=1,
                                        old=f'{old_type_name}類型', new=f'{group.type.type_name}類型')

            return success(request=request)
        else:
            return no_authority('群組成員', request)

    @action(detail=False, methods=['POST'])
    def invite_friend(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')
        group_num = data.get('groupNum')

        try:
            group_num = Group.objects.get(pk=group_num)
            user_is_manager = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id=4)
            friendship = Friend.objects.filter(user_id=uid, related_person=friend_id, relation_id__in=[1, 2])

            if user_is_manager.exists() and friendship.exists():
                GroupMember.objects.create(group_no=group_num, user_id=friend_id, status_id=2, inviter_id=uid)
                return success(request=request)
            elif not friendship.exists():
                return err(Msg.Err.Group.friend_only, 'GR-C-001', request)
            else:
                return no_authority('群組管理者', request)
        except IntegrityError:
            return err(Msg.Err.Group.already_invited, 'GR-C-002', request)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.group, request)

    @action(detail=False, methods=['PATCH'])
    def member_status(self, request):
        data = request.data

        uid = data.get('uid')
        group_num = data.get('groupNum')
        status_id = int(data.get('statusId'))

        group = GroupScheduleTime.objects.filter(serial_no=group_num, end_time__gt=datetime.now())
        group_member = GroupMember.objects.filter(group_no=group_num)
        user_in_group = group_member.filter(user_id=uid)

        if user_in_group.filter(status_id__in=[1, 4]).exists():
            return err(Msg.Err.Group.already_joined, 'GR-D-001', request)
        if (not group.exists() or not group_member.exists()) and status_id == 1:
            return not_found(Msg.NotFound.group, request)

        if user_in_group.filter(status_id=2).exists():
            if status_id == 1:
                user_in_group.update(status_id=1, join_time=datetime.now())
                return success(request=request)
            elif status_id == 3:
                user_in_group.delete()
                return success(request=request)
        elif status_id != 1:
            return not_found(Msg.NotFound.member_status, request)

        try:
            user = Account.objects.get(user_id=uid)
            group = Group.objects.get(serial_no=group_num)
            GroupMember.objects.create(group_no=group, user_id=user.pk,
                                       status_id=1, join_time=datetime.now(), inviter_id=user.pk)
            return success(request=request)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.group, request)

    @action(detail=False, methods=['PATCH'])
    def setting_manager(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')
        group_num = data.get('groupNum')
        status_id = data.get('statusId')

        if uid == friend_id:
            return err(Msg.Err.Group.must_choose_others, 'GR-E-001', request)
        if status_id not in [1, 4]:
            return not_found(Msg.NotFound.member_status, request)

        user_is_manager = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id=4)
        group_member = GroupMember.objects.filter(user_id=friend_id, group_no=group_num, status_id__in=[1, 4])

        if user_is_manager.exists() and group_member.exists():
            group_member.update(status_id=status_id)
            return success(request=request)
        elif not group_member.exists():
            return not_found(Msg.NotFound.member, request)
        else:
            return no_authority('群組管理者', request)

    @action(detail=False, methods=['DELETE'])
    def quit_group(self, request):
        data = request.data

        uid = data.get('uid')
        group_num = data.get('groupNum')

        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])
        group_manager = GroupMember.objects.filter(group_no=group_num, status_id=4)
        group_member = GroupMember.objects.filter(group_no=group_num, status_id__in=[1, 2])

        if not user_in_group.exists():
            return not_found(Msg.NotFound.user_has_left, request)
        elif user_in_group.first().status_id == 4 and group_manager.count() == 1 and group_member.count() > 0:
            return err(Msg.Err.Group.only_one_manager, 'GR-F-001', request)

        user_in_group.delete()
        return success(request=request)

    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')

        group = GroupScheduleTime.objects.filter(serial_no=group_num, end_time__gt=datetime.now())
        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])

        if group.exists() and user_in_group.exists():
            group_vote = Vote.objects.filter(group_no=group_num)
            return success({
                'title': group.first().group_name,
                'typeId': group.first().type_id,
                'vote': [
                    {
                        'title': g.title,
                        'voteNum': g.serial_no,
                        'isVoteType': True if not g.end_time or datetime.now() < g.end_time else False,
                    }
                    for g in group_vote
                ]
            }, request)
        elif not group.exists():
            return not_found(Msg.NotFound.group, request)
        else:
            return not_found(Msg.NotFound.not_in_group, request)

    @action(detail=False)
    def member_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')

        user_in_group = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id__in=[1, 4])
        if user_in_group.exists():
            founder = Group.objects.get(pk=group_num).founder
            group_member = GroupMember.objects.filter(group_no=group_num)
            return success({
                'founderPhoto': founder.photo,
                'founderName': founder.name,
                'founderId': founder.pk,
                'member': [
                    {
                        'memberPhoto': g.user.photo,
                        'memberName': g.user.name,
                        'memberId': g.user.pk,
                        'statusId': g.status_id,
                    }
                    for g in group_member
                ]
            }, request)
        else:
            return not_found(Msg.NotFound.not_in_group, request)

    @action(detail=False)
    def invite_friend_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')
        friend_status_id = int(data.get('friendStatusId'))

        if friend_status_id not in [1, 2]:
            return not_found(Msg.NotFound.relation)

        user_in_group = GroupMember.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])
        if user_in_group.exists():
            group_member = GroupMember.objects.filter(group_no=group_num)
            friend = Friend.objects.filter(user_id=uid, relation_id=friend_status_id)\
                .exclude(related_person__in=group_member.values_list('user_id'))
            return success({
                'friend': [
                    {
                        'photo': f.related_person.photo,
                        'friendId': f.related_person.pk,
                        'friendName': f.related_person.name
                    }
                    for f in friend
                ]
            }, request)
        else:
            return not_found(Msg.NotFound.not_in_group, request)

    @action(detail=False)
    def group_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group = GroupList.objects.filter(user_id=uid, status_id__in=[1, 4],
                                         is_temporary_group=0).order_by('-join_time')
        return success({
            'groupContent': [
                {
                    'groupID': g.group_no,
                    'title': g.group_name,
                    'typeId': g.type_id,
                    'peopleCount': g.cnt,
                }
                for g in group
            ]
        }, request)

    @action(detail=False)
    def invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group = GroupList.objects.filter(user_id=uid, status_id=2,
                                         is_temporary_group=0).order_by('-join_time')
        return success({
            'groupContent': [
                {
                    'groupId': g.group_no,
                    'title': g.group_name,
                    'typeId': g.type_id,
                    'inviterPhoto': g.inviter_photo,
                    'inviterName': g.inviter_name
                }
                for g in group
            ]
        }, request)

    @action(detail=False)
    def get_log(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')

        group = GroupScheduleTime.objects.filter(serial_no=group_num, end_time__gt=datetime.now())
        user_in_group = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id__in=[1, 4])

        if group.exists() and user_in_group.exists():
            group_content = []
            trigger_name = {'I': '建立了', 'U': '編輯了', 'D': '刪除了'}

            group_log = GroupLog.objects.filter(group_no=group_num).order_by('do_time')
            for log in group_log:
                group = {'doTime': log.do_time, 'name': log.user.name}
                type_name = log.do_type.do_type_name
                do_type = log.do_type.pk

                if log.new and log.old:
                    content = f'把{type_name}從「{log.old}」改為「{log.new}」'
                elif do_type == 2:
                    if log.trigger_type in ['I', 'D']:
                        content = '已加入群組' if log.trigger_type == 'I' else '已離開群組'
                    else:
                        content = '已成為管理者' if log.new else '已不是管理者'
                else:
                    title = log.new if log.new else log.old
                    if do_type in [4, 7] and log.trigger_type in ['I', 'D']:
                        content = '分享了' if log.trigger_type == 'I' else '取消分享了'
                        content += f'{type_name}「{title}」'
                    elif do_type == 6:
                        content = '新增了' if log.new else trigger_name['D']
                        content += f'「{title}」的{type_name}'
                    else:
                        content = f'{trigger_name[log.trigger_type]}{type_name}「{title}」'
                group['logContent'] = content
                group_content.append(group)
            return success({'groupContent': group_content}, request)
        elif not group.exists():
            return not_found(Msg.NotFound.group, request)
        else:
            return not_found(Msg.NotFound.not_in_group, request)
