import string
import random

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import ObjectDoesNotExist
from datetime import datetime
from django.core.mail import send_mail

from api.models import Account, VerificationCode
from api.response import *
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
                return err(Msg.Err.Account.registered, 'AC-A-001')
            else:
                new_account = Account.objects.create(user_id=uid, name=name, password=password)
                new_account.save()
        except:
            return err(Msg.Err.Account.account_create)
        return success()

    @action(detail=False, methods=['POST'])
    def change_pw(self, request):
        data = request.data

        uid = data.get('uid')
        password = data.get('password')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account)
        except:
            return err(Msg.Err.Account.get, 'AC-B-001')

        if password is not None:
            account.password = password

        account.save()

        return success()

    @action(detail=False, methods=['POST'])
    def login(self, request):
        data = request.data

        uid = data.get('uid')
        password = data.get('password')

        try:
            account = Account.objects.get(user_id=uid, password=password)
        except:
            return err(Msg.Err.Account.login, 'AC-C-001')

        response = {
            'userName': account.name
        }

        return success(response)

    @action(detail=False, methods=['POST'])
    def send_code(self, request):
        data = request.data

        uid = data.get('uid')

        try:
            Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account)
        except:
            return err(Msg.Err.Account.get, 'AC-D-001')

        code = ''
        for i in range(6):
            code += str(random.choice(string.ascii_letters + string.digits))

        try:
            get_code = VerificationCode.objects.get(user_id=uid)
            get_code.delete()
            VerificationCode.objects.create(user_id=uid, ver_code=code, create_time=datetime.now())
        except:
            VerificationCode.objects.create(user_id=uid, ver_code=code, create_time=datetime.now())

        send_mail('您的learnAt驗證碼',
                  '驗證碼：'+code,
                  'learnat.ntub@gmail.com',
                  ['thomas355213@gmail.com'],
                  fail_silently=False)

        return success()

    @action(detail=False, methods=['POST'])
    def forget_pw(self, request):
        data = request.data

        uid = data.get('uid')
        verification_Code = data.get('verificationCode')

        try:
            VerificationCode.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.verification_code)

        try:
            VerificationCode.objects.get(user_id=uid, ver_code=verification_Code)
        except:
            return err(Msg.Err.Account.verification_code, 'AC-E-001')

        return success()
