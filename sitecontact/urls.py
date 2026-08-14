from django.urls import path
from .views import SiteInfoView, ContactMessageCreateView

urlpatterns = [
    path('site-info/', SiteInfoView.as_view(), name='site-info'),
    path('contact/', ContactMessageCreateView.as_view(), name='contact-submit'),
]
