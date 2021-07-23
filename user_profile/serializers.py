from rest_framework.serializers import ModelSerializer

from api.models import Account


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
