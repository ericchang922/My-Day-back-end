import string
import random

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import ObjectDoesNotExist
from datetime import datetime

from api.models import PersonalTimetable, Timetable, School, Subject, Section, ClassTime, TimetableCreate, ShareLog, \
    Account, ShareType, Sharecode
from api.response import *
from timetable.serializers import TimetableSerializer

week_name = {
    '星期一': 100,
    '星期二': 200,
    '星期三': 300,
    '星期四': 400,
    '星期五': 500,
    '星期六': 600,
    '星期日': 700
}


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
        end_date = data.get('endDate')

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
                                             semester_start=start_date, semester_end=end_date, timetable_no=timetable)
        except:
            return err(Msg.Err.Timetable.personal_create, 'TI-A-003', request)

        for i in subject:
            subject_name = i.get('subjectName')
            start_time = i.get('startTime')
            end_time = i.get('endTime')
            section = i.get('section')
            week = i.get('week')
            try:
                section_db = Section.objects.get(weekday=week, section=section)
            except ObjectDoesNotExist:
                section_no = week_name[week] + section
                section_db = Section.objects.create(section_no=section_no, weekday=week, section=section)
            except:
                return err(Msg.Err.Timetable.section_create, 'TI-A-004', request)
            try:
                subject_db = Subject.objects.get(subject_name=subject_name)
            except ObjectDoesNotExist:
                subject_db = Subject.objects.create(subject_name=subject_name)
            except:
                return err(Msg.Err.Timetable.subject_create, 'TI-A-005', request)
            try:
                Timetable.objects.create(timetable_no_id=timetable.serial_no, section_no=section_db,
                                         subject_no=subject_db)
            except:
                return err(Msg.Err.Timetable.create, 'TI-A-006', request)
            try:
                ClassTime.objects.create(school_no=school, section_no=section_db, start=start_time, end=end_time)
            except:
                return err(Msg.Err.Timetable.create, 'TI-A-007', request)

        return success(request=request)

    @action(detail=False, methods=['POST'])
    def edit_timetable(self, request):
        data = request.data

        uid = data['uid']
        school_year = data['schoolYear']
        semester = data['semester']
        f_semester = f'{school_year}-{semester}'
        subject = data['subject']

        try:
            p_timetable = PersonalTimetable.objects.filter(user_id=uid, semester=f_semester)
        except:
            return err(Msg.Err.Timetable.get_timetable, 'TI-B-001', request)
        timetable_no = p_timetable[0].timetable_no.serial_no
        school_no = p_timetable[0].school_no

        try:
            timetable = Timetable.objects.filter(timetable_no=timetable_no)
        except:
            return err()

        timetable_list = []
        for t in timetable:
            timetable_list.append(int(t.section_no.section_no))

        edit_list = []

        for i in subject:
            subject_name = i.get('subjectName')
            start_time = i.get('startTime')
            end_time = i.get('endTime')
            section = i.get('section')
            week = i.get('week')
            section_no = week_name[week] + section

            if week and section is not None:
                try:
                    section_db = Section.objects.get(weekday=week, section=section)
                except ObjectDoesNotExist:
                    section_db = Section.objects.create(section_no=section_no, weekday=week, section=section)
                except:
                    return err(Msg.Err.Timetable.section_create, 'TI-B-002', request)

            if subject_name is not None:
                try:
                    subject_db = Subject.objects.get(subject_name=subject_name)
                except ObjectDoesNotExist:
                    subject_db = Subject.objects.create(subject_name=subject_name)
                except:
                    return err(Msg.Err.Timetable.subject_create, 'TI-B-003', request)

                if section_no in timetable_list:
                    # try:
                    timetable_update = Timetable.objects.filter(timetable_no_id=timetable_no, section_no=section_db)
                    timetable_update.update(subject_no=subject_db)
                    # except:
                    #     return err(Msg.Err.Timetable.update, 'TI-B-004', request)
                else:
                    try:
                        Timetable.objects.create(timetable_no_id=timetable_no, section_no=section_db,
                                                 subject_no=subject_db)
                    except:
                        return err(Msg.Err.Timetable.create, 'TI-B-005', request)

                # try:
                get_classtime = ClassTime.objects.filter(school_no=school_no, section_no=section_db)

                if start_time is not None:
                    get_classtime.update(start=start_time)
                if end_time is not None:
                    get_classtime.update(end=end_time)
                # except:
                # return err(Msg.Err.Timetable.section_update, 'TI-B-006', request)

                if get_classtime.count() <= 0:
                    ClassTime.objects.create(school_no=school_no, section_no=section_db, start=start_time, end=end_time)
                edit_list.append(section_no)

        for t in timetable_list:
            if t not in edit_list:
                Timetable.objects.get(timetable_no=timetable_no, section_no=t).delete()

        return success()

    @action(detail=False, methods=['POST'])
    def delete_timetable(self, request):
        data = request.data

        uid = data.get('uid')
        school_year = data.get('schoolYear')
        semester = data.get('semester')
        f_semester = f'{school_year}-{semester}'

        try:
            p_timetable = PersonalTimetable.objects.filter(user_id=uid, semester=f_semester)
        except:
            return err(Msg.Err.Timetable.get_timetable, 'TI-C-001', request)

        try:
            p_school = School.objects.get(serial_no=p_timetable[0].school_no.serial_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.school, request)
        except:
            return err(Msg.Err.Timetable.get_school, 'TI-C-002', request)

        try:
            p_class = ClassTime.objects.filter(school_no=p_school)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.class_time, request)
        except:
            return err(Msg.Err.Timetable.get_classtime, 'TI-C-002', request)

        try:
            timetable = Timetable.objects.filter(timetalbe_no=p_timetable[0].timetable_no.serial_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.timetable, request)
        except:
            return err(Msg.Err.get_time, 'TI-C-004', request)

        try:
            create = TimetableCreate.objects.get(serial_no=p_timetable[0].timetable_no.serial_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.timetable, request)
        except:
            return err(Msg.Err.get_timetable, 'TI-C-005', request)

        p_timetable.delete()
        p_class.delete()
        p_school.delete()
        timetable.delete()
        create.delete()

        return success()
