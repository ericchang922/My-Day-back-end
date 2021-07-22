import base64
from datetime import datetime

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from group.views import new_group_request
from temporary_group.serializers import ScheduleSerializer, CreateTmpGroupRequestSerializer
from api.models import Schedule, TemporaryList, GetTemporaryInvite, PersonalSchedule


# Create your views here.
class TemporaryGroupViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    @action(detail=False, methods=['POST'])
    def create_group(self, request):
        data = request.data

        serializer = CreateTmpGroupRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        schedule_start_time = serializer.validated_data.pop('scheduleStartTime')
        schedule_end_time = serializer.validated_data.pop('scheduleEndTime')
        if schedule_start_time > schedule_end_time:
            return Response({'response': False, 'message': '開始時間需小於結束時間'})

        place = serializer.validated_data.pop('place')
        serializer.validated_data.update({'is_temporary_group': 1})

        result = new_group_request(serializer.validated_data)
        if result == -1:
            return Response({'response': False, 'message': '帳號不存在'})
        elif result == -2:
            return Response({'response': False, 'message': '僅能邀請好友'})

        group = result
        schedule_name = serializer.validated_data['group_name']
        type_id = serializer.validated_data['type']
        founder = serializer.validated_data['founder']
        schedule = Schedule.objects.create(schedule_name=schedule_name, connect_group_no=group,
                                           type_id=type_id, schedule_start=schedule_start_time,
                                           schedule_end=schedule_end_time, place=place)

        PersonalSchedule.objects.create(user_id=founder, schedule_no=schedule, is_notice=0,
                                        is_countdown=0, is_hidden=0)
        return Response({
            'response': True,
            'message': '成功'
        })

    @action(detail=False)
    def temporary_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        tmp_group = TemporaryList.objects.filter(user_id=uid, status_id__in=[1, 4],
                                                 is_temporary_group=1, end_time__gte=datetime.now())

        return Response({
            'temporaryContent': [
                {
                    'groupId': g.group_no,
                    'typeId': g.type_id,
                    'title': g.group_name,
                    'startTime': g.start_time,
                    'endTime': g.end_time,
                    'peopleCount': g.cnt,
                }
                for g in tmp_group
            ]
        })

    @action(detail=False)
    def invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        tmp_group = TemporaryList.objects.filter(user_id=uid, status_id=2,
                                                 is_temporary_group=1, end_time__gte=datetime.now())

        return Response({
            'temporaryContent': [
                {
                    'groupId': g.group_no,
                    'typeId': g.type_id,
                    'title': g.group_name,
                    'startTime': g.start_time,
                    'endTime': g.end_time,
                    'peopleCount': g.cnt,
                }
                for g in tmp_group
            ]
        })

    @action(detail=False)
    def get_invite(self, request):
        data = request.query_params

        group_num = data.get('groupNum')
        tmp_group_invite = GetTemporaryInvite.objects.filter(group_no=group_num)

        if tmp_group_invite.exists():
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
