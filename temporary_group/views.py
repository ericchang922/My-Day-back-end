import base64
from datetime import datetime

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from temporary_group.serializers import ScheduleSerializer
from api.models import Schedule, Group, TemporaryList, GetGroup, GetTemporaryInvite, GetGroupNoVote, GroupMember


# Create your views here.
class TemporaryGroupViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    @action(detail=False, methods=['POST'])
    def create_schedule(self, request):
        data = request.data

        uid = data.get('uid')
        group_no = data.get('group_no')
        title = data.get('title')
        startTime = data.get('startTime')
        endTime = data.get('endTime')
        typeId = data.get('typeId')

        group_no = Group.objects.get(pk=group_no)

        Schedule.objects.create(connect_group_no=group_no,schedule_name=title,
                                schedule_start=startTime,schedule_end=endTime,
                                type_id=typeId)

        return Response({
            'response': True,
            'message': '成功'
        })


    @action(detail=False)
    def temporary_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        tg = TemporaryList.objects.filter(user_id=uid,status_id__in=[1,4],
                                          is_temporary_group=1, endtime__gte=datetime.now())

        if tg.count() > 0:
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
        else:
            return Response({
                'response': False,
                'message': '沒有玩聚'
            })

    @action(detail=False)
    def invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        tg = TemporaryList.objects.filter(user_id=uid, status_id=2,
                                          is_temporary_group=1, endtime__gte=datetime.now())

        if tg.count() > 0:
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
        else:
            return Response({
                'response': False,
                'message': '沒有玩聚邀請'
            })

    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        groupNum = data.get('groupNum')

        gr = GroupMember.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])
        if gr.count() > 0:
            tg = GetGroup.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])
            if tg.count() > 0:
                return Response({
                    'title': tg.first().group_name,
                    'typeId': tg.first().type_id,
                    'vote': [
                        {
                            'title': g.title,
                            'voteNum': g.votenum,
                            'isVoteType': g.votetype,
                        }
                        for g in tg
                    ]
                })
            else:
                tg = GetGroupNoVote.objects.filter(user_id=uid, group_no=groupNum, status_id__in=[1, 4])
                return Response({
                    'title': tg.first().group_name,
                    'typeId': tg.first().type_id,
                })
        else:
            return Response({
                'response': False,
                'message': '您不屬於此群組'
            })

    @action(detail=False)
    def get_invite(self, request):
        data = request.query_params

        groupNum = data.get('groupNum')
        tg = GetTemporaryInvite.objects.filter(group_no=groupNum)

        if tg.count() > 0:
            return Response({
                'title': tg.first().group_name,
                'startTime': tg.first().found_time,
                'endTime': tg.first().schedule_end,
                'founderPhoto': base64.b64encode(tg.first().founder_photo),
                'founderName': tg.first().founder_name,
                'member': [
                    {
                        'memberPhoto': base64.b64encode(g.member_photo),
                        'memberName': g.member_name,
                        'statusId': g.status_id,
                    }
                    for g in tg
                ]
            })
        else:
            return Response({
                'response': False,
                'message': '沒有此玩聚邀請'
            })
