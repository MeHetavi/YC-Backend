from datetime import timedelta
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Session, SessionParticipant
from .serializers import SessionParticipantSerializer, SessionSerializer
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from profiles.models import Notification

User = get_user_model()

class SessionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        sessions = Session.objects.filter(trainer=request.user)
        for s in sessions:
            print(s.duration)
        
        serializer = SessionSerializer(sessions, many=True)

        data = serializer.data
        for d in data:
            d['participants'] = SessionParticipantsAPIView().get(request, d['id']).data
        return Response(serializer.data)

    def post(self, request):
        user = request.user    
        data = request.data.copy()  # Make a copy of the request data
        data['trainer'] = user.id # Explicitly add the trainer field to the data
        serializer = SessionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(trainer=user)
            data = self.get(request).data
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SessionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user):
        return Session.objects.get(trainer=user,many=True)
    
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        if user.is_trainer:
            vc_url = Session.objects.filter(trainer=user)
            serializer = SessionSerializer(vc_url,many=True)
            data = serializer.data
            for d in data:
                d['participants'] = SessionParticipantsAPIView().get(request, d['id']).data
            return Response(data,status=status.HTTP_200_OK)
        return Response({"error": "You are not a trainer"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user = request.user
        if user.is_trainer:
            vc_url = self.get_object(pk, user)
            serializer = SessionSerializer(vc_url, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "You are not a trainer"}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        user = request.user
        if user.is_trainer:
            vc_url = Session.objects.get(id=pk)
            serializer = SessionSerializer(vc_url, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                sessions = SessionListCreateAPIView().get(request).data
                return Response(sessions, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "You are not a trainer"}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        user = request.user
        if user.is_trainer:
            session = Session.objects.filter(id=pk).first()
            session.delete()
            sessions = SessionListCreateAPIView().get(request).data
            return Response(sessions,status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "You are not a trainer"}, status=status.HTTP_400_BAD_REQUEST)

# Cleanup expired participants
def remove_expired_participants():
    expired = SessionParticipant.objects.filter(expires__lt=now())

    for e in expired:
        Notification.objects.create(
                    actow= e.session.trainer,
                    recipient=e.user,
                    verb='Expired',
                    target=f'{e.session.title} Session'
                )
    expired.delete()

class SessionParticipantCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        """
        Add user as a session participant if not already joined.
        """
        remove_expired_participants()  # Clean up expired participants first

        session = get_object_or_404(Session, id=session_id)
        if session.accept_participants:
            user = request.user

            # Check if user is already a participant
            if SessionParticipant.objects.filter(session=session, user=user).exists():
                return Response({"error": "User already joined this session"}, status=status.HTTP_400_BAD_REQUEST)

            # Get expiration time (optional: set logic based on session duration)
            expires_at = now() + datetime.timedelta(days=session.duration)  # Adjust based on session model

            participant = SessionParticipant.objects.create(session=session, user=user, expires=expires_at)
            Notification.objects.create(
                        recipient=session.trainer,
                        actor=user,
                        verb='joined',
                        target=f'{session.title} Session'
                    )
            serializer = SessionParticipantSerializer(participant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Accepting no more participants."}, status=status.HTTP_400_BAD_REQUEST)


class SessionParticipantsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        """
        Retrieve all participants of a specific session.
        """
        remove_expired_participants()  # Clean up expired participants first
        session = get_object_or_404(Session, id=session_id)

        participants = SessionParticipant.objects.filter(session=session)  # Using related_name="participants"
        serializer = SessionParticipantSerializer(participants, many=True)
        for participant in serializer.data:
            user_id = participant['user']  # Assuming 'user' is storing the UUID
            user = User.objects.get(id=user_id)
            participant['user'] = user.username  # Add username to the data

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserJoinedSessionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all sessions a user has joined.
        """
        remove_expired_participants()  # Clean up expired participants first
        user = request.user
        sessions = SessionParticipant.objects.filter(user=user)  # Using related_name="joined_sessions"
        sessions_data = []

        for session in sessions:
            sessions_data+=[
                {
                    'title':session.session.title,
                    'trainer' : session.session.trainer.username,
                    'joined_at' : session.joined_at,
                    'expires' : session.expires,
                    'fees' : session.session.fees,
                    'start_time':session.session.start_time,
                    'accept_participants':session.session.accept_participants,
                    'end_time':session.session.end_time,
                    'duration':session.session.duration,
                    'url':session.session.url,
                    'session_id' : session.session.id
                }
            ]

        return Response(sessions_data, status=status.HTTP_200_OK)
    

class AcceptParticipants(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.POST.get('session_id')
        bool = request.POST.get('bool')
        session = Session.objects.get(id=session_id)
        session.accept_participants = bool
        session.save()
        data = SessionDetailAPIView().get(request,request.user.id).data
        return Response(data,status=status.HTTP_201_CREATED)
