from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Notice, Account, Friend
from setting.serializers import SettingSerializer


# Create your views here.
class SettingViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = SettingSerializer

    @action(detail=False, methods=['POST'])
    def notice(self, request):
        data = request.data

        uid = data.get('uid')
        isSchedule = data.get('isSchedule')
        isCountdown = data.get('isCountdown')
        isGroup = data.get('isGroup')
        isTemporary = data.get('isTemporary')

        try:
            account = Notice.objects.get(user_id=uid)
        except:
            return Response({'request': False, 'message': '沒有此帳號'}, status=status.HTTP_400_BAD_REQUEST)

        if isSchedule is not None:
            account.is_schedule_notice = isSchedule

        if isCountdown is not None:
            account.is_countdown_notice = isCountdown

        if isGroup is not None:
            account.is_group_notice = isGroup

        if isTemporary is not None:
            account.is_temporary_group_notice = isTemporary

        account.save()

        return Response({'Response': True, 'message': '成功'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def theme(self, request):
        data = request.data

        uid = data.get('uid')
        themeId = data.get('themeId')

        try:
            account = Account.objects.get(user_id=uid)
        except:
            return Response({'request': False, 'message': '沒有此帳號'}, status=status.HTTP_400_BAD_REQUEST)

        if themeId is not None:
            account.theme_id = themeId

        account.save()

        return Response({'Response': True, 'message': '成功'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def privacy(self, request):
        data = request.data

        uid = data.get('uid')
        isLocation = data.get('isLocation')
        isPublic = data.get('isPublic')

        try:
            account = Account.objects.get(user_id=uid)
        except:
            return Response({'request': False, 'message': '沒有此帳號'}, status=status.HTTP_400_BAD_REQUEST)

        if isLocation is not None:
            account.is_location = isLocation

        if isPublic is not None:
            account.is_public = isPublic

        account.save()

        return Response({'Response': True, 'message': '成功'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def friend_privacy(self, request):
        data = request.data

        uid = data.get('uid')
        friendId = data.get('friendId')
        isPublic = data.get('isPublic')
        isTemporary = data.get('isTemporary')

        try:
            friend = Friend.objects.filter(user_id=uid, related_person=friendId)
        except:
            return Response({'request': False, 'message': '他們還不是朋友'}, status=status.HTTP_400_BAD_REQUEST)

        if isTemporary is not None:
            friend.update(is_temporary_group=isTemporary)

        if isPublic is not None:
            friend.update(is_public_timetable=isPublic)

        return Response({'Response': True, 'message': '成功'}, status=status.HTTP_200_OK)
