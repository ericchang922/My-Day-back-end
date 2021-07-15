from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Account
from account.serializers import AccountSerializer


# Create your views here.
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @action(detail=False, methods=['POST'])
    def register(self, request):
        data = request.data

        uid = data.get('uid')
        name = data.get('userName')
        password = data.get('password')

        try:
            registered = Account.objects.filter(user_id=uid).count()

            if registered > 0:
                return Response({'response': False, 'message': '此email已被使用'}, status=status.HTTP_226_IM_USED)
            else:
                new_account = Account.objects.create(user_id=uid, name=name, password=password)
                new_account.save()
        except:
            return Response({'response': False, 'message': '錯誤'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Response': True, 'message': '成功'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def change_pw(self, request):
        data = request.data

        uid = data.get('uid')
        password = data.get('password')

        try:
            account = Account.objects.get(user_id=uid)
        except:
            return Response({'request': False, 'message': '沒有此帳號'}, status=status.HTTP_400_BAD_REQUEST)

        if password is not None:
            account.password = password

        account.save()

        return Response({'response': True, 'message': '更改密碼成功'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        data = request.data

        uid = data.get('uid')
        password = data.get('password')

        try:
            account = Account.objects.get(user_id=uid, password=password)
        except:
            return Response({'request': False, 'message': '登入失敗'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'response': True, 'message': account.name}, status=status.HTTP_200_OK)
