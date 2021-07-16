# rest
from rest_framework.response import Response
from rest_framework import status
from api.message import *


def success(response={}):
    response.update({'response': True})
    return Response(response, status=status.HTTP_200_OK)


def err(message='錯誤', err_code=''):
    return Response({'response': False, 'message': message, 'err_code': err_code}, status=status.HTTP_400_BAD_REQUEST)


def not_found(message='不存在'):
    return Response({'response': False, 'message': message}, status=status.HTTP_404_NOT_FOUND)


def no_authority():
    return Response({'response': False, 'message': '沒有權限'}, status=status.HTTP_403_FORBIDDEN)


# vote
def option_type_not_exist():
    return Response({'response': False, 'message': '投票類型不存在'}, status=status.HTTP_412_PRECONDITION_FAILED)


def no_item():
    return Response({'response': False, 'message': '至少新增一個選項'}, status=status.HTTP_400_BAD_REQUEST)


def can_not_edit():
    return Response({'response': False, 'message': '已經投票不能修改'}, status=status.HTTP_403_FORBIDDEN)
