# python
import logging
# rest
from rest_framework.response import Response
from rest_framework import status
# my day
from api.log_func import log_func
# 使用response的時候則無需再import message
from api.message import *

logger = logging.getLogger('my_day')


def success(response={}, request=None):
    response.update({'response': True})
    logger.info(log_func(request, 'OK'))
    return Response(response, status=status.HTTP_200_OK)


def err(message='錯誤', err_code='', request=None):
    logger.error(log_func(request, message, 'ERROR', err_code))
    return Response({'response': False, 'message': message, 'err_code': err_code}, status=status.HTTP_400_BAD_REQUEST)


def not_found(message='不存在', request=None):
    logger.warning(log_func(request, 'NOT_FOUND', message))
    return Response({'response': False, 'message': message}, status=status.HTTP_404_NOT_FOUND)


def no_authority(authority='', request=None):
    message = f'沒有{authority}權限'
    logger.warning(log_func(request, 'NO_AUTHORITY', message))
    return Response({'response': False, 'message': message}, status=status.HTTP_403_FORBIDDEN)


# vote
def no_item(request=None):
    message = '至少新增一個選項'
    logger.warning(log_func(request, 'NO_ITEM', message))
    return Response({'response': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)


def can_not_edit(request=None):
    message = '已經投票不能修改'
    logger.warning(log_func(request, 'CAN_NOT_EDIT', message))
    return Response({'response': False, 'message': message}, status=status.HTTP_403_FORBIDDEN)


def limit_vote(request=None):
    message = '超過票數限制'
    logger.warning(log_func(request, 'LIMIT_VOTE', message))
    return Response({'response': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)


def vote_option_exist(num='', request=None):
    if num != '':
        num = f'編號{num}的'
    message = f'{num}投票項目編號已經存在'
    logger.warning(log_func(request, 'VOTE_OPTION_EXIST', message))
    return Response({'response': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)


def vote_expired(request=None):
    message = '投票已過期'
    logger.warning(log_func(request, 'VOTE_EXPIRED', message))
    return Response({'response': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)


# note
def note_is_connect(request=None):
    message = '筆記已經與讀書計畫綁定，請先解除綁定'
    logger.warning(log_func(request, 'NOTE_IS_CONNECT', message))
    return Response({'response': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)
