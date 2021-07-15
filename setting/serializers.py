from rest_framework.serializers import ModelSerializer

from api.models import Notice


class SettingSerializer(ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
