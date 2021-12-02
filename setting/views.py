from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import ObjectDoesNotExist

from api.models import Notice, Account, Friend, PersonalTimetable
from api.response import *
from setting.serializers import SettingSerializer

from datetime import datetime

# Create your views here.
class SettingViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = SettingSerializer

    @action(detail=False, methods=['POST'])
    def notice(self, request):
        data = request.data

        uid = data['uid']
        is_schedule = data['isSchedule']
        is_countdown = data['isCountdown']
        is_group = data['isGroup']

        try:
            account = Notice.objects.filter(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-A-001', request)

        if is_schedule is not None:
            account.update(is_schedule_notice = is_schedule)

        if is_countdown is not None:
            account.update(is_countdown_notice = is_countdown)

        if is_group is not None:
            account.update(is_group_notice = is_group)

        return success(request=request)

    @action(detail=False, methods=['POST'])
    def notice_temporary(self, request):
        data = request.data

        uid = data['uid']
        is_temporary = data['isTemporary']

        try:
            account = Notice.objects.filter(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-B-001', request)

        if is_temporary is not None:
            account.update(is_temporary_group_notice=is_temporary)

        return success(request=request)

    @action(detail=False, methods=['POST'])
    def themes(self, request):
        data = request.data

        uid = data['uid']
        theme_id = data['themeId']

        try:
            account = Account.objects.filter(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-C-001', request)

        if theme_id is not None:
            account.update(theme_id=theme_id)

        return success(request=request)

    @action(detail=False)
    def get_themes(self, request):
        data = request.query_params

        uid = data.get('uid')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-D-001', request)

        response = {
            'theme': account.theme_id
        }

        return success(response, request)

    @action(detail=False, methods=['POST'])
    def privacy_location(self, request):
        data = request.data

        uid = data['uid']
        is_location = data['isLocation']

        try:
            account = Account.objects.filter(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-E-001', request)

        if is_location is not None:
            account.update(is_location=is_location)

        return success(request=request)

    @action(detail=False, methods=['POST'])
    def privacy_timetable(self, request):
        data = request.data

        uid = data.get('uid')
        is_public = data.get('isPublic')

        try:
            account = Account.objects.filter(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-F-001', request)

        if is_public is not None:
            account.update(is_public=is_public)

        return success(request=request)

    @action(detail=False, methods=['POST'])
    def friend_privacy(self, request):
        data = request.data

        uid = data.get('uid')
        friend_id = data.get('friendId')
        is_public = data.get('isPublic')
        is_temporary = data.get('isTemporary')

        try:
            friend = Friend.objects.filter(user_id=uid, related_person=friend_id)
        except:
            return err(Msg.NotFound.friend, 'SE-G-001', request)

        if is_temporary is not None:
            friend.update(is_temporary_group=is_temporary)

        if is_public is not None:
            friend.update(is_public_timetable=is_public)

        return success(request=request)

    @action(detail=False)
    def get_location(self, request):
        data = request.query_params

        uid = data.get('uid')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-H-001', request)

        response = {
            'location': account.is_location
        }

        return success(response, request)

    @action(detail=False)
    def get_timetable(self, request):
        data = request.query_params

        uid = data.get('uid')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-I-001', request)

        response = {
            'timetable': account.is_public
        }

        return success(response, request)

    @action(detail=False)
    def get_friend_privacy(self, request):
        data = request.query_params

        uid = data.get('uid')
        friend_id = data.get('friendId')

        friend = Friend.objects.filter(user_id=uid, related_person=friend_id, relation_id__in=[1, 2])
        if friend.exists():
            return success({
                'isPublicTimetable': friend.first().is_public_timetable,
                'isTemporaryGroup': friend.first().is_temporary_group
            }, request)
        else:
            return not_found(Msg.NotFound.friend, request)

    @action(detail=False)
    def get_notice(self, request):
        data = request.query_params

        uid = data.get('uid')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-L-001', request)

        response = {
            'scheduleNotice': account.notice.is_schedule_notice,
            'temporaryNotice': account.notice.is_temporary_group_notice,
            'countdownNotice': account.notice.is_countdown_notice,
            'groupNotice': account.notice.is_group_notice
        }

        return success(response, request)
