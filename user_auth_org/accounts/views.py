from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import DatabaseError
from .models import User, Organisation
from .serializers import (
    UserSerializer, OrganisationSerializer, OrganisationCreateSerializer,
    RegistrationSerializer, LoginSerializer, AddUserToOrganisationSerializer,
    CustomTokenObtainPairSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import LoginSerializer
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponse


def welcome_view(request):
    return HttpResponse("BACKEND Stage 2 Task: User Authentication & Organisation")

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            user = User.objects.create_user(
                email=validated_data['email'],
                firstName=validated_data['firstName'],
                lastName=validated_data['lastName'],
                password=validated_data['password'],
                phone=validated_data.get('phone', '')
            )

            org_name = f"{user.firstName}'s Organisation"
            organisation = Organisation.objects.create(
                name=org_name,
                description=f"Organisation created for {user.firstName} {user.lastName}"
            )
            organisation.users.add(user)

            refresh = RefreshToken.for_user(user)

            return Response({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    'accessToken': str(refresh.access_token),
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_201_CREATED)
        except DRFValidationError as exc:
            errors = []
            for field, messages in exc.detail.items():
                for message in messages:
                    errors.append({
                        "field": field,
                        "message": message
                    })
            return Response({
                "errors": errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except DjangoValidationError as exc:
            return Response({
                "status": "Bad request",
                "message": "Validation error occurred",
                "message":"Registration unsuccessful",
                "details": exc.messages,
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as exc:
            return Response({
                "status": "Bad request",
                "message": "Database error occurred during registration. Please try again later.",
                "details": str(exc),
                "message":"Registration unsuccessful",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({
                "status": "Bad request",
                "message": "An unexpected error occurred during registration. Please try again later.",
                "details": str(exc),
                "message":"Registration unsuccessful",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])

            if not user:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'Authentication failed',
                    'statusCode': 401
                }, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'accessToken': str(refresh.access_token),
                    'user': {
                        'userId': user.userId,  
                        'email': user.email,
                        'firstName': user.firstName,
                        'lastName': user.lastName
                    }
                }
            }, status=status.HTTP_200_OK)
        
        except DRFValidationError as exc:
            errors = []
            for field, messages in exc.detail.items():
                for message in messages:
                    errors.append({
                        "field": field,
                        "message": message
                    })
            return Response({
                "errors": errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        
        try:
            user = User.objects.get(userId=user_id)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if the requesting user can access this user's data
        if request.user.is_authenticated:
            if str(request.user.userId) == str(user_id):
                # Return data if the user is requesting their own data
                serializer = self.get_serializer(user)
                return Response({
                    "status": "success",
                    "message": "User record retrieved successfully",
                    "data": {
                        "userId": user.userId,
                        "firstName": user.firstName,
                        "lastName": user.lastName,
                        "email": user.email,
                        "phone": user.phone
                    }
                }, status=status.HTTP_200_OK)
            elif hasattr(user, 'organizations') and user.organizations.filter(users=request.user).exists():
                # Return data if the requesting user belongs to the same organization(s)
                serializer = self.get_serializer(user)
                return Response({
                    "status": "success",
                    "message": "User record retrieved successfully",
                    "data": {
                        "userId": user.userId,
                        "firstName": user.firstName,
                        "lastName": user.lastName,
                        "email": user.email,
                        "phone": user.phone
                    }
                }, status=status.HTTP_200_OK)
            else:
                # Return error if the requesting user is not authorized
                return Response({
                    "status": "error",
                    "message": "Unauthorized to access this user's data"
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            # Return error if the user is not authenticated
            return Response({
                "status": "error",
                "message": "Authentication credentials were not provided."
            }, status=status.HTTP_401_UNAUTHORIZED)

        
class OrganisationListView(GenericAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organisations = request.user.organisations.all()
        serializer = self.get_serializer(organisations, many=True)
        return Response({
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {"organisations": serializer.data}
        }, status=status.HTTP_200_OK)

class OrganisationDetailView(RetrieveAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        org_id = self.kwargs['orgId']
        try:
            organisation = Organisation.objects.get(pk=org_id, users=self.request.user)
            return organisation
        except Organisation.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "message": "Organisation record retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "Forbidden",
                "message": "You do not have permission to access this organisation."
            }, status=status.HTTP_403_FORBIDDEN)
    
class OrganisationCreateView(GenericAPIView):
    serializer_class = OrganisationCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            # Perform database operation directly in the view
            organisation = Organisation.objects.create(
                name=validated_data['name'],
                description=validated_data.get('description', '')
            )
            organisation.users.add(request.user)

            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": {
                    "orgId": organisation.org_id,  # Adjust based on your actual field name
                    "name": organisation.name,
                    "description": organisation.description
                }
            }, status=status.HTTP_201_CREATED)

        except DRFValidationError as exc:
            errors = []
            for field, messages in exc.detail.items():
                for message in messages:
                    errors.append({
                        "field": field,
                        "message": message
                    })
            return Response({
                "status": "Bad Request",
                "message": "Client error",
                "errors": errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except DjangoValidationError as exc:
            return Response({
                "status": "Bad Request",
                "message": "Validation error occurred",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        except DatabaseError as exc:
            return Response({
                "status": "Bad Request",
                "message": "Database error occurred during organisation creation. Please try again later.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as exc:
            return Response({
                "status": "Bad Request",
                "message": "An unexpected error occurred during organisation creation. Please try again later.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

class AddUserToOrganisationView(GenericAPIView):
    serializer_class = AddUserToOrganisationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            try:
                organisation = Organisation.objects.get(pk=orgId, users=request.user)
            except Organisation.DoesNotExist:
                return Response({
                    "status": "Not Found",
                    "message": "Organisation not found",
                    "statusCode": 404
                }, status=status.HTTP_404_NOT_FOUND)

            try:
                user = User.objects.get(pk=validated_data['userId'])
            except User.DoesNotExist:
                return Response({
                    "status": "Not Found",
                    "message": "User not found",
                    "statusCode": 404
                }, status=status.HTTP_404_NOT_FOUND)

            organisation.users.add(user)

            return Response({
                "status": "success",
                "message": "User added to organisation successfully"
            }, status=status.HTTP_200_OK)
        except DRFValidationError as exc:
            errors = []
            for field, messages in exc.detail.items():
                for message in messages:
                    errors.append({
                        "field": field,
                        "message": message
                    })
            return Response({
                "errors": errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except DjangoValidationError as exc:
            return Response({
                "status": "Bad request",
                "message": "Validation error occurred",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except DatabaseError as exc:
            return Response({
                "status": "Bad request",
                "message": "Database error occurred during adding user to organisation. Please try again later.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({
                "status": "Bad request",
                "message": "An unexpected error occurred during adding user to organisation. Please try again later.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
