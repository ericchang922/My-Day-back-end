from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.db.models import ObjectDoesNotExist

from api.models import Account
from api.response import *
from user_profile.serializers import ProfileSerializer


# Create your views here.
class ProfileViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False)
    def profile_list(self, request):
        data = request.query_params

        uid = data.get('uid')

        try:
            account = Account.objects.get(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'US-A-001', request)

        response = {
            'userName': account.name,
            'photo': str(account.photo)
        }

        return success(response, request)

    @action(detail=False, methods=['POST'])
    def edit_profile(self, request):
        data = request.data

        uid = data['uid']
        name = data['userName']
        photo = data['photo']

        try:
            account = Account.objects.filter(user_id=uid)
        except ObjectDoesNotExist:
            return not_found(Msg.NotFound.account, request)
        except:
            return err(Msg.Err.Account.get, 'US-B-001', request)

        if name is not None:
            account.update(name=name)

        if photo is not None:
            account.update(photo=photo)

        return success(request=request)
