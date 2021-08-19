from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from api.response import *
from api.models import Group, StudyPlan, Schedule, PlanContent, StudyplanList, GroupStudyplanList, \
    PersonalSchedule, GroupLog, Account, GroupMember, Note
from studyplan.serializers import StudyPlanSerializer, CreateStudyPlanSerializer


# Create your views here.
class StudyPlanViewSet(ModelViewSet):
    queryset = StudyPlan.objects.filter(serial_no=0)
    serializer_class = StudyPlanSerializer

    @action(detail=False, methods=['POST'])
    def create_studyplan(self, request):
        data = request.data

        uid = data.get('uid')
        try:
            Account.objects.get(pk=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)

        serializer = CreateStudyPlanSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        subjects = serializer.validated_data.pop('subjects')
        if len(subjects) == 0:
            return err(Msg.Err.StudyPlan.at_least_one_subject, 'ST-A-001', request)

        study_plan = None
        schedule_num = data['scheduleNum']

        if not schedule_num:
            serializer.validated_data.update({'type_id': 1})
            schedule_no = serializer.save()
            study_plan = StudyPlan.objects.create(create_id=uid, schedule_no=schedule_no)
        elif isinstance(schedule_num, int):
            if not Schedule.objects.filter(serial_no=schedule_num).exists():
                return not_found(Msg.NotFound.schedule, request)
            if not PersonalSchedule.objects.filter(schedule_no=schedule_num, user_id=uid).exists():
                return no_authority('行程建立讀書計畫', request)
            if StudyPlan.objects.filter(schedule_no=schedule_num).exists():
                return err(Msg.Err.StudyPlan.already_existed, 'ST-A-002', request)

            schedule = Schedule.objects.get(pk=schedule_num)
            if schedule.type_id == 1:
                schedule.schedule_start = serializer.validated_data['schedule_start']
                schedule.schedule_end = serializer.validated_data['schedule_end']
                schedule.save()
                study_plan = StudyPlan.objects.create(create_id=uid, schedule_no=schedule)
            else:
                return err(Msg.Err.StudyPlan.not_study_plan_schedule, 'ST-A-003', request)

        all_subjects = []
        num = 0
        for subject in subjects:
            num += 1
            plan_content = PlanContent(plan_no=study_plan, plan_num=num, subject=subject['subject'],
                                       plan_start=subject['plan_start'], plan_end=subject['plan_end'],
                                       is_rest=subject['is_rest'], remark=subject['remark'])
            all_subjects.append(plan_content)
        PlanContent.objects.bulk_create(all_subjects)
        return success(request=request)

    @action(detail=False, methods=['PUT'])
    def edit_studyplan(self, request):
        data = request.data
        uid = data.get('uid')
        study_plan_num = data.get('studyplanNum')

        try:
            study_plan = StudyPlan.objects.get(pk=study_plan_num)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.study_plan, request)

        creator = study_plan.create_id
        connect_no = study_plan.schedule_no.connect_group_no
        user_in_group = GroupMember.objects.filter(group_no=connect_no, user_id=uid, status_id__in=[1, 4])

        if uid != creator and \
                (not study_plan.is_authority or not user_in_group.exists()):
            return no_authority('編輯讀書計畫', request)

        serializer = CreateStudyPlanSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        subjects = serializer.validated_data.pop('subjects')

        if len(subjects) == 0:
            return err(Msg.Err.StudyPlan.at_least_one_subject, 'ST-B-001', request)

        all_subjects = []
        num = 0
        for subject in subjects:
            num += 1
            note_no = subject['note_no']
            if note_no:
                user_note = Note.objects.filter(serial_no=note_no, create_id=uid).exists()
                group_note = Note.objects.filter(serial_no=note_no, group_no=connect_no).exists()
                if not user_note and not group_note:
                    return not_found(Msg.NotFound.note, request)
                note_no = Note.objects.get(pk=note_no)
            subject_item = PlanContent(plan_no=study_plan, plan_num=num, subject=subject['subject'],
                                       plan_start=subject['plan_start'], plan_end=subject['plan_end'],
                                       note_no=note_no, is_rest=subject['is_rest'], remark=subject['remark'])
            all_subjects.append(subject_item)

        plan_content = PlanContent.objects.filter(plan_no=study_plan)
        plan_content.delete()
        PlanContent.objects.bulk_create(all_subjects)

        if uid == creator:
            study_plan.is_authority = data['is_authority']
            study_plan.save()

        schedule = study_plan.schedule_no
        old_schedule_name = schedule.schedule_name
        schedule.schedule_name = serializer.validated_data['schedule_name']
        schedule.schedule_start = serializer.validated_data['schedule_start']
        schedule.schedule_end = serializer.validated_data['schedule_end']
        schedule.save()

        if schedule.connect_group_no:
            if old_schedule_name != schedule.schedule_name:
                GroupLog.objects.create(do_time=datetime.now(), group_no=schedule.connect_group_no, user_id=uid,
                                        trigger_type='U', do_type_id=4,
                                        old=old_schedule_name, new=schedule.schedule_name)
            else:
                GroupLog.objects.create(do_time=datetime.now(), group_no=schedule.connect_group_no, user_id=uid,
                                        trigger_type='U', do_type_id=4, new=schedule.schedule_name)
        return success(request=request)

    @action(detail=False, methods=['PATCH'])
    def sharing(self, request):
        data = request.data

        uid = data.get('uid')
        study_plan_num = data.get('studyplanNum')
        group_num = data.get('groupNum')

        user_study_plan = StudyPlan.objects.filter(create_id=uid, serial_no=study_plan_num)
        user_in_group = GroupMember.objects.filter(group_no=group_num, user_id=uid, status_id__in=[1, 4])

        if user_study_plan.exists() and user_in_group.exists():
            group_num = Group.objects.get(pk=group_num)
            study_plan = StudyPlan.objects.get(pk=study_plan_num)

            schedule = Schedule.objects.get(pk=study_plan.schedule_no.pk)
            if datetime.now() > schedule.schedule_start:
                return err(Msg.Err.StudyPlan.select_old, 'ST-C-001', request)

            if not schedule.connect_group_no:
                schedule.connect_group_no = group_num
                schedule.save()
                GroupLog.objects.create(do_time=datetime.now(), group_no=group_num, user_id=uid,
                                        trigger_type='I', do_type_id=4, new=schedule.schedule_name)
                return success(request=request)
            elif schedule.connect_group_no != group_num:
                return err(Msg.Err.StudyPlan.only_share_with_one_group, 'ST-C-002', request)
            else:
                return err(Msg.Err.StudyPlan.has_been_shared, 'ST-C-003', request)
        elif not user_in_group.exists():
            return not_found(Msg.NotFound.not_in_group, request)
        else:
            return no_authority('分享讀書計畫', request)

    @action(detail=False, methods=['PATCH'])
    def cancel_sharing(self, request):
        data = request.data

        uid = data.get('uid')
        study_plan_num = data.get('studyplanNum')

        user_study_plan = StudyPlan.objects.filter(create_id=uid, serial_no=study_plan_num)
        if user_study_plan.exists():
            study_plan = StudyPlan.objects.get(pk=study_plan_num)
            schedule = Schedule.objects.get(pk=study_plan.schedule_no.pk)

            if schedule.connect_group_no:
                plan_content = PlanContent.objects.filter(plan_no=study_plan_num, note_no__isnull=False)
                for content in plan_content:
                    if content.note_no.create_id != uid:
                        plan_content.filter(plan_num=content.plan_num).update(note_no=None)

                group_no = schedule.connect_group_no
                schedule.connect_group_no = None
                schedule.save()
                GroupLog.objects.create(do_time=datetime.now(), group_no=group_no, user_id=uid,
                                        trigger_type='D', do_type_id=4, old=schedule.schedule_name)
                return success(request=request)
            else:
                return err(Msg.Err.StudyPlan.has_been_canceled, 'ST-D-001', request)
        else:
            return no_authority('取消分享讀書計畫', request)

    @action(detail=False, methods=['DELETE'])
    def delete(self, request):
        data = request.data

        uid = data.get('uid')
        study_plan_num = data.get('studyplanNum')

        try:
            study_plan = StudyPlan.objects.get(pk=study_plan_num)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.study_plan, request)

        user_study_plan = StudyPlan.objects.filter(create_id=uid, serial_no=study_plan_num)
        if user_study_plan.exists():
            schedule = Schedule.objects.get(pk=study_plan.schedule_no.pk)

            if schedule.connect_group_no:
                return err(Msg.Err.StudyPlan.disconnect_group_first, 'ST-E-001', request)

            plan_content = PlanContent.objects.filter(pk=study_plan_num)
            plan_content.delete()

            schedule_no = study_plan.schedule_no.pk
            study_plan.delete()

            personal_schedule = PersonalSchedule.objects.filter(schedule_no=schedule_no)
            if not personal_schedule.exists():
                schedule.delete()
            return success(request=request)
        else:
            return no_authority('刪除讀書計畫', request)

    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        study_plan_num = data.get('studyplanNum')

        try:
            study_plan = StudyPlan.objects.get(pk=study_plan_num)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.study_plan, request)

        creator = study_plan.create_id
        schedule = Schedule.objects.get(pk=study_plan.schedule_no.pk)
        user_is_member = GroupMember.objects.filter(user_id=uid, group_no=schedule.connect_group_no,
                                                    status_id__in=[1, 4])
        if uid == creator or user_is_member.exists():
            plan_content = PlanContent.objects.filter(plan_no=study_plan_num)
            return success({
                'creatorId': study_plan.create.pk,
                'creator': study_plan.create.name,
                'isAuthority': bool(study_plan.is_authority),
                'title': schedule.schedule_name,
                'date': schedule.schedule_start.date(),
                'startTime': schedule.schedule_start,
                'endTime': schedule.schedule_end,
                'subject': [
                    {
                        'subjectName': p.subject,
                        'subjectStart': p.plan_start,
                        'subjectEnd': p.plan_end,
                        'remark': p.remark,
                        'noteNum': p.note_no.pk if p.note_no else None,
                        'rest': bool(p.is_rest),
                    }
                    for p in plan_content
                ]
            }, request)
        else:
            return not_found(Msg.NotFound.study_plan, request)

    @action(detail=False)
    def personal_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        study_plan = StudyplanList.objects.filter(create_id=uid)

        return success({
            'studyplan': [
                {
                    'studyplanNum': s.studyplan_num,
                    'title': s.schedule_name,
                    'date': s.schedule_start.date(),
                    'startTime': s.schedule_start,
                    'endTime': s.schedule_end,
                }
                for s in study_plan
            ]
        }, request)

    @action(detail=False)
    def personal_share_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        share_status = int(data.get('shareStatus'))
        study_plan = StudyplanList.objects.filter(create_id=uid).exclude(connect_group_no__isnull=share_status)

        return success({
            'studyplan': [
                {
                    'studyplanNum': s.studyplan_num,
                    'title': s.schedule_name,
                    'date': s.schedule_start.date(),
                    'startTime': s.schedule_start,
                    'endTime': s.schedule_end,
                }
                for s in study_plan
            ]
        }, request)

    @action(detail=False)
    def group_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        study_plan = GroupStudyplanList.objects.filter(user_id=uid, status_id__in=[1, 4])

        return success({
            'groupStudyplan': [
                {
                    'groupNum': group_no,
                    'groupName': Group.objects.get(pk=group_no).group_name,
                    'studyplanCount': study_plan.filter(group_no=group_no).count(),
                    'studyplanContent': [
                        {
                            'studyplanNum': s.studyplan_num,
                            'title': s.schedule_name,
                            'date': s.schedule_start.date(),
                            'startTime': s.schedule_start,
                            'endTime': s.schedule_end,
                        }
                        for s in study_plan.filter(group_no=group_no)
                    ]
                }
                for group_no in study_plan.values_list('group_no', flat=True).distinct()
            ]
        }, request)

    @action(detail=False)
    def one_group_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_num = data.get('groupNum')
        study_plan = GroupStudyplanList.objects.filter(user_id=uid, group_no=group_num, status_id__in=[1, 4])

        return success({
            'studyplan': [
                {
                    'studyplanNum': s.studyplan_num,
                    'creatorId': s.create_id,
                    'creator': s.creator,
                    'title': s.schedule_name,
                    'date': s.schedule_start.date(),
                    'startTime': s.schedule_start,
                    'endTime': s.schedule_end,
                }
                for s in study_plan
            ]
        }, request)

