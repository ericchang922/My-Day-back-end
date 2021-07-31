from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import ObjectDoesNotExist

from api.models import Notice, Account, Friend
from api.response import *
from setting.serializers import SettingSerializer


# Create your views here.
class SettingViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = SettingSerializer

    @action(detail=False, methods=['POST'])
    def notice(self, request):
        data = request.data

        uid = data.get('uid')
        is_schedule = data.get('isSchedule')
        is_countdown = data.get('isCountdown')
        is_group = data.get('isGroup')
        is_temporary = data.get('isTemporary')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-A-001', request)

        if is_schedule is not None:
            account.is_schedule_notice = is_schedule

        if is_countdown is not None:
            account.is_countdown_notice = is_countdown

        if is_group is not None:
            account.is_group_notice = is_group

        if is_temporary is not None:
            account.is_temporary_group_notice = is_temporary

        account.save()

        return success(request=request)

    @action(detail=False, methods=['POST'])
    def theme(self, request):
        data = request.data

        uid = data.get('uid')
        theme_id = data.get('themeId')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-B-001', request)

        if theme_id is not None:
            account.theme_id = theme_id

        account.save()

        return success(request=request)

    @action(detail=False, methods=['POST'])
    def privacy(self, request):
        data = request.data

        uid = data.get('uid')
        is_location = data.get('isLocation')
        is_public = data.get('isPublic')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'SE-C-001', request)

        if is_location is not None:
            account.is_location = is_location

        if is_public is not None:
            account.is_public = is_public

        account.save()

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
            return err(Msg.NotFound.friend, 'SE-D-001', request)

        if is_temporary is not None:
            friend.update(is_temporary_group=is_temporary)

        if is_public is not None:
            friend.update(is_public_timetable=is_public)

        return success(request=request)
