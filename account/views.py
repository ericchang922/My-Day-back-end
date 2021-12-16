import string
import random

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import ObjectDoesNotExist
from datetime import datetime
from django.core.mail import send_mail

import core.settings
from api.models import Account, VerificationCode, Notice
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
                new_account = Account.objects.create(user_id=uid, name=name,
                                                     photo='data:image/png;base64,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',
                                                     password=password, theme_id='1', is_public='0', is_help='0',
                                                     is_location='0')
                new_account.save()
                Notice.objects.create(user_id=uid, is_group_notice='1', is_countdown_notice='1',
                                      is_temporary_group_notice='1',
                                      is_schedule_notice='1')
        except:
            return err(Msg.Err.Account.account_create)
        return success()

    @action(detail=False, methods=['POST'])
    def change_pw(self, request):
        data = request.data

        uid = data.get('uid')
        password = data.get('password')

        try:
            account = Account.objects.filter(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account)
        except:
            return err(Msg.Err.Account.get, 'AC-B-001')

        if password is not None:
            account.update(password=password)

        return success()

    @action(detail=False, methods=['POST'])
    def login(self, request):
        data = request.data

        uid = data.get('uid')
        password = data.get('password')

        try:
            account = Account.objects.get(user_id=uid, password=password)
        except:
            try:
                account = Account.objects.get(user_id=uid)
            except ObjectDoesNotExist:
                return not_found(Msg.NotFound.account)

            if account.password != password:
                return not_found(Msg.NotFound.password_wrong)
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

        send_mail('您的My Day驗證碼',
                  '驗證碼：' + code,
                  core.settings.EMAIL_HOST_USER,
                  [uid],
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
