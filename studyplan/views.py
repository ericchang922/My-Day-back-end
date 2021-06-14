from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Group, StudyPlan, Schedule, PlanContent, \
                        GetStudyplan, StudyplanList, GroupStudyplanList
from studyplan.serializers import StudyPlanSerializer, CreateStudyPlanSerializer, ScheduleSerializer


# Create your views here.
class StudyPlanViewSet(ModelViewSet):
    queryset = StudyPlan.objects.all()
    serializer_class = StudyPlanSerializer

    @action(detail=False, methods=['POST'])
    def create_studyplan(self, request):
        data = request.data
        uid = data.pop('uid')

        serializer = CreateStudyPlanSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        subjects = serializer.validated_data.pop('subjects')

        subject_all = []
        num = 0
        no = None

        if data['sheduleNum'] == None:
            serializer.validated_data.update({'type_id': 1})
            schedule_no = serializer.save()
            no = StudyPlan.objects.create(create_id=uid, schedule_no=schedule_no)
        elif isinstance(data['sheduleNum'],int):
            no = Schedule.objects.get(pk=data['sheduleNum'])
            type_id = ScheduleSerializer(no).data['type']
            if type_id == 1:
                sc = Schedule.objects.get(serial_no=ScheduleSerializer(no).data['serial_no'])
                sc.schedule_start = data['schedule_start']
                sc.schedule_end = data['schedule_end']
                sc.save()

                no = StudyPlan.objects.create(create_id=uid, schedule_no=no)
            else:
                return Response({
                    'response': '失敗，此行程非讀書計畫行程'
                })

        for subject in subjects:
            num += 1
            subject_item = PlanContent(plan_no=no, plan_num=num, subject=subject['subject'],
                                       plan_start=subject['plan_start'], plan_end=subject['plan_end']
                                       , is_rest=subject['is_rest'])
            subject_all.append(subject_item)
        PlanContent.objects.bulk_create(subject_all)

        return Response({
            'response': '成功'
        })


    @action(detail=False, methods=['PATCH'])
    def edit_studyplan(self, request):
        data = request.data
        uid = data.pop('uid')
        studyplanNum = data.pop('studyplanNum')

        st = StudyPlan.objects.filter(create_id=uid, serial_no=studyplanNum)
        if st.count() > 0:
            serializer = CreateStudyPlanSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            subjects = serializer.validated_data.pop('subjects')

            studyplan_no = StudyPlan.objects.get(pk=studyplanNum)
            pl = PlanContent.objects.filter(plan_no=studyplan_no)
            pl.delete()

            subject_all = []
            num = 0
            for subject in subjects:
                num += 1
                subject_item = PlanContent(plan_no=studyplan_no, plan_num=num, subject=subject['subject'],
                                           plan_start=subject['plan_start'], plan_end=subject['plan_end']
                                           , is_rest=subject['is_rest'])
                subject_all.append(subject_item)
            PlanContent.objects.bulk_create(subject_all)

            schedule_no = StudyPlanSerializer(studyplan_no).data['schedule_no']
            sc = Schedule.objects.get(pk=schedule_no)

            sc.schedule_name = data['schedule_name']
            sc.schedule_start = data['schedule_start']
            sc.schedule_end = data['schedule_end']
            sc.save()

            return Response({
                'response': '成功'
            })
        else:
            return Response({
                'response': '您非此讀書計畫建立者，無法編輯'
            })


    @action(detail=False, methods=['PATCH'])
    def sharing(self, request):
        uid = request.query_params.get('uid')
        studyplanNum = request.query_params.get('studyplanNum')
        groupNum = request.query_params.get('groupNum')

        st = StudyPlan.objects.filter(create_id=uid, serial_no=studyplanNum)
        if st.count() > 0:
            sc = StudyPlan.objects.get(pk=studyplanNum)
            scheduleNum = self.get_serializer(sc).data['schedule_no']

            groupNum = Group.objects.get(pk=groupNum)
            sc = Schedule.objects.get(pk=scheduleNum)
            sc.connect_group_no = groupNum
            sc.save()

            return Response({
                'response': '成功'
            })
        else:
            return Response({
                'response': '您非此讀書計畫建立者，無法分享'
            })


    @action(detail=False, methods=['PATCH'])
    def cancel_sharing(self, request):
        uid = request.query_params.get('uid')
        studyplanNum = request.query_params.get('studyplanNum')

        st = StudyPlan.objects.filter(create_id=uid, serial_no=studyplanNum)
        if st.count() > 0:
            sc = StudyPlan.objects.get(pk=studyplanNum)
            scheduleNum = self.get_serializer(sc).data['schedule_no']

            sc = Schedule.objects.get(pk=scheduleNum)
            sc.connect_group_no = None
            sc.save()

            return Response({
                'response': '成功'
            })
        else:
            return Response({
                'response': '您非此讀書計畫建立者，無法取消分享'
            })

    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        uid = request.query_params.get('uid')
        studyplanNum = request.query_params.get('studyplanNum')

        st = StudyPlan.objects.filter(create_id=uid, serial_no=studyplanNum)
        if st.count() > 0:
            pl = PlanContent.objects.filter(pk=studyplanNum)
            pl.delete()

            st = StudyPlan.objects.get(pk=studyplanNum)
            scheduleNum = self.get_serializer(st).data['schedule_no']
            st.delete()

            sc = Schedule.objects.get(pk=scheduleNum)
            sc.delete()

            return Response({
                'response': '成功'
            })
        else:
            return Response({
                'response': '您非此讀書計畫建立者，無法刪除'
            })

    @action(detail=False)
    def get(self, request):
        uid = request.query_params.get('uid')
        studyplanNum = request.query_params.get('studyplanNum')
        st = GetStudyplan.objects.filter(create_id=uid, plan_no=studyplanNum)

        if st.count() > 0:
            return Response({
                'title': st.first().schedule_name,
                'date': st.first().field_date,
                'startTime': st.first().schedule_start,
                'endTime': st.first().schedule_end,
                'subject': [
                    {
                        'subjectName': t.subject,
                        'subjectStart': t.plan_start,
                        'subjectEnd': t.plan_end,
                        'rest': t.is_rest,
                    }
                    for t in st
                ]
            })
        else:
            return Response({
                'response': '沒有讀書計畫'
            })


    @action(detail=False)
    def personal_list(self, request):
        uid = request.query_params.get('uid')
        st = StudyplanList.objects.filter(create_id=uid)

        if st.count() > 0:
            return Response({
                'studyplan': [
                    {
                        'studyplanNum': t.studyplan_num,
                        'title': t.schedule_name,
                        'date': t.field_date,
                        'startTime': t.schedule_start,
                        'endTime': t.schedule_end,
                    }
                    for t in st
                ]
            })
        else:
            return Response({
                'response': '沒有個人讀書計畫'
            })

    @action(detail=False)
    def group_list(self, request):
        uid = request.query_params.get('uid')
        st = GroupStudyplanList.objects.filter(user_id=uid)

        if st.count() > 0:
            return Response({
                'studyplan': [
                    {
                        'studyplanNum': t.studyplan_num,
                        'title': t.schedule_name,
                        'date': t.field_date,
                        'startTime': t.schedule_start,
                        'endTime': t.schedule_end,
                    }
                    for t in st
                ]
            })
        else:
            return Response({
                'response': '沒有群組讀書計畫'
            })

    @action(detail=False)
    def one_group_list(self, request):
        uid = request.query_params.get('uid')
        groupNum = request.query_params.get('groupNum')
        st = GroupStudyplanList.objects.filter(user_id=uid,group_no=groupNum,status_id__in=[1,4])

        if st.count() > 0:
            return Response({
                'studyplan': [
                    {
                        'studyplanNum': t.studyplan_num,
                        'title': t.schedule_name,
                        'date': t.field_date,
                        'startTime': t.schedule_start,
                        'endTime': t.schedule_end,
                    }
                    for t in st
                ]
            })
        else:
            return Response({
                'response': '查無結果'
            })
