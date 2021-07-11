from rest_framework.response import Response
from rest_framework import status


class ErrMessage:
    schedule_create = '建立行程錯誤'
    personal_schedule_create = '建立個人行程錯誤'
    remind_create = '建立提醒錯誤'
    personal_schedule_select = '個人行程查詢錯誤'


def success(response={}):
    response.update({'response': True})
    return Response(response, status=status.HTTP_200_OK)


def err(message='錯誤'):
    return Response({'response': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)


def schedule_not_found():
    return Response({'response': False, 'message': '行程不存在'}, status=status.HTTP_404_NOT_FOUND)


def personal_schedule_not_found():
    return Response({'response': False, 'massage': '用戶沒有此行程'}, status=status.HTTP_404_NOT_FOUND)


def no_personal_schedule():
    return Response({'response': False, 'message': '用戶沒有行程'}, status=status.HTTP_404_NOT_FOUND)


def not_in_group():
    return Response({'response': False, 'message': '用戶沒有此群組'}, status=status.HTTP_404_NOT_FOUND)


def common_not_found():
    return Response({'response': False, 'message': '共同行程不存在'}, status=status.HTTP_404_NOT_FOUND)
