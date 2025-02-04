# serializers.py
from rest_framework import serializers
from .models import Session,SessionParticipant

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [ 'id','url', 'title', 'start_time', 'end_time', 'trainer','created_at','description','fees','duration','accept_participants']

class SessionParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionParticipant
        fields = "__all__"
