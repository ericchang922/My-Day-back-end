from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Account
from account.serializers import RegisterSerializer


# Create your views here.
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = RegisterSerializer

    @action(detail=False, methods=['POST'])
    def register(self, request):

        serializer = RegisterSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['uid'] = account.user_id
            data['userName'] = account.name
            data['password'] = account.password
            data['response'] = '成功'

        return Response(data)


