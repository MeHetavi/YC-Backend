# urls.py
from django.urls import path
from .views import AcceptParticipants, SessionDetailAPIView,SessionListCreateAPIView, SessionParticipantCreateAPIView, SessionParticipantsAPIView, UserJoinedSessionsAPIView

urlpatterns = [
    path('vc-urls', SessionListCreateAPIView.as_view(), name='vc_url_list_create'),
    path('vc-urls/<uuid:pk>', SessionDetailAPIView.as_view(), name='vc_url_detail'),
    path('', SessionListCreateAPIView.as_view(), name='session-list-create'),
    path('<str:pk>/', SessionDetailAPIView.as_view(), name='session-detail'),
    path('<str:session_id>/join', SessionParticipantCreateAPIView.as_view(), name='session-participant-join'),
    path('accept-participants',AcceptParticipants.as_view(),name="accept-participants")
    # path('<str:session_id>/participants', SessionParticipantsAPIView.as_view(), name='session-participants'),
    # path('users/joined-sessions', UserJoinedSessionsAPIView.as_view(), name='user-joined-sessions')
]