from rest_framework import serializers

from api.models import Account


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['name', 'user_id', 'password']

    def save(self):
        account = Account(
             user_id=self.validated_data['user_id'],
             name=self.validated_data['name'],
             password=self.validated_data['password'],
        )
        account.save()
        return account

