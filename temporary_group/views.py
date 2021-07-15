import base64
from datetime import datetime

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from temporary_group.serializers import ScheduleSerializer
from api.models import Schedule, Group, TemporaryList, GetGroup, GetTemporaryInvite, GetGroupNoVote, GroupMember, \
    GroupLog


# Create your views here.
class TemporaryGroupViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    @action(detail=False, methods=['POST'])
    def create_schedule(self, request):
        data = request.data

        uid = data.get('uid')
        groupNum = data.get('groupNum')
        title = data.get('title')
        startTime = data.get('startTime')
        endTime = data.get('endTime')
        typeId = data.get('typeId')

        group_member = GroupMember.objects.filter(group_no=groupNum, user_id=uid, status_id__in=[1, 4])
        if group_member.exists():
            groupNum = Group.objects.get(serial_no=groupNum)
            Schedule.objects.create(connect_group_no=groupNum,schedule_name=title,
                                    schedule_start=startTime,schedule_end=endTime,
                                    type_id=typeId)
            GroupLog.objects.create(do_time=datetime.now(), group_no=groupNum,user_id=uid,
                                    trigger_type='I', do_type_id=3)
            return Response({
                'response': True,
                'message': '成功'
            })
        return Response({
            'response': False,
            'message': '非群組成員，故無法建立'
        })

    @action(detail=False)
    def temporary_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        tg = TemporaryList.objects.filter(user_id=uid,status_id__in=[1,4],
                                          is_temporary_group=1, endtime__gte=datetime.now())

        return Response({
            'temporaryContent': [
                {
                    'groupId': g.group_no,
                    'typeId': g.type_id,
                    'title': g.group_name,
                    'startTime': g.starttime,
                    'endTime': g.endtime,
                    'peopleCount': g.cnt,
                }
                for g in tg
            ]
        })

    @action(detail=False)
    def invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        tmp_group = TemporaryList.objects.filter(user_id=uid, status_id=2,
                                                is_temporary_group=1, endtime__gte=datetime.now())

        return Response({
            'temporaryContent': [
                {
                    'groupId': g.group_no,
                    'typeId': g.type_id,
                    'title': g.group_name,
                    'startTime': g.starttime,
                    'endTime': g.endtime,
                    'peopleCount': g.cnt,
                }
                for g in tmp_group
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
    def get_invite(self, request):
        data = request.query_params

        groupNum = data.get('groupNum')
        tmp_group_invite = GetTemporaryInvite.objects.filter(group_no=groupNum)

        if tmp_group_invite.count() > 0:
            return Response({
                'title': tmp_group_invite.first().group_name,
                'startTime': tmp_group_invite.first().found_time,
                'endTime': tmp_group_invite.first().schedule_end,
                'founderPhoto': base64.b64encode(tmp_group_invite.first().founder_photo),
                'founderName': tmp_group_invite.first().founder_name,
                'member': [
                    {
                        'memberPhoto': base64.b64encode(g.member_photo),
                        'memberName': g.member_name,
                        'statusId': g.status_id,
                    }
                    for g in tmp_group_invite
                ]
            })
        else:
            return Response({
                'response': False,
                'message': '沒有此玩聚邀請'
            })
