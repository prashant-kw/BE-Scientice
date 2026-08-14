from django.urls import path
from .views import (
    EducationCategoryListView,
    PatientEducationListView,
    MedicalEducationListView,
    CMEEducationListView,
    EducationResourceDetailView,
)

urlpatterns = [
    path('', EducationCategoryListView.as_view(), name='education-categories'),
    path('categories/', EducationCategoryListView.as_view(), name='education-categories-alt'),
    path('patient/', PatientEducationListView.as_view(), name='education-patient'),
    path('medical/', MedicalEducationListView.as_view(), name='education-medical'),
    path('guidelines/', CMEEducationListView.as_view(), name='education-guidelines-cme'),
    path('resource/<int:pk>/', EducationResourceDetailView.as_view(), name='education-resource-detail'),
]
