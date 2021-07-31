# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import django
from django.db import models
from datetime import datetime


class Account(models.Model):
    user_id = models.CharField(primary_key=True, max_length=255)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.TextField(blank=True, null=True)
    theme = models.ForeignKey('Theme', models.DO_NOTHING, blank=True, null=True)
    is_public = models.IntegerField(blank=True, null=True)
    is_help = models.IntegerField(blank=True, null=True)
    is_location = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account'


class ClassTime(models.Model):
    school_no = models.ForeignKey('School', models.DO_NOTHING, db_column='school_no')
    section_no = models.ForeignKey('Section', models.DO_NOTHING, db_column='section_no')
    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        managed = False
        db_table = 'class_time'
        unique_together = (('school_no', 'section_no'),)


class DoType(models.Model):
    do_type_id = models.IntegerField(primary_key=True)
    do_type_name = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'do_type'


class Friend(models.Model):
    user = models.OneToOneField(Account, models.DO_NOTHING, primary_key=True)
    related_person = models.ForeignKey(Account, models.DO_NOTHING, db_column='related_person',
                                       related_name='related_person')
    relation = models.ForeignKey('Relation', models.DO_NOTHING)
    is_temporary_group = models.IntegerField(blank=True, null=True,default=1)
    is_public_timetable = models.IntegerField(blank=True, null=True,default=1)

    class Meta:
        managed = True
        db_table = 'friend'
        unique_together = ('user', 'related_person')

class FriendList(models.Model):
    user_id = models.CharField(max_length=255, primary_key=True)
    photo = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    related_person = models.CharField(max_length=255)
    relation_id = models.IntegerField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'friend_list'
        unique_together = ('user_id', 'related_person')

class GetFriend(models.Model):
    user_id = models.CharField(max_length=255,primary_key=True)
    related_person = models.CharField(max_length=255)
    relation_id = models.IntegerField()
    name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.TextField(blank=True, null=True)
    is_public_timetable = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'get_friend'
        unique_together = ('user_id', 'related_person')

class GroupVote(models.Model):
    user_id = models.CharField(max_length=255)
    status_id = models.IntegerField()
    group_no = models.IntegerField()
    group_name = models.CharField(max_length=255)
    is_temporary_group = models.IntegerField()
    type_id = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=255)
    vote_num = models.IntegerField(primary_key=True)
    vote_type = models.BigIntegerField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'group_vote'
        unique_together = ('user_id', 'group_no','vote_num')

class GetStudyplan(models.Model):
    create_id = models.CharField(max_length=255, blank=True, null=True)
    plan_no = models.IntegerField(primary_key=True)
    plan_num = models.IntegerField()
    schedule_name = models.CharField(max_length=255)
    field_date = models.DateField(db_column='_date', blank=True, null=True)  # Field renamed because it started with '_'.
    schedule_start = models.DateTimeField()
    schedule_end = models.DateTimeField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    plan_start = models.DateTimeField()
    plan_end = models.DateTimeField()
    is_rest = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'get_studyplan'
        unique_together = ('plan_no', 'plan_num')


class GetTemporaryInvite(models.Model):
    group_no = models.IntegerField(primary_key=True)
    group_name = models.CharField(max_length=255)
    found_time = models.DateTimeField()
    schedule_end = models.DateTimeField(blank=True, null=True)
    founder_photo = models.TextField(blank=True, null=True)
    founder_name = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    member_photo = models.TextField(blank=True, null=True)
    user_id = models.CharField(max_length=255)
    member_name = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    status_id = models.IntegerField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'get_temporary_invite'
        unique_together = ('group_no', 'user_id')

class Group(models.Model):
    serial_no = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=255)
    founder = models.ForeignKey(Account, models.DO_NOTHING, db_column='founder')
    type = models.ForeignKey('Type', models.DO_NOTHING, blank=False, null=False)
    found_time = models.DateTimeField(default=django.utils.timezone.now)
    is_temporary_group = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'group'


class GroupScheduleTime(models.Model):
    serial_no = models.IntegerField(primary_key=True)
    group_name = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    founder = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    type_id = models.IntegerField(blank=True, null=True)
    found_time = models.DateTimeField(blank=True, null=True)
    is_temporary_group = models.IntegerField(blank=True, null=True)
    end_time = models.CharField(max_length=19, db_collation='utf8mb4_0900_ai_ci', blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'group_schedule_time'

class GroupInviteList(models.Model):
    group_no = models.IntegerField(primary_key=True)
    user_id = models.CharField(max_length=255)
    group_name = models.CharField(max_length=255)
    type_id = models.IntegerField(blank=True, null=True)
    status_id = models.IntegerField()
    inviter_id = models.CharField(max_length=255)
    inviter_photo = models.TextField(blank=True, null=True)
    inviter_name = models.CharField(max_length=255, blank=True, null=True)
    is_temporary_group = models.IntegerField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'group_invite_list'
        unique_together = ('group_no', 'user_id')

class GroupList(models.Model):
    group_no = models.IntegerField()
    group_name = models.CharField(max_length=255)
    member_photo = models.TextField(blank=True, null=True)
    user_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    type_id = models.IntegerField(blank=True, null=True)
    status_id = models.IntegerField()
    founder = models.CharField(max_length=255,primary_key=True)
    founder_name = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    founder_photo = models.TextField(blank=True, null=True)
    cnt = models.BigIntegerField()
    is_temporary_group = models.IntegerField()
    member = []

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'group_list'
        unique_together = ('founder', 'user_id', 'group_no')


class GroupLog(models.Model):
    serial_no = models.AutoField(primary_key=True)
    do_time = models.DateTimeField(blank=True, null=True)
    group_no = models.ForeignKey(Group, models.DO_NOTHING, db_column='group_no', blank=True, null=True)
    user = models.ForeignKey(Account, models.DO_NOTHING, blank=True, null=True)
    trigger_type = models.CharField(max_length=1, blank=True, null=True)
    do_type = models.ForeignKey(DoType, models.DO_NOTHING, blank=True, null=True)
    old = models.CharField(max_length=255, blank=True, null=True)
    new = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'group_log'


class GroupLogDetail(models.Model):
    serial_no = models.IntegerField(primary_key=True)
    do_time = models.DateTimeField(blank=True, null=True)
    group_no = models.IntegerField(blank=True, null=True)
    user_id = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    name = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    photo = models.TextField(blank=True, null=True)
    trigger_type = models.CharField(max_length=1, db_collation='utf8_general_ci', blank=True, null=True)
    do_type_id = models.IntegerField(blank=True, null=True)
    old = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)
    content = models.CharField(max_length=255, db_collation='utf8_general_ci', blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'group_log_detail'


class GroupMember(models.Model):
    group_no = models.OneToOneField(Group, models.DO_NOTHING, db_column='group_no', primary_key=True)
    user = models.ForeignKey(Account, models.DO_NOTHING)
    join_time = models.DateTimeField(default=django.utils.timezone.now)
    status = models.ForeignKey('MemberStatus', models.DO_NOTHING)
    inviter = models.ForeignKey(Account, models.DO_NOTHING,related_name='inviter')

    class Meta:
        managed = False
        db_table = 'group_member'
        unique_together = ('group_no', 'user')


class GetGroupNoVote(models.Model):
    group_no = models.IntegerField(primary_key=True)
    user_id = models.CharField(max_length=255, db_collation='utf8_general_ci')
    status_id = models.IntegerField()
    group_name = models.CharField(max_length=255, db_collation='utf8_general_ci')
    type_id = models.IntegerField(blank=True, null=True)
    is_temporary_group = models.IntegerField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'get_group_no_vote'
        unique_together = ('group_no', 'user_id')

class GroupStudyplanList(models.Model):
    user_id = models.CharField(max_length=255,primary_key=True)
    status_id = models.IntegerField()
    group_no = models.IntegerField(blank=True, null=True)
    schedule_name = models.CharField(max_length=255)
    studyplan_num = models.IntegerField()
    field_date = models.DateField(db_column='_date', blank=True, null=True)  # Field renamed because it started with '_'.
    schedule_start = models.DateTimeField()
    schedule_end = models.DateTimeField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'group_studyplan_list'
        unique_together = ('user_id', 'group_no','studyplan_num')

class MemberStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'member_status'


class Note(models.Model):
    serial_no = models.AutoField(primary_key=True)
    create = models.ForeignKey(Account, models.DO_NOTHING)
    group_no = models.ForeignKey(Group, models.DO_NOTHING, db_column='group_no', blank=True, null=True)
    type_name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    is_personal = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'note'


class Notice(models.Model):
    user = models.OneToOneField(Account, models.DO_NOTHING, primary_key=True)
    is_schedule_notice = models.IntegerField(blank=True, null=True)
    is_temporary_group_notice = models.IntegerField(blank=True, null=True)
    is_countdown_notice = models.IntegerField(blank=True, null=True)
    is_group_notice = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notice'


class OptionType(models.Model):
    option_type_id = models.IntegerField(primary_key=True)
    option_type_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'option_type'


class PersonalSchedule(models.Model):
    serial_no = models.AutoField(primary_key=True)
    user = models.ForeignKey(Account, models.DO_NOTHING)
    schedule_no = models.ForeignKey('Schedule', models.DO_NOTHING, db_column='schedule_no')
    is_notice = models.IntegerField()
    is_countdown = models.IntegerField()
    is_hidden = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'personal_schedule'


class PersonalTimetable(models.Model):
    user = models.OneToOneField(Account, models.DO_NOTHING, primary_key=True)
    semester = models.CharField(max_length=255)
    school_no = models.ForeignKey('School', models.DO_NOTHING, db_column='school_no', blank=True, null=True)
    semester_start = models.DateField(blank=True, null=True)
    semester_end = models.DateField(blank=True, null=True)
    timetable_no = models.ForeignKey('TimetableCreate', models.DO_NOTHING, db_column='timetable_no')

    class Meta:
        managed = False
        db_table = 'personal_timetable'
        unique_together = (('user', 'semester'),)


class PlanContent(models.Model):
    plan_no = models.OneToOneField('StudyPlan', models.DO_NOTHING, db_column='plan_no', primary_key=True)
    plan_num = models.IntegerField()
    subject = models.CharField(max_length=255, blank=True, null=True)
    plan_start = models.DateTimeField()
    plan_end = models.DateTimeField()
    note_no = models.ForeignKey(Note, models.DO_NOTHING, db_column='note_no', blank=True, null=True)
    is_rest = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plan_content'
        unique_together = (('plan_no', 'plan_num'),)


class Relation(models.Model):
    relation_id = models.IntegerField(primary_key=True)
    relationship = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'relation'


class Schedule(models.Model):
    serial_no = models.AutoField(primary_key=True)
    schedule_name = models.CharField(max_length=255)
    connect_group_no = models.ForeignKey(Group, models.DO_NOTHING, db_column='connect_group_no', blank=True, null=True)
    type = models.ForeignKey('Type', models.DO_NOTHING, blank=True, null=True)
    schedule_start = models.DateTimeField()
    schedule_end = models.DateTimeField()
    place = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'schedule'


class ScheduleNotice(models.Model):
    serial_no = models.AutoField(primary_key=True)
    personal_schedule_no = models.ForeignKey(PersonalSchedule, models.DO_NOTHING, db_column='personal_schedule_no')
    notice_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'schedule_notice'


class School(models.Model):
    serial_no = models.AutoField(primary_key=True)
    school_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'school'


class Section(models.Model):
    section_no = models.IntegerField(primary_key=True)
    weekday = models.CharField(max_length=255)
    section = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'section'


class StudyPlan(models.Model):
    serial_no = models.AutoField(primary_key=True)
    create = models.ForeignKey(Account, models.DO_NOTHING, blank=True, null=True)
    schedule_no = models.ForeignKey(Schedule, models.DO_NOTHING, db_column='schedule_no', blank=True, null=True)
    is_authority = models.IntegerField(default=False, null=False)

    class Meta:
        managed = False
        db_table = 'study_plan'

class StudyplanList(models.Model):
    create_id = models.CharField(max_length=255, blank=True, null=True)
    studyplan_num = models.IntegerField(primary_key=True)
    schedule_name = models.CharField(max_length=255)
    field_date = models.DateField(db_column='_date', blank=True, null=True)  # Field renamed because it started with '_'.
    schedule_start = models.DateTimeField()
    schedule_end = models.DateTimeField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'studyplan_list'


class Subject(models.Model):
    serial_no = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'subject'

class TemporaryList(models.Model):
    group_no = models.IntegerField(primary_key=True)
    founder_name = models.CharField(max_length=255, blank=True, null=True)
    founder = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    status_id = models.IntegerField()
    type_id = models.IntegerField(blank=True, null=True)
    group_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    cnt = models.BigIntegerField()
    is_temporary_group = models.IntegerField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'temporary_list'
        unique_together = (('group_no', 'user_id'),)


class Theme(models.Model):
    theme_id = models.IntegerField(primary_key=True)
    color = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'theme'


class Timetable(models.Model):
    timetalbe_no = models.ForeignKey('TimetableCreate', models.DO_NOTHING, db_column='timetalbe_no')
    section_no = models.ForeignKey(Section, models.DO_NOTHING, db_column='section_no')
    subject_no = models.ForeignKey(Subject, models.DO_NOTHING, db_column='subject_no')

    class Meta:
        managed = False
        db_table = 'timetable'
        unique_together = (('timetalbe_no', 'section_no'),)


class Type(models.Model):
    type_id = models.IntegerField(primary_key=True)
    type_name = models.CharField(max_length=255)
    color = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'type'


class VerificationCode(models.Model):
    user = models.OneToOneField(Account, models.DO_NOTHING, primary_key=True)
    ver_code = models.CharField(max_length=255)
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'verification_code'
        unique_together = (('user', 'ver_code'),)


class Vote(models.Model):
    serial_no = models.AutoField(primary_key=True)
    group_no = models.ForeignKey(Group, models.DO_NOTHING, db_column='group_no')
    option_type = models.ForeignKey(OptionType, models.DO_NOTHING)
    founder = models.ForeignKey(Account, models.DO_NOTHING, db_column='founder')
    title = models.CharField(max_length=255)
    found_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    is_anonymous = models.IntegerField(blank=True, null=True)
    is_add_option = models.IntegerField(blank=True, null=True)
    multiple_choice = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vote'


class VoteDateOption(models.Model):
    vote_no = models.OneToOneField(Vote, models.DO_NOTHING, db_column='vote_no', primary_key=True)
    option_num = models.IntegerField()
    content = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vote_date_option'
        unique_together = (('vote_no', 'option_num'),)


class VoteOption(models.Model):
    vote_no = models.OneToOneField(Vote, models.DO_NOTHING, db_column='vote_no', primary_key=True)
    option_num = models.IntegerField()
    content = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vote_option'
        unique_together = (('vote_no', 'option_num'),)


class VoteRecord(models.Model):
    serial_no = models.AutoField(primary_key=True)
    vote_no = models.ForeignKey(Vote, models.DO_NOTHING, db_column='vote_no')
    option_num = models.IntegerField()
    user = models.ForeignKey(Account, models.DO_NOTHING)
    vote_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vote_record'


class TimetableCreate(models.Model):
    serial_no = models.AutoField(primary_key=True)
    create = models.ForeignKey(Account, models.DO_NOTHING)
    create_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'timetable_create'

