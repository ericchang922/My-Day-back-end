from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Group, StudyPlan, Schedule, PlanContent, \
    GetStudyplan, StudyplanList, GroupStudyplanList, PersonalSchedule, GroupLog, Account, GroupMember, Note
from studyplan.serializers import StudyPlanSerializer, CreateStudyPlanSerializer, ScheduleSerializer


# Create your views here.
class StudyPlanViewSet(ModelViewSet):
    queryset = StudyPlan.objects.all()
    serializer_class = StudyPlanSerializer

    @action(detail=False, methods=['POST'])
    def create_studyplan(self, request):
        data = request.data
        if not Account.objects.filter(user_id=data['uid']).exists():
            return Response({'response':False, 'message':'帳號不存在'})

        uid = data.pop('uid')
        serializer = CreateStudyPlanSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        subjects = serializer.validated_data.pop('subjects')
        if len(subjects) == 0:
            return Response({'response': False, 'message': '至少要有一個課程'})

        subject_all = []
        num = 0
        no = None

        if not data['sheduleNum']:
            serializer.validated_data.update({'type_id': 1})
            schedule_no = serializer.save()
            no = StudyPlan.objects.create(create_id=uid, schedule_no=schedule_no)
        elif isinstance(data['sheduleNum'],int):
            if not Schedule.objects.filter(serial_no=data['sheduleNum']).exists():
                return Response({'response': False, 'message': '未有行程建立'})
            if not PersonalSchedule.objects.filter(schedule_no=data['sheduleNum'], user_id=uid).exists():
                return Response({'response': False, 'message': '您非此行程建立者'})
            if StudyPlan.objects.filter(schedule_no=data['sheduleNum']).count() > 0:
                return Response({'response': False, 'message': '此行程已有讀書計畫'})
            no = Schedule.objects.get(pk=data['sheduleNum'])
            type_id = ScheduleSerializer(no).data['type']
            if type_id == 1:
                schedule = Schedule.objects.get(serial_no=ScheduleSerializer(no).data['serial_no'])
                schedule.schedule_start = data['schedule_start']
                schedule.schedule_end = data['schedule_end']
                schedule.save()

                no = StudyPlan.objects.create(create_id=uid, schedule_no=no)
            else:
                return Response({
                    'response': False,
                    'message': '失敗，此行程非讀書計畫行程'
                })

        for subject in subjects:
            num += 1
            subject_item = PlanContent(plan_no=no, plan_num=num, subject=subject['subject'],
                                       plan_start=subject['plan_start'], plan_end=subject['plan_end']
                                       , is_rest=subject['is_rest'])
            subject_all.append(subject_item)
        PlanContent.objects.bulk_create(subject_all)

        return Response({
            'response': True,
            'message': '成功'
        })

    @action(detail=False, methods=['PATCH'])
    def edit_studyplan(self, request):
        data = request.data
        uid = data.pop('uid')
        studyplanNum = data.pop('studyplanNum')

        studyplan = StudyPlan.objects.filter(create_id=uid, serial_no=studyplanNum)
        if studyplan.exists():
            serializer = CreateStudyPlanSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            subjects = serializer.validated_data.pop('subjects')

            for subject in subjects:
                note_no = subject['note_no']
                if note_no and not Note.objects.filter(serial_no=note_no, create_id=uid).exists():
                    return Response({'response': False, 'message': '筆記選取錯誤'})

            if len(subjects) == 0:
                return Response({'response': False, 'message': '至少要有一個課程'})

            studyplan_no = StudyPlan.objects.get(pk=studyplanNum)
            plan_content = PlanContent.objects.filter(plan_no=studyplan_no)
            plan_content.delete()

            subject_all = []
            num = 0
            for subject in subjects:
                num += 1
                note_no = Note.objects.get(pk=subject['note_no']) if subject['note_no'] else None
                subject_item = PlanContent(plan_no=studyplan_no, plan_num=num, subject=subject['subject'],
                                           plan_start=subject['plan_start'], plan_end=subject['plan_end'],
                                           note_no=note_no, is_rest=subject['is_rest'])
                subject_all.append(subject_item)
            PlanContent.objects.bulk_create(subject_all)

            schedule_no = StudyPlanSerializer(studyplan_no).data['schedule_no']
            schedule = Schedule.objects.get(pk=schedule_no)

            schedule.schedule_name = data['schedule_name']
            schedule.schedule_start = data['schedule_start']
            schedule.schedule_end = data['schedule_end']
            schedule.save()
            if schedule.connect_group_no:
                GroupLog.objects.create(do_time=datetime.now(), group_no=schedule.connect_group_no, user_id=uid,
                                        trigger_type='U', do_type_id=4)

            return Response({
                'response': True,
                'message': '成功'
            })
        else:
            return Response({
                'response': False,
                'message': '您非此讀書計畫建立者，無法編輯'
            })


    @action(detail=False, methods=['PATCH'])
    def sharing(self, request):
        data = request.data

        uid = data.get('uid')
        studyplanNum = data.get('studyplanNum')
        groupNum = data.get('groupNum')

        user_studyplan = StudyPlan.objects.filter(create_id=uid, serial_no=studyplanNum)
        user_in_group = GroupMember.objects.filter(group_no=groupNum, user_id=uid, status_id__in=[1, 4])
        if user_studyplan.exists() and user_in_group.exists():
            studyplan = StudyPlan.objects.get(pk=studyplanNum)
            schedule_no = self.get_serializer(studyplan).data['schedule_no']

            groupNum = Group.objects.get(pk=groupNum)
            schedule = Schedule.objects.get(pk=schedule_no)
            if not schedule.connect_group_no:
                schedule.connect_group_no = groupNum
                schedule.save()
                GroupLog.objects.create(do_time=datetime.now(), group_no=groupNum, user_id=uid,
                                        trigger_type='I', do_type_id=4)
                return Response({
                    'response': True,
                    'message': '成功'
                })
            elif schedule.connect_group_no != groupNum:
                return Response({
                    'response': False,
                    'message': '失敗，讀書計畫僅能分享一個群組'
                })
            elif schedule.connect_group_no == groupNum:
                return Response({
                    'response': False,
                    'message': '已分享過給此群組'
                })
        elif not user_in_group.exists():
            return Response({
                'response': False,
                'message': '非此群組成員，無法分享'
            })
        return Response({
            'response': False,
            'message': '您非此讀書計畫建立者，無法分享'
        })

    @action(detail=False, methods=['PATCH'])
    def cancel_sharing(self, request):
        data = request.data

        uid = data.get('uid')
        studyplanNum = data.get('studyplanNum')

        user_studyplan = StudyPlan.objects.filter(create_id=uid, serial_no=studyplanNum)
        if user_studyplan.exists():
            studyplan = StudyPlan.objects.get(pk=studyplanNum)
            schedule_no = self.get_serializer(studyplan).data['schedule_no']
            schedule = Schedule.objects.get(pk=schedule_no)
            if schedule.connect_group_no:
                GroupLog.objects.create(do_time=datetime.now(), group_no=schedule.connect_group_no, user_id=uid,
                                        trigger_type='D', do_type_id=4)
                schedule.connect_group_no = None
                schedule.save()
                return Response({
                    'response': True,
                    'message': '成功'
                })
            return Response({
                'response': False,
                'message': '已取消分享'
            })
        else:
            return Response({
                'response': False,
                'message': '您非此讀書計畫建立者，無法取消分享'
            })

    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        data = request.data

        uid = data.get('uid')
        studyplanNum = data.get('studyplanNum')

        user_studyplan = StudyPlan.objects.filter(create_id=uid, serial_no=studyplanNum)
        if user_studyplan.exists():
            plan_content = PlanContent.objects.filter(pk=studyplanNum)
            plan_content.delete()

            studyplan = StudyPlan.objects.get(pk=studyplanNum)
            schedule_no = self.get_serializer(studyplan).data['schedule_no']
            studyplan.delete()

            personal_schedule = PersonalSchedule.objects.filter(schedule_no=schedule_no)
            if not personal_schedule.exists():
                schedule = Schedule.objects.get(pk=schedule_no)
                schedule.delete()

            return Response({
                'response': True,
                'message': '成功'
            })
        else:
            return Response({
                'response': False,
                'message': '您非此讀書計畫建立者，無法刪除'
            })

    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        studyplanNum = data.get('studyplanNum')
        studyplan = GetStudyplan.objects.filter(create_id=uid, plan_no=studyplanNum)

        if studyplan.count() > 0:
            return Response({
                'title': studyplan.first().schedule_name,
                'date': studyplan.first().field_date,
                'startTime': studyplan.first().schedule_start,
                'endTime': studyplan.first().schedule_end,
                'subject': [
                    {
                        'subjectName': s.subject,
                        'subjectStart': s.plan_start,
                        'subjectEnd': s.plan_end,
                        'rest': s.is_rest,
                    }
                    for s in studyplan
                ]
            })
        else:
            return Response({
                'response': False,
                'message': '沒有讀書計畫'
            })

    @action(detail=False)
    def personal_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        studyplan = StudyplanList.objects.filter(create_id=uid)

        return Response({
            'studyplan': [
                {
                    'studyplanNum': s.studyplan_num,
                    'title': s.schedule_name,
                    'date': s.field_date,
                    'startTime': s.schedule_start,
                    'endTime': s.schedule_end,
                }
                for s in studyplan
            ]
        })

    @action(detail=False)
    def group_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        studyplan = GroupStudyplanList.objects.filter(user_id=uid)

        return Response({
            'studyplan': [
                {
                    'studyplanNum': s.studyplan_num,
                    'title': s.schedule_name,
                    'date': s.field_date,
                    'startTime': s.schedule_start,
                    'endTime': s.schedule_end,
                }
                for s in studyplan
            ]
        })

    @action(detail=False)
    def one_group_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        groupNum = data.get('groupNum')
        studyplan = GroupStudyplanList.objects.filter(user_id=uid,group_no=groupNum,status_id__in=[1,4])

        return Response({
            'studyplan': [
                {
                    'studyplanNum': s.studyplan_num,
                    'title': s.schedule_name,
                    'date': s.field_date,
                    'startTime': s.schedule_start,
                    'endTime': s.schedule_end,
                }
                for s in studyplan
            ]
        })
