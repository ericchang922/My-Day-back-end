from rest_framework.response import Response
from rest_framework import status


# err message
class ErrMessage:
    vote_create = '建立投票錯誤'
    vote_option_create = '建立投票項目錯誤'
    group_member_read = '群組資料讀取錯誤'


def success(response={}):
    response.update({'response': True})
    return Response(response, status=status.HTTP_200_OK)


def err(message='錯誤'):
    return Response({'response': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)


def not_in_group():
    return Response({'response': False, 'message': '用戶沒有此群組'}, status=status.HTTP_404_NOT_FOUND)


def option_type_not_exist():
    return Response({'response': False, 'message': '投票類型不存在'}, status=status.HTTP_400_BAD_REQUEST)


def no_item():
    return Response({'response': False, 'message': '至少新增一個選項'}, status=status.HTTP_400_BAD_REQUEST)


def group_not_found():
    return Response({'response': False, 'message': '群組不存在'}, status=status.HTTP_404_NOT_FOUND)
