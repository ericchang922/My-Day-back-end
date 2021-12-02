# python
from datetime import datetime
# django
from django.db.models import ObjectDoesNotExist
from django.db.utils import IntegrityError
# rest
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
# my day
from note.serializer import NoteSerializer
from api.models import Note, GroupMember, GroupLog
# note
from api.response import *


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.filter(serial_no=0)
    serializer_class = NoteSerializer

    # /note/create_new/  ----------------------------------------------------------------------------------------------A
    @action(detail=False, methods=['POST'])
    def create_new(self, request):
        data = request.data

        uid = data['uid']
        type_name = data['typeName']
        title = data['title']
        content = data['content']

        try:
            Note.objects.create(create_id=uid, type_name=type_name, title=title, content=content, is_personal=True)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.create, 'NO-A-001', request, request)  # --------------------------------------001

        return success(request=request)

    # /note/edit/  ----------------------------------------------------------------------------------------------------B
    @action(detail=False, methods=['POST'])
    def edit(self, request):
        data = request.data

        uid = data['uid']
        note_no = data['noteNum']
        type_name = data['typeName']
        title = data['title']
        content = data['content']
        old = None

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-B-001', request)  # --------------------------------------001

        group_no = note.group_no.serial_no
        if note.create_id != uid:
            try:
                GroupMember.objects.get(user=uid, group_no=group_no)
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_note, request)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'NO-B-002', request)  # -------------------------------------002
            return no_authority('編輯筆記', request)

        if note.type_name != type_name and type_name is not None:
            note.type_name = type_name
        if note.title != title and title is not None:
            old = note.title
            note.title = title
        if note.content != content and content is not None:
            note.content = content

        if group_no is not None:
            try:
                group_log = GroupLog.objects.create(do_time=datetime.now(), group_no_id=group_no, user_id=uid,
                                                    trigger_type='U', do_type_id=7, new=title)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.log_create, 'NO-B-003', request)  # --------------------------------------003
            if old is not None:
                print(old)
                group_log.old = old
                group_log.save()
        note.save()
        return success(request=request)

    # /note/delete/  --------------------------------------------------------------------------------------------------C
    @action(detail=False, methods=['POST'])
    def delete(self, request):
        data = request.data

        uid = data['uid']
        note_no = data['noteNum']

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-C-001', request)  # -----------------------------------------------001

        group_no = note.group_no.serial_no
        title = note.title
        if group_no is None:
            return note_is_connect(request=request)
        if note.create_id != uid:
            try:
                GroupMember.objects.get(user=uid, group_no=group_no)
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_note, request)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'NO-C-002', request)  # -------------------------------------002
            return no_authority('刪除筆記', request)

        try:
            note.delete()
        except IntegrityError:
            return note_is_connect(request=request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.delete, 'NO-C-003', request)  # -----------------------------------------------003
        return success(request=request)

    # /note/get/  -----------------------------------------------------------------------------------------------------D
    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data['uid']
        note_no = data['noteNum']

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-D-001', request)  # -----------------------------------------------001

        if note.create_id != uid:
            try:
                GroupMember.objects.filter(user=uid, group_no=note.group_no, status__in=[1, 4])
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_note, request)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'NO-D-002', request)  # -------------------------------------002

        response = {
            'title': note.title,
            'typeName': note.type_name,
            'content': note.content
        }
        return success(response, request)

    # /note/get_list/  ------------------------------------------------------------------------------------------------E
    @action(detail=False)
    def get_list(self, request):
        data = request.query_params

        uid = data['uid']

        try:
            note = Note.objects.filter(create_id=uid)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-E-001', request)  # -----------------------------------------------001

        note_list = []
        for i in note:
            note_list.append(
                {
                    'noteNum': i.serial_no,
                    'typeName': i.type_name,
                    'title': i.title
                }
            )
        response = {'note': note_list}
        return success(response, request)

    # /note/get_group_list/  ------------------------------------------------------------------------------------------F
    @action(detail=False)
    def get_group_list(self, request):
        data = request.query_params

        uid = data['uid']
        group_no = data['groupNum']

        try:
            GroupMember.objects.filter(user_id=uid, group_no=group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'NO-F-001', request)  # -----------------------------------------001

        try:
            note = Note.objects.filter(group_no=group_no)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-F-002', request)  # -----------------------------------------------002

        note_list = []
        for i in note:
            note_list.append(
                {
                    'noteNum': i.serial_no,
                    'typeName': i.type_name,
                    'title': i.title,
                    'createId': i.create_id
                }
            )
        response = {'note': note_list}
        return success(response, request)

    # /note/share/  ---------------------------------------------------------------------------------------------------G
    @action(detail=False, methods=['POST'])
    def share(self, request):
        data = request.data

        uid = data['uid']
        group_no = data['groupNum']
        note_no = data['noteNum']

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-G-001', request)  # -----------------------------------------------001

        if note.create_id != uid:
            return not_found(Msg.NotFound.user_note, request)

        try:
            GroupMember.objects.get(user=uid, group_no=group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'NO-G-002', request)  # -----------------------------------------002

        if note.group_no is not None:
            return not_found(Msg.NotFound.note_is_share, request)
        note.group_no_id = group_no
        note.save()

        try:
            GroupLog.objects.create(do_time=datetime.now(), group_no_id=group_no, user_id=uid, trigger_type='I',
                                    do_type_id=7, new=str(note.title))
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.log_create, 'NO-G-003', request)  # ------------------------------------------003

        return success(request=request)

    # /note/cancel_share/  --------------------------------------------------------------------------------------------H
    @action(detail=False, methods=['POST'])
    def cancel_share(self, request):
        data = request.data

        uid = data['uid']
        note_no = data['noteNum']

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-H-001', request)  # -----------------------------------------------001
        try:
            group_no = note.group_no.serial_no
        except AttributeError:
            return not_found(Msg.NotFound.note_not_share, request)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-H-002', request)  # -----------------------------------------------002

        if note.create_id != uid:
            try:
                GroupMember.objects.get(user=uid, group_no=group_no, status__in=[1, 4])
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_note, request)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'NO-H-003', request)  # -------------------------------------003
            return no_authority('筆記', request)

        note.group_no = None
        note.save()

        try:
            GroupLog.objects.create(do_time=datetime.now(), group_no_id=group_no, user_id=uid, trigger_type='D',
                                    do_type_id=7,
                                    old=str(note.title))
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.log_create, 'NO-H-004', request)  # ------------------------------------------004
        return success(request=request)

    # /note/not_share_list/  ------------------------------------------------------------------------------------------I
    @action(detail=False)
    def not_share_list(self, request):
        data = request.query_params

        uid = data['uid']

        try:
            note = Note.objects.filter(create_id=uid)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-I-001', request)  # -----------------------------------------------001

        note_list = []
        for i in note:
            if i.group_no is None:
                note_list.append(
                    {
                        'noteNum': i.serial_no,
                        'typeName': i.type_name,
                        'title': i.title
                    }
                )
        response = {'note': note_list}
        return success(response, request)
