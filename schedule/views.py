# python
from datetime import datetime
# django
from django.db.models import ObjectDoesNotExist
# rest
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
# my day
from schedule.serializers import ScheduleSerializer
from api.models import Schedule, ScheduleNotice, PersonalSchedule, Type, GroupMember, Group
# schedule
from api.response import *


class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.filter(serial_no=0)
    serializer_class = ScheduleSerializer

    # /schedule/create_new/  ------------------------------------------------------------------------------------------A
    @action(detail=False, methods=['POST'])
    def create_new(self, request):
        data = request.data

        uid = data['uid']
        title = data['title']
        start_time = data['startTime']
        end_time = data['endTime']
        remind = data['remind']
        remind_time = remind['remindTime']
        is_notice = remind['isRemind']
        type_id = data['typeId']
        is_countdown = data['isCountdown']
        place = data['place']
        remark = data['remark']

        try:
            schedule = Schedule.objects.create(schedule_name=title, type_id=type_id, schedule_start=start_time,
                                               schedule_end=end_time, place=place)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.create, 'SC-A-001')  # ----------------------------------------------------001
        try:
            personal_schedule = PersonalSchedule.objects.create(user_id=uid, schedule_no=schedule, is_notice=is_notice,
                                                                is_countdown=is_countdown, is_hidden=False,
                                                                remark=remark)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.personal_select, 'SC-A-002')  # -------------------------------------------002
        try:
            for i in remind_time:
                ScheduleNotice.objects.create(personal_schedule_no=personal_schedule, notice_time=i)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.notice_create, 'SC-A-003')  # ---------------------------------------------003

        return success()

    # /schedule/edit/  ------------------------------------------------------------------------------------------------B
    @action(detail=False, methods=['POST'])
    def edit(self, request):
        data = request.data

        uid = data['uid']
        schedule_no = data['scheduleNum']
        try:
            schedule = Schedule.objects.get(serial_no=schedule_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.schedule)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.select, 'SC-B-001')  # ----------------------------------------------------001

        try:
            personal_schedule = PersonalSchedule.objects.get(schedule_no=schedule, user_id=uid)
        except ObjectDoesNotExist:
            if schedule.connect_group_no is None:
                return not_found(Msg.NotFound.personal_schedule)

            try:
                GroupMember.objects.get(group_no=schedule.connect_group_no.serial_no, user_id=uid,
                                        status__in=[1, 4])
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.not_in_group)

            try:
                personal_schedule = PersonalSchedule.objects.create(user_id=uid, schedule_no=schedule, is_notice=False,
                                                                    is_countdown=False, is_hidden=False)
            except Exception as e:
                print(e)
                return err(Msg.Err.Schedule.personal_create, 'SC-B-002')  # ---------------------------------------002
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.personal_select, 'SC-B-003')  # -------------------------------------------003

        try:
            schedule_notice = ScheduleNotice.objects.filter(personal_schedule_no=personal_schedule)
            schedule_notice_list = []
            for i in schedule_notice:
                schedule_notice_list.append(str(i.notice_time))
        except Exception as e:
            print(e)
            schedule_notice_list = []

        title = data['title'] if data['title'] != schedule.schedule_name else None
        start_time = data['startTime'] if data['startTime'] != schedule.schedule_start else None
        end_time = data['endTime'] if data['endTime'] != schedule.schedule_end else None
        remind = data['remind']
        is_remind = remind['isRemind'] if remind is not None else None
        remind_time = remind['remindTime'] if remind is not None else None
        type_id = data['typeId'] if data['typeId'] != schedule.type else None
        is_countdown = data['isCountdown'] if data['isCountdown'] != personal_schedule.is_countdown else None
        place = data['place'] if data['place'] != schedule.place else None
        remark = data['remark'] if data['remark'] != personal_schedule.remark else None

        def update_remind():
            for r in remind_time:
                if r in schedule_notice_list:
                    continue
                else:
                    ScheduleNotice.objects.create(personal_schedule_no=personal_schedule, notice_time=r)

            for s in schedule_notice_list:
                if s not in remind_time:
                    try:
                        del_notice = ScheduleNotice.objects.get(personal_schedule_no=personal_schedule, notice_time=s)
                        del_notice.delete()
                    except ObjectDoesNotExist:
                        return not_found(Msg.NotFound.schedule_notice)
                    except:
                        return err(Msg.Err.Schedule.notice_delete, 'SC-B-004')  # ---------------------------------004

        if title is not None:
            schedule.schedule_name = title

        if start_time is not None:
            schedule.schedule_start = start_time

        if end_time is not None:
            schedule.schedule_end = end_time

        if remind is not None:
            if is_remind is not None:
                personal_schedule.is_notice = is_remind
            if len(remind_time) > 0:
                update_remind()
        else:
            personal_schedule.is_notice = False

        if type_id is not None:
            schedule.type_id = type_id

        if is_countdown is not None:
            personal_schedule.is_countdown = is_countdown

        if place is not None:
            schedule.place = place

        if remark is not None:
            personal_schedule.remark = remark

        schedule.save()
        personal_schedule.save()

        return success()

    # /schedule/delete/  ----------------------------------------------------------------------------------------------C
    @action(detail=False, methods=['POST'])
    def delete(self, request):
        data = request.data

        uid = data['uid']
        schedule_no = data['scheduleNum']

        try:
            personal_schedule = PersonalSchedule.objects.get(schedule_no=schedule_no, user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.personal_schedule)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.personal_select, 'SC-C-001')  # -------------------------------------------001

        try:
            schedule_notice = ScheduleNotice.objects.filter(personal_schedule_no=personal_schedule)
            schedule_notice.delete()
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.notice_delete, 'SC-C-002')  # ---------------------------------------------002

        try:
            personal_schedule.delete()
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.personal_delete, 'SC-C-003')  # -------------------------------------------003

        return success()

    # /schedule/get/  -------------------------------------------------------------------------------------------------D
    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data['uid']
        schedule_no = data['scheduleNum']

        try:
            schedule = Schedule.objects.get(serial_no=schedule_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.schedule)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.select, 'SC-D-001')  # ----------------------------------------------------001

        try:
            personal_schedule = PersonalSchedule.objects.get(schedule_no=schedule, user=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.personal_schedule)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.personal_select, 'SC-D-002')  # -------------------------------------------002

        try:
            schedule_notice = ScheduleNotice.objects.filter(personal_schedule_no=personal_schedule)
            remind = []
            for i in schedule_notice:
                remind.append(str(i.notice_time))
        except Exception as e:
            print(e)
            remind = []

        response = {
            'title': str(schedule.schedule_name),
            'startTime': str(schedule.schedule_start),
            'endTime': str(schedule.schedule_end),
            'remind': {
                'isRemind': bool(personal_schedule.is_notice),
                'remindTime': remind
            },
            'typeId': int(schedule.type_id),
            'isCountdown': bool(personal_schedule.is_countdown),
            'place': schedule.place,
            'remark': personal_schedule.remark
        }
        return success(response)

    # /schedule/get_list/  --------------------------------------------------------------------------------------------E
    @action(detail=False)
    def get_list(self, request):
        data = request.query_params

        uid = data['uid']

        try:
            personal_schedule = PersonalSchedule.objects.filter(user=uid).all()
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.personal_select, 'SC-E-001')  # -------------------------------------------001

        schedule_list = []
        try:
            for i in personal_schedule:
                schedule = Schedule.objects.get(serial_no=i.schedule_no.serial_no)
                schedule_list.append(
                    {
                        'scheduleNum': schedule.serial_no,
                        'title': schedule.schedule_name,
                        'startTime': schedule.schedule_start,
                        'endTime': schedule.schedule_end,
                        'typeId': schedule.type_id
                    }
                )
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.schedule)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.select, 'SC-E-002')  # ----------------------------------------------------002

        response = {'schedule': schedule_list}
        return success(response)

    # /schedule/create_common/  ---------------------------------------------------------------------------------------F
    @action(detail=False, methods=['POST'])
    def create_common(self, request):
        data = request.data

        uid = data['uid']
        group_no = data['groupNum']
        title = data['title']
        start_time = data['startTime']
        end_time = data['endTime']
        type_id = data['typeId']
        place = data['place']

        try:
            group = Group.objects.get(serial_no=group_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.group)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.select, 'SC-F-001')  # -------------------------------------------------------001

        try:
            GroupMember.objects.get(group_no=group, user_id=uid, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'SC-F-002')  # --------------------------------------------------002

        try:
            schedule = Schedule.objects.create(schedule_name=title, connect_group_no=group, type_id=type_id,
                                               schedule_start=start_time, schedule_end=end_time, place=place)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.create, 'SC-F-003')  # ----------------------------------------------------003

        try:
            group_member = GroupMember.objects.filter(group_no=group_no, status__in=[1, 4])
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'SC-F-004')  # --------------------------------------------------004

        for i in group_member:
            try:
                PersonalSchedule.objects.create(user=i.user, schedule_no=schedule, is_notice=False,
                                                is_countdown=False, is_hidden=False)
            except Exception as e:
                print(e)
                return err(Msg.Err.Schedule.personal_create, 'SC-F-005')  # ---------------------------------------005

        return success()

    # /schedule/get_common/  ------------------------------------------------------------------------------------------G
    @action(detail=False)
    def get_common(self, request):
        data = request.query_params

        uid = data['uid']
        schedule_no = data['scheduleNum']

        try:
            schedule = Schedule.objects.get(serial_no=schedule_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.schedule)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.select, 'SC-G-001')  # ----------------------------------------------------001

        try:
            PersonalSchedule.objects.get(schedule_no=schedule, user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.personal_schedule)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.personal_select, 'SC-G-002')  # -------------------------------------------002

        if schedule.connect_group_no is None:
            return not_found(Msg.NotFound.common_schedule)

        try:
            # 此功能是在有人建立共同行程後成員會收到通知時使用的，因此要驗證是否在群組內
            GroupMember.objects.get(user=uid, group_no=schedule.connect_group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'SC-G-003')  # --------------------------------------------------003

        response = {
            'title': str(schedule.schedule_name),
            'startTime': str(schedule.schedule_start),
            'endTime': str(schedule.schedule_end),
            'typeName': str(schedule.type.type_name),
            'place': schedule.place
        }
        return success(response)

    # /schedule/common_list/ ------------------------------------------------------------------------------------------H
    @action(detail=False)
    def common_list(self, request):
        data = request.query_params

        uid = data['uid']
        group_no = data['groupNum']

        try:
            GroupMember.objects.get(user=uid, group_no=group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'SC-H-001')  # --------------------------------------------------001

        try:
            schedule = Schedule.objects.filter(connect_group_no=group_no)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.select, 'SC-H-002')  # ----------------------------------------------------002

        schedule_list = []
        for i in schedule:
            schedule_list.append(
                {
                    'scheduleNum': int(i.serial_no),
                    'title': str(i.schedule_name),
                    'startTime': str(i.schedule_start),
                    'endTime': str(i.schedule_end),
                    'typeName': str(Type.objects.get(type_id=i.type_id).type_name)
                }
            )

        response = {'schedule': schedule_list}
        return success(response)

    # /schedule/common_hidden/  ---------------------------------------------------------------------------------------I
    @action(detail=False, methods=['POST'])
    def common_hidden(self, request):
        data = request.data

        uid = data['uid']
        schedule_no = data['scheduleNum']
        is_hidden = data['isHidden']

        try:
            personal_schedule = PersonalSchedule.objects.get(user=uid, schedule_no=schedule_no)
            personal_schedule.is_hidden = is_hidden
            personal_schedule.save()
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.no_personal_schedule)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.select, 'SC-I-001')  # ----------------------------------------------------001

        return success()

    # /schedule/countdown_list/  --------------------------------------------------------------------------------------J
    @action(detail=False)
    def countdown_list(self, request):
        data = request.query_params

        uid = data['uid']

        try:
            personal_schedule = PersonalSchedule.objects.filter(user=uid, is_countdown=True)
        except Exception as e:
            print(e)
            return err(Msg.Err.Schedule.personal_select, 'SC-J-001')  # -------------------------------------------001

        now = datetime.now()
        schedule_list = []
        for i in personal_schedule:
            try:
                schedule = Schedule.objects.get(serial_no=i.schedule_no.serial_no)
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.schedule)
            except Exception as e:
                print(e)
                return err(Msg.Err.Schedule.select, 'SC-J-002')  # ------------------------------------------------002

            days = schedule.schedule_start - now
            days = days.days
            if days >= 0:
                schedule_list.append(
                    {
                        'title': schedule.schedule_name,
                        'countdownDate': days
                        # 未滿24小時不算一天
                    }
                )

        response = {'schedule': schedule_list}
        return success(response)
