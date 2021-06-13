from rest_framework.serializers import ModelSerializer
from api.models import Friend

class FriendSerializer(ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'
