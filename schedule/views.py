from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from schedule.serializers import ScheduleSerilizer
from api.models import Schedule, ScheduleNotice, PersonalSchedule, Account, Type


# Create your views here.
class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerilizer

    @action(detail=False, methods=['POST'])
    def create_new(self, request):
        uid = request.data.get('uid')
        title = request.data.get('title')
        start_time = request.data.get('startTime')
        end_time = request.data.get('endTime')
        remind = request.data.get('remind')
        type_id = request.data.get('typeId')
        is_countdown = request.data.get('isCountdown')
        place = request.data.get('place')
        remark = request.data.get('remark')
        is_notice = remind.get('isRemind')

        type = Type.objects.get(type_id=type_id)
        try:
            new_schedule = Schedule.objects.create(schedule_name=title, type=type, schedule_start=start_time,
                                                   schedule_end=end_time, place=place)
            new_schedule.save()

            schedule_no = Schedule.objects.get(serial_no= new_schedule.serial_no)

            print(schedule_no)
            user_id = Account.objects.get(user_id= uid)
            print(user_id)
            new_personal_schedule = PersonalSchedule.objects.create(user=user_id, schedule_no=schedule_no,
                                                                    is_notice=is_notice, is_countdown=is_countdown,
                                                                    is_hidden=False, remark=remark)
            new_personal_schedule.save()
            personal_schedule_no = PersonalSchedule.objects.get(serial_no=new_personal_schedule.serial_no)

            if remind.get('isRemind') == True:
                for i in remind.get('remindTime'):
                    print(i)
                    if i == 'isRemind':
                        continue
                    else:
                        new_schedule_notice = ScheduleNotice.objects.create(personal_schedule_no=personal_schedule_no,
                                                                            notice_time=i)
                        new_schedule_notice.save()
        except:
            return Response({'Response': 'error'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Response': 'success'}, status=status.HTTP_201_CREATED)
