# django
from django.db.models import ObjectDoesNotExist
from django.db.utils import IntegrityError
# rest
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
# my day
from note.serializer import NoteSerializer
from api.models import Note, GroupMember, Group
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
            return err(Msg.Err.Note.create, 'NO-A-001')  # --------------------------------------------------------001

        return success()

    # /note/edit/  ----------------------------------------------------------------------------------------------------B
    @action(detail=False, methods=['POST'])
    def edit(self, request):
        data = request.data

        uid = data['uid']
        note_no = data['noteNum']
        type_name = data['typeName']
        title = data['title']
        content = data['content']

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-B-001')  # --------------------------------------------------------001

        if note.create_id != uid:
            try:
                GroupMember.objects.get(user=uid, group_no=note.group_no)
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_note)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'NO-B-002')  # ----------------------------------------------002
            return no_authority('編輯筆記')

        if note.type_name != type_name and type_name is not None:
            note.type_name = type_name
        if note.title != title and title is not None:
            note.title = title
        if note.content != content and content is not None:
            note.content = content

        note.save()
        return success()

    # /note/delete/  --------------------------------------------------------------------------------------------------C
    @action(detail=False, methods=['POST'])
    def delete(self, request):
        data = request.data

        uid = data['uid']
        note_no = data['noteNum']

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-C-001')  # --------------------------------------------------------001

        if note.create_id != uid:
            try:
                GroupMember.objects.get(user=uid, group_no=note.group_no)
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_note)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'NO-C-002')  # ----------------------------------------------002
            return no_authority('刪除筆記')
        else:
            try:
                note.delete()
            except IntegrityError:
                return note_is_connect()
            except Exception as e:
                print(e)
                return err(Msg.Err.Note.delete, 'NO-C-003')  # ----------------------------------------------------003
            return success()

    # /note/get/  -----------------------------------------------------------------------------------------------------D
    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data['uid']
        note_no = data['noteNum']

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-D-001')  # --------------------------------------------------------001

        if note.create_id != uid:
            try:
                GroupMember.objects.filter(user=uid, group_no=note.group_no, status__in=[1, 4])
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_note)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read, 'NO-D-002')  # ----------------------------------------------002

        response = {
            'title': note.title,
            'content': note.content
        }
        return success(response)

    # /note/get_list/  ------------------------------------------------------------------------------------------------E
    @action(detail=False)
    def get_list(self, request):
        data = request.query_params

        uid = data['uid']

        try:
            note = Note.objects.filter(create_id=uid)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-E-001')  # --------------------------------------------------------001

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
        return success(response)

    # /note/get_group_list/  ------------------------------------------------------------------------------------------F
    @action(detail=False)
    def get_group_list(self, request):
        data = request.query_params

        uid = data['uid']
        group_no = data['groupNum']

        try:
            GroupMember.objects.filter(user_id=uid, group_no=group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'NO-F-001')  # --------------------------------------------------001

        try:
            note = Note.objects.filter(group_no=group_no)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-F-002')  # --------------------------------------------------------002

        note_list = []
        for i in note:
            note_list.append(
                {
                    'noteNum': i.serial_no,
                    'typeNum': i.type_name,
                    'title': i.title
                }
            )
        response = {'note': note_list}
        return success(response)

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
            return not_found(Msg.NotFound.note)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'NO-G-001')  # --------------------------------------------------------001

        if note.create_id != uid:
            return not_found(Msg.NotFound.user_note)

        try:
            GroupMember.objects.get(user=uid, group_no=group_no, status__in=[1, 4])
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.not_in_group)
        except Exception as e:
            print(e)
            return err(Msg.Err.Group.member_read, 'NO-G-002')  # --------------------------------------------------002

        note.group_no_id = group_no
        note.save()
        return success()

    # /note/cancel_share/  --------------------------------------------------------------------------------------------H
    @action(detail=False, methods=['POST'])
    def cancel_share(self, request):
        data = request.data

        uid = data['uid']
        note_no = data['noteNum']

        try:
            note = Note.objects.get(serial_no=note_no)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.note)
        except Exception as e:
            print(e)
            return err(Msg.Err.Note.select, 'No-H-001')  # --------------------------------------------------------001

        if note.create_id != uid:
            try:
                GroupMember.objects.get(user=uid, group_no=note.group_no, status__in=[1, 4])
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.user_note)
            except Exception as e:
                print(e)
                return err(Msg.Err.Group.member_read)
            return no_authority('筆記')

        note.group_no = None
        note.save()
        return success()
