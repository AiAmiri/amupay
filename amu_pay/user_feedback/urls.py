from django.urls import path
from .views import SubmitFeedbackView

app_name = 'user_feedback'

urlpatterns = [
    path('submit/', SubmitFeedbackView.as_view(), name='submit_feedback'),
]

