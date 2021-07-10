from rest_framework.response import Response
from rest_framework import status


def success(response={}):
    response.update({'response': True})
    return Response(response, status=status.HTTP_200_OK)


def err():
    return Response({'response': False, 'message': '錯誤'}, status=status.HTTP_400_BAD_REQUEST)


def note_not_found():
    return Response({'response': False, 'message': '筆記不存在'}, status=status.HTTP_404_NOT_FOUND)


def user_note_not_found():
    return Response({'response': False, 'message': '用戶沒有此筆記'}, status=status.HTTP_404_NOT_FOUND)


def no_authority():
    return Response({'response': False, 'message': '沒有權限'}, status=status.HTTP_403_FORBIDDEN)


def not_in_group():
    return Response({'response': False, 'message': '用戶沒有此群組'}, status=status.HTTP_404_NOT_FOUND)

def group_not_found():
    return Response({'response': False, 'message': '群組不存在'}, status=status.HTTP_404_NOT_FOUND)
