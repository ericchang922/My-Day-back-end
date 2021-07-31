from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import ObjectDoesNotExist
from datetime import datetime

from api.models import PersonalTimetable, Timetable, School, Subject, Section, ClassTime, TimetableCreate
from api.response import *
from timetable.serializers import TimetableSerializer


# Create your views here.
class TimetableViewSet(ModelViewSet):
    queryset = PersonalTimetable.objects.all()
    serializer_class = TimetableSerializer

    @action(detail=False, methods=['POST'])
    def create_timetable(self, request):
        data = request.data

        uid = data.get('uid')
        school = data.get('school')
        school_year = data.get('schoolYear')
        semester = data.get('semester')
        start_date = data.get('startDate')
        endDate = data.get('endDate')

        subject = request.data['subject']

        try:
            timetable = TimetableCreate.objects.create(create_id=uid, create_time=datetime.now())
        except:
            return err(Msg.Err.Timetable.create_create, 'TI-A-001', request)
        try:
            school = School.objects.create(school_name=school)
        except:
            return err(Msg.Err.Timetable.school_create, 'TI-A-002', request)
        try:
            PersonalTimetable.objects.create(user_id=uid, semester=f'{school_year}-{semester}', school_no=school,
                                             semester_start=start_date, semester_end=endDate, timetable_no=timetable)
        except:
            return err(Msg.Err.Timetable.personal_create, 'TI-A-003', request)

        for i in subject:
            subject_name = i.get('subjectName')
            start_time = i.get('startTime')
            end_time = i.get('endTime')
            section = i.get('section')
            week = i.get('week')
            week_name = {
                '星期一': 100,
                '星期二': 200,
                '星期三': 300,
                '星期四': 400,
                '星期五': 500,
                '星期六': 600,
                '星期日': 700
            }
            try:
                section = Section.objects.get(weekday=i.get('week'), section=i.get('section'))
            except ObjectDoesNotExist:
                section_no = week_name[week] + section
                section = Section.objects.create(section_no=section_no, weekday=i.get('week'), section=i.get('section'))
            except:
                return err(Msg.Err.Timetable.section_create, 'TI-A-004', request)
            try:
                subject = Subject.objects.get(subject_name=i.get('subjectName'))
            except ObjectDoesNotExist:
                subject = Subject.objects.create(subject_name=i.get('subjectName'))
            except:
                return err(Msg.Err.Timetable.subject_create, 'TI-A-005', request)
            try:
                Timetable.objects.create(timetalbe_no=timetable, section_no=section, subject_no=subject)
            except:
                return err(Msg.Err.Timetable.create, 'TI-A-006', request)
            try:
                ClassTime.objects.create(school_no=school, section_no=section, start=i.get('startTime'),
                                         end=i.get('endTime'))
            except:
                return err(Msg.Err.Timetable.create, 'TI-A-007', request)

        return success(request=request)
