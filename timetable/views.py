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

            try:
                sharecode = Sharecode.objects.get(user_id=uid, timetable_no=timetable)
                code = sharecode.code
            except ObjectDoesNotExist:
                def create_random():
                    rand = ''
                    for i in range(8):
                        rand += str(random.choice(string.ascii_letters + string.digits))
                    return rand

                is_not_created = True
                while is_not_created:
                    code = create_random()
                    try:
                        Sharecode.objects.get(code=code)
                    except ObjectDoesNotExist:
                        Sharecode.objects.create(code=code, user_id=uid, timetable_no=timetable)
                        is_not_created = False

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

        uid = data['uid']
        school_year = data['schoolYear']
        semester = data['semester']
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
            timetable = Timetable.objects.filter(timetable_no=p_timetable[0].timetable_no.serial_no)
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

        try:
            share = Sharecode.objects.get(timetable_no=p_timetable[0].timetable_no.serial_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.timetable, request)
        except:
            return err(Msg.Err.get_timetable, 'TI-C-005', request)

        share.delete()
        p_timetable.delete()
        p_class.delete()
        p_school.delete()
        timetable.delete()
        create.delete()

        return success()

    @action(detail=False)
    def get_timetable_list(self, request):
        data = request.query_params

        uid = data['uid']

        try:
            p_timetable = PersonalTimetable.objects.filter(user_id=uid).all()
        except:
            return err(Msg.Err.Timetable.get_timetable, 'TI-D-001', request)

        p_timetable_list = []
        try:
            for i in p_timetable:
                p_timetable_list.append(
                    {
                        'schoolYear': i.semester[:3],
                        'semester': i.semester[4:],
                        'timetableNo': i.timetable_no.serial_no
                    }
                )
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.timetable, request)
        except:
            return err(Msg.Err.Timetable.get_timetable_list, 'TI-D-002', request)

        response = {'timetable': p_timetable_list}
        return success(response, request)

    @action(detail=False)
    def get_timetable(self, request):
        data = request.query_params

        uid = data['uid']
        school_year = data['schoolYear']
        semester = data['semester']
        f_semester = f'{school_year}-{semester}'
        subject = []

        try:
            p_timetable = PersonalTimetable.objects.get(user_id=uid, semester=f_semester)
        except:
            return err(Msg.Err.Timetable.get_timetable, 'TI-E-001', request)

        classtime = ClassTime.objects.filter(school_no=p_timetable.school_no.serial_no)

        for i in classtime:
            timetable = Timetable.objects.get(timetable_no=p_timetable.timetable_no, section_no=i.section_no.section_no)
            subject.append(
                {
                    'subjectName': timetable.subject_no.subject_name,
                    'startTime': i.start,
                    'endTime': i.end,
                    'week': timetable.section_no.weekday,
                    'section': timetable.section_no.section
                }
            )
        response = {
            'school': p_timetable.school_no.school_name,
            'schoolYear': p_timetable.semester[:3],
            'semester': p_timetable.semester[4:],
            'startDate': p_timetable.semester_start,
            'endDate': p_timetable.semester_end,
            'subject': subject
        }
        response = {'timetable': response}
        return success(response, request)

    @action(detail=False)
    def main_timetable_list(self, request):
        data = request.query_params

        uid = data['uid']
        p_timetable_list = []
        try:
            p_timetable = PersonalTimetable.objects.filter(user_id=uid)
        except:
            return err(Msg.Err.Timetable.get_timetable, 'TI-F-001', request)

        for i in p_timetable:
            one_classtime = ClassTime.objects.filter(school_no=i.school_no.serial_no)
            subject = []
            for t in one_classtime:
                timetable = Timetable.objects.get(timetable_no=i.timetable_no, section_no=t.section_no.section_no)
                subject.append(
                    {
                        'subjectName': timetable.subject_no.subject_name,
                        'startTime': t.start,
                        'endTime': t.end,
                        'week': timetable.section_no.weekday,
                        'section': timetable.section_no.section
                    }

                )
            p_timetable_list.append(
                {
                    'schoolYear': i.semester[:3],
                    'semester': i.semester[4:],
                    'startDate': i.semester_start,
                    'endDate': i.semester_end,
                    'subject': subject
                }
            )
        response = {'timetable': p_timetable_list}
        return success(response, request)

    @action(detail=False, methods=['POST'])
    def edit_timetable_information(self, request):
        data = request.data

        uid = data['uid']
        timetable_no = data['timetableNo']
        school = data['school']
        school_year = data['schoolYear']
        semester = data['semester']
        f_semester = f'{school_year}-{semester}'
        start_date = data['startDate']
        end_date = data['endDate']

        try:
            p_timetable = PersonalTimetable.objects.filter(user_id=uid, timetable_no_id=timetable_no)
        except:
            return err(Msg.Err.Timetable.get_timetable, 'TI-G-001', request)

        get_school = School.objects.filter(serial_no=p_timetable[0].school_no.serial_no)

        if school is not None:
            get_school.update(school_name=school)
        if start_date is not None:
            p_timetable.update(semester_start=start_date)
        if end_date is not None:
            p_timetable.update(semester_end=end_date)
        if school_year and semester is not None:
            p_timetable.update(semester=f_semester)

        return success()

    @action(detail=False, methods=['POST'])
    def share_timetable(self, request):
        share = request.data['share']

        try:
            for i in share:
                uid = i.get('uid')
                timetable_no = i.get('timetableNo')
                share_type_id = i.get('shareTypeId')
                to_id = i.get('toId')
                school_year = i.get('schoolYear')
                semester = i.get('semester')
                f_semester = f'{school_year}-{semester}'

                share_to = Account.objects.get(user_id=to_id)
                timetable_serial = TimetableCreate.objects.get(serial_no=timetable_no)
                share_type = ShareType.objects.get(share_type_id=share_type_id)

                ShareLog.objects.create(do_time=datetime.now(), user_id=uid, share_to=share_to,
                                        timetable_no=timetable_serial, semester=f_semester, share_type_id=share_type)
        except:
            return err(Msg.Err.Timetable.share, 'TI-H-001', request)

        return success()

    @action(detail=False, methods=['POST'])
    def delete_accept_timetable(self, request):
        data = request.data

        uid = data['uid']
        timetable_no = data['timetableNo']

        try:
            get_share = ShareLog.objects.get(user_id=uid, timetable_no=timetable_no)
        except:
            return err(Msg.Err.Timetable.delete_share, 'TI-I-001', request)

        get_share.delete()

        return success()

    @action(detail=False, methods=['POST'])
    def accept_timetable(self, request):
        data = request.data

        uid = data['uid']
        timetable_no = data['timetableNo']

        share = ShareLog.objects.get(share_to=uid, timetable_no=timetable_no)

        timetable = TimetableCreate.objects.create(create_id=uid, create_time=datetime.now())

        old_personal_timetable = PersonalTimetable.objects.get(user_id=share.user, timetable_no=timetable_no)

        school = School.objects.create(school_name=old_personal_timetable.school_no.school_name)

        PersonalTimetable.objects.create(user_id=uid, semester=old_personal_timetable.semester, school_no=school,
                                         semester_start=old_personal_timetable.semester_start,
                                         semester_end=old_personal_timetable.semester_end,
                                         timetable_no=timetable)

        subject = []

        old_classtime = ClassTime.objects.filter(school_no=old_personal_timetable.school_no.serial_no)
        for i in old_classtime:
            old_timetable = Timetable.objects.get(timetable_no=old_personal_timetable.timetable_no,
                                                  section_no=i.section_no.section_no)
            subject.append(
                {
                    'subjectName': old_timetable.subject_no.subject_name,
                    'startTime': i.start,
                    'endTime': i.end,
                    'week': old_timetable.section_no.weekday,
                    'section': old_timetable.section_no.section
                }
            )

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
                return err(Msg.Err.Timetable.section_create, 'TI-J-004', request)
            try:
                subject_db = Subject.objects.get(subject_name=subject_name)
            except ObjectDoesNotExist:
                subject_db = Subject.objects.create(subject_name=subject_name)
            except:
                return err(Msg.Err.Timetable.subject_create, 'TI-J-005', request)
            try:
                Timetable.objects.create(timetable_no_id=timetable.serial_no, section_no=section_db,
                                         subject_no=subject_db)
            except:
                return err(Msg.Err.Timetable.create, 'TI-J-006', request)
            try:
                ClassTime.objects.create(school_no=school, section_no=section_db, start=start_time, end=end_time)
            except:
                return err(Msg.Err.Timetable.create, 'TI-J-007', request)

        ShareLog.objects.get(share_to=uid, timetable_no=timetable_no).delete()
        return success(request=request)

    @action(detail=False)
    def get_sharecode(self, request):
        data = request.query_params

        uid = data['uid']
        timetable_no = data['timetableNo']

        try:
            code = Sharecode.objects.get(user_id=uid, timetable_no=timetable_no)
        except:
            return err(Msg.Err.Timetable.get_sharecode, 'TI-K-001', request)

        response = {'sharecode': code.code}
        return success(response, request)

    @action(detail=False, methods=['POST'])
    def sharecode_accept_timetable(self, request):
        data = request.data

        uid = data['uid']
        share_code = data['shareCode']

        try:
            sharecode = Sharecode.objects.get(code=share_code)
        except:
            return err(Msg.Err.Timetable.get_sharecode, 'TI-L-001', request)

        timetable = TimetableCreate.objects.create(create_id=uid, create_time=datetime.now())

        old_personal_timetable = PersonalTimetable.objects.get(user_id=sharecode.user,
                                                               timetable_no=sharecode.timetable_no)

        school = School.objects.create(school_name=old_personal_timetable.school_no.school_name)

        PersonalTimetable.objects.create(user_id=uid, semester=old_personal_timetable.semester, school_no=school,
                                         semester_start=old_personal_timetable.semester_start,
                                         semester_end=old_personal_timetable.semester_end,
                                         timetable_no=timetable)

        subject = []

        old_classtime = ClassTime.objects.filter(school_no=old_personal_timetable.school_no.serial_no)
        for i in old_classtime:
            old_timetable = Timetable.objects.get(timetable_no=old_personal_timetable.timetable_no,
                                                  section_no=i.section_no.section_no)
            subject.append(
                {
                    'subjectName': old_timetable.subject_no.subject_name,
                    'startTime': i.start,
                    'endTime': i.end,
                    'week': old_timetable.section_no.weekday,
                    'section': old_timetable.section_no.section
                }
            )

        print(subject)
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
                return err(Msg.Err.Timetable.section_create, 'TI-L-002', request)
            try:
                subject_db = Subject.objects.get(subject_name=subject_name)
            except ObjectDoesNotExist:
                subject_db = Subject.objects.create(subject_name=subject_name)
            except:
                return err(Msg.Err.Timetable.subject_create, 'TI-L-003', request)
            try:
                Timetable.objects.create(timetable_no_id=timetable.serial_no, section_no=section_db,
                                         subject_no=subject_db)
            except:
                return err(Msg.Err.Timetable.create, 'TI-L-004', request)
            try:
                ClassTime.objects.create(school_no=school, section_no=section_db, start=start_time, end=end_time)
            except:
                return err(Msg.Err.Timetable.create, 'TI-L-005', request)

        return success(request=request)

    @action(detail=False)
    def get_section_time(self, request):
        data = request.query_params

        uid = data['uid']
        p_timetable_list = []
        try:
            p_timetable = PersonalTimetable.objects.filter(user_id=uid)
        except:
            return err(Msg.Err.Timetable.get_timetable, 'TI-M-001', request)

        for i in p_timetable:
            one_classtime = ClassTime.objects.filter(school_no=i.school_no.serial_no)
            subject = []
            for t in one_classtime:
                timetable = Timetable.objects.get(timetable_no=i.timetable_no, section_no=t.section_no.section_no)
                subject.append(
                    {
                        'startTime': t.start,
                        'endTime': t.end,
                    }

                )
            p_timetable_list.append(
                {
                    'semester': i.semester,
                    'startDate': i.semester_start,
                    'endDate': i.semester_end,
                    'subject': subject
                }
            )
        response = {'timetable': p_timetable_list}
        return success(response, request)

    @action(detail=False)
    def get_accept_timetable_list(self, request):
        data = request.data

        uid = data['uid']
        school_year = data['schoolYear']
        semester = data['semester']
        f_semester = f'{school_year}-{semester}'

        try:
            share = ShareLog.objects.filter(share_to=uid, semester=f_semester)
        except:
            return err(Msg.Err.Timetable.get_share, 'TI-N-001', request)

        for i in share:
            subject = []
            subject.append(
                {
                    'friendName': i.user.name,
                    'timetableNo': i.timetable_no.serial_no,
                    'photo': i.user.photo
                }
            )

        response = {'accept_timetable_list': subject}
        return success(response, request)

    @action(detail=False)
    def get_accept_list(self, request):
        data = request.query_params

        uid = data['uid']

        try:
            share = ShareLog.objects.filter(share_to=uid)
        except:
            return err(Msg.Err.Timetable.get_share, 'TI-O-001', request)

        for i in share:
            subject = []
            subject.append(
                {
                    'timetableNo': i.timetable_no.serial_no,
                    'semester': i.semester
                }
            )

        response = {'accept_list': subject}
        return success(response, request)
