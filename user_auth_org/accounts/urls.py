from django.urls import path
from .views import (
    RegisterView, LoginView, UserDetailView, OrganisationListView, 
    OrganisationDetailView, OrganisationCreateView, AddUserToOrganisationView,
    CustomTokenObtainPairView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('api/users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('api/organisations/', OrganisationListView.as_view(), name='organisation-list'),
    path('api/organisations/<int:orgId>/', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('api/organisationsCreate/', OrganisationCreateView.as_view(), name='organisation-create'),
    path('api/organisations/<int:orgId>/users/', AddUserToOrganisationView.as_view(), name='add-user-to-organisation'),
     path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]