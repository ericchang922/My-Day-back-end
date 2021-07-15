from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Account


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
