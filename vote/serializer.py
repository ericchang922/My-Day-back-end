from rest_framework.serializers import ModelSerializer

from api.models import Vote

class VoteSerializer(ModelSerializer):
    class Mata:
        model = Vote
        fields = '__all__'