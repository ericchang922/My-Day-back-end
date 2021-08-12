from datetime import datetime

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from api.response import *
from api.models import Schedule, TemporaryList, PersonalSchedule, GroupMember, Group, GroupScheduleTime
from group.views import new_group_request
from temporary_group.serializers import TemporaryGroupSerializer, CreateTmpGroupRequestSerializer


# Create your views here.
class TemporaryGroupViewSet(ModelViewSet):
    queryset = Group.objects.filter(serial_no=0)
    serializer_class = TemporaryGroupSerializer

    @action(detail=False, methods=['POST'])
    def create_group(self, request):
        data = request.data

        serializer = CreateTmpGroupRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        schedule_start_time = serializer.validated_data.pop('schedule_start')
        schedule_end_time = serializer.validated_data.pop('schedule_end')
        if schedule_start_time > schedule_end_time:
            return err(Msg.Err.Group.time, 'TMP-A-001', request)

        place = serializer.validated_data.pop('place')
        serializer.validated_data.update({'is_temporary_group': 1})

        result = new_group_request(serializer.validated_data)
        if isinstance(result, str):
            return not_found(result, request)

        group = result
        schedule_name = serializer.validated_data['group_name']
        type_id = serializer.validated_data['type']
        founder = serializer.validated_data['founder']
        schedule = Schedule.objects.create(schedule_name=schedule_name, connect_group_no=group,
                                           type_id=type_id, schedule_start=schedule_start_time,
                                           schedule_end=schedule_end_time, place=place)

        PersonalSchedule.objects.create(user_id=founder, schedule_no=schedule, is_notice=1,
                                        is_countdown=1, is_hidden=0)
        return success(request=request)

    @action(detail=False)
    def temporary_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        tmp_group = TemporaryList.objects.filter(user_id=uid, status_id__in=[1, 4], is_temporary_group=1,
                                                 end_time__gt=datetime.now()).order_by('-start_time')
        return success({
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
        }, request)

    @action(detail=False)
    def invite_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        tmp_group = TemporaryList.objects.filter(user_id=uid, status_id=2, is_temporary_group=1,
                                                 end_time__gt=datetime.now()).order_by('-start_time')
        return success({
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
        }, request)

    @action(detail=False)
    def get_invite(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')

        tmp_group = GroupScheduleTime.objects.filter(serial_no=group_num, is_temporary_group=1,
                                                     end_time__gt=datetime.now())
        user_is_invited = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id=2)

        if tmp_group.exists() and user_is_invited.exists():
            schedule = Schedule.objects.filter(connect_group_no=group_num)
            group = Group.objects.get(serial_no=group_num)
            group_member = GroupMember.objects.filter(group_no=group_num)
            return success({
                'title': group.group_name,
                'startTime': schedule.order_by('schedule_start').first().schedule_start,
                'endTime': schedule.order_by('-schedule_end').first().schedule_end,
                'founderPhoto': group.founder.photo,
                'founderName': group.founder.name,
                'member': [
                    {
                        'memberPhoto': g.user.photo,
                        'memberName': g.user.name,
                        'statusId': g.status_id
                    }
                    for g in group_member
                ]
            }, request)
        elif not tmp_group.exists():
            return not_found(Msg.NotFound.group, request)
        else:
            return not_found(Msg.NotFound.group_invite, request)
