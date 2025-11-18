from django.urls import path
from . import views

app_name = 'hawala'

urlpatterns = [
    # Send Hawala (Mode 1 & 2.1)
    path('send/', views.SendHawalaView.as_view(), name='send_hawala'),
    
    # Receive Hawala (Mode 1)
    path('receive/', views.ReceiveHawalaListView.as_view(), name='receive_hawala_list'),
    path('receive/<str:hawala_number>/', views.ReceiveHawalaDetailView.as_view(), name='receive_hawala_detail'),
    
    # External Receive Hawala (Mode 2.2)
    path('external-receive/', views.ExternalReceiveHawalaView.as_view(), name='external_receive_hawala'),
    
    # Hawala History and Management
    path('history/', views.HawalaHistoryView.as_view(), name='hawala_history'),
    path('list-all/', views.ListAllHawalasView.as_view(), name='list_all_hawalas'),
    path('status/<str:hawala_number>/', views.HawalaStatusUpdateView.as_view(), name='hawala_status_update'),
    path('statistics/', views.hawala_statistics, name='hawala_statistics'),
    
    # Receipt endpoints
    path('receipt/<str:hawala_number>/', views.HawalaReceiptView.as_view(), name='hawala_receipt'),
    path('generate-receipt/<str:hawala_number>/', views.GenerateReceiptView.as_view(), name='generate_receipt'),
    path('supported-currencies/', views.SupportedCurrenciesView.as_view(), name='supported_currencies'),
    
    # Normal user lookup endpoint
    path('lookup-by-phone/', views.NormalUserHawalaLookupView.as_view(), name='hawala_lookup_by_phone'),
]
