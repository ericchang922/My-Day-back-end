# python
import base64
# rest
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
# myday
from note.serializer import NoteSerializer
from api.models import Note, GroupMember, Group
# note
from note.response import *


# Create your views here.
class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    # /note/create_new/  -----------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def create_new(self, request):
        data = request.data

        uid = data.get('uid')
        type_name = data.get('typeName')
        title = data.get('title')
        content = data.get('content')

        try:
            note = Note.objects.create(create_id=uid, type_name=type_name, title=title, content=content,
                                       is_personal=True)
        except:
            return err()

        note.save()
        return success()

    # /note/edit/  -----------------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def edit(self, request):
        data = request.data

        uid = data.get('uid')
        note_no = data.get('noteNum')
        type_name = data.get('typeName')
        title = data.get('title')
        content = data.get('content')

        try:
            note = Note.objects.get(serial_no=note_no)
        except:
            return note_not_found()

        if note.create_id != uid:
            try:
                group_member = GroupMember.objects.filter(user=uid, group_no=note.group_no)
            except:
                return err()
            if len(group_member) > 0:
                return no_authority()
            else:
                return user_note_not_found()

        if note.type_name != type_name and type_name is not None:
            note.type_name = type_name
        if note.title != title and title is not None:
            note.title = title
        if note.content != content and content is not None:
            note.content = content

        note.save()
        return success()

    # /note/delete/  ---------------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def delete(self, request):
        data = request.data

        uid = data.get('uid')
        note_no = data.get('noteNum')

        try:
            note = Note.objects.get(serial_no=note_no)
        except:
            return note_not_found()

        if note.create_id != uid:
            try:
                group_member = GroupMember.objects.filter(user=uid, group_no=note.group_no)
            except:
                return err()
            if len(group_member) > 0:
                return no_authority()
            else:
                return user_note_not_found()
        else:
            note.delete()
            return success()

    # /note/get/  ------------------------------------------------------------------------------------------------------
    @action(detail=False)
    def get(self, request):
        data = request.query_params

        uid = data.get('uid')
        note_no = data.get('noteNum')

        try:
            note = Note.objects.get(serial_no=note_no)
        except:
            return note_not_found()

        if note.create_id != uid:
            try:
                group_member = GroupMember.objects.filter(user=uid, group_no=note.group_no, status=1)
                group_manager = GroupMember.objects.filter(user=uid, group_no=note.group_no, status=4)
            except:
                return err()
            if len(group_member) <= 0 and len(group_manager) <= 0:
                return user_note_not_found()

        response = {
            'title': note.title,
            'content': note.content
        }
        return success(response)

    # /note/get_list/  -------------------------------------------------------------------------------------------------
    @action(detail=False)
    def get_list(self, request):
        data = request.query_params

        uid = data.get('uid')

        try:
            note = Note.objects.filter(create_id=uid)
        except:
            return err()

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

    # /note/get_group_list/  -------------------------------------------------------------------------------------------
    @action(detail=False)
    def get_group_list(self, request):
        data = request.query_params

        uid = data.get('uid')
        group_no = data.get('groupNum')

        try:
            group_member = GroupMember.objects.filter(user=uid, group_no=group_no, status=1)
            group_manager = GroupMember.objects.filter(user=uid, group_no=group_no, status=4)
        except:
            return err()
        if len(group_member) <= 0 and len(group_manager) <= 0:
            return not_in_group()

        try:
            note = Note.objects.filter(group_no=group_no)
        except:
            return err()

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

    # /note/share/  ----------------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def share(self, request):
        data = request.data

        uid = data.get('uid')
        group_no = data.get('groupNum')
        note_no = data.get('noteNum')

        try:
            note = Note.objects.get(serial_no=note_no)
        except:
            return note_not_found()

        if note.create_id != uid:
            return user_note_not_found()

        try:
            group = Group.objects.get(serial_no=group_no)
        except:
            return group_not_found()
        try:
            group_member = GroupMember.objects.filter(user=uid, group_no=group, status=1)
            group_manager = GroupMember.objects.filter(user=uid, group_no=group, status=4)
        except:
            return err()

        if len(group_member) <= 0 and len(group_manager) <= 0:
            return not_in_group()

        note.group_no = group
        note.save()
        return success()

    # /note/cancel_share/  ---------------------------------------------------------------------------------------------
    @action(detail=False, methods=['POST'])
    def cancel_share(self, request):
        data = request.data

        uid = data.get('uid')
        note_no = data.get('noteNum')

        try:
            note = Note.objects.get(serial_no=note_no)
        except:
            return note_not_found()

        if note.create_id != uid:
            try:
                group_member = GroupMember.objects.filter(user=uid, group_no=note.group_no, status=1)
                group_manager = GroupMember.objects.filter(user=uid, group_no=note.group_no, status=4)
            except:
                return err()
            if len(group_member) > 0 or len(group_manager) > 0:
                print(uid)
                return no_authority()
            else:
                return user_note_not_found()

        note.group_no = None
        note.save()
        return success()
