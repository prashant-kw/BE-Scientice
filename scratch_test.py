import traceback
from rest_framework.test import APIRequestFactory
from accounts.models import User
from rest_framework.test import force_authenticate
from cms.views import TherapyAreaCMSViewSet

try:
    factory = APIRequestFactory()
    request = factory.get('/api/cms/therapy-areas/', HTTP_HOST='localhost')
    user = User.objects.filter(is_superuser=True).first()
    force_authenticate(request, user=user)
    view = TherapyAreaCMSViewSet.as_view({'get': 'list'})
    response = view(request)
    print("Status Code:", response.status_code)
    if response.status_code != 200:
        print(response.data)
    else:
        print("Success, length of data:", len(response.data.get('results', [])))
except Exception as e:
    print(traceback.format_exc())
