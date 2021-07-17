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


def no_authority(authority=''):
    return Response({'response': False, 'message': f'沒有{authority}權限'}, status=status.HTTP_403_FORBIDDEN)


# vote
def option_type_not_exist():
    return Response({'response': False, 'message': '投票類型不存在'}, status=status.HTTP_412_PRECONDITION_FAILED)


def no_item():
    return Response({'response': False, 'message': '至少新增一個選項'}, status=status.HTTP_400_BAD_REQUEST)


def can_not_edit():
    return Response({'response': False, 'message': '已經投票不能修改'}, status=status.HTTP_403_FORBIDDEN)


def limit_vote():
    return Response({'response': False, 'message': '超過票數限制'}, status=status.HTTP_400_BAD_REQUEST)


def vote_option_exist(message=''):
    if message != '':
        message = f'編號{message}的'
    return Response({'response': False, 'message': f'{message}投票項目編號已經存在'}, status=status.HTTP_400_BAD_REQUEST)


def vote_expired():
    return Response({'response': False, 'message': '投票已過期'}, status=status.HTTP_400_BAD_REQUEST)


# note
def note_is_connect():
    return Response({'response': False, 'message': '筆記已經與讀書計畫綁定，請先解除綁定'}, status=status.HTTP_400_BAD_REQUEST)
