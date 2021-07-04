from rest_framework.response import Response
from rest_framework import status


def success(response={}):
    response.update({'response': True})
    return Response(response, status=status.HTTP_200_OK)


def err():
    return Response({'response': False, 'message': '錯誤'}, status=status.HTTP_400_BAD_REQUEST)


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
