from rest_framework import serializers
from .models import User, Organisation

from rest_framework import serializers
class UserSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    firstName = serializers.CharField(max_length=30)
    lastName = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15, required=False)

class OrganisationSerializer(serializers.Serializer):
    orgId = serializers.IntegerField(source='org_id')
    name = serializers.CharField(max_length=255)
    description = serializers.CharField()

class OrganisationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1024, required=False)

class AddUserToOrganisationSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    

class RegistrationSerializer(serializers.Serializer):
    firstName = serializers.CharField(max_length=30)
    lastName = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=15, allow_blank=True)



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom fields
        token['email'] = user.email
        token['firstName'] = user.firstName
        token['lastName'] = user.lastName
        token['phone'] = user.phone

        return token