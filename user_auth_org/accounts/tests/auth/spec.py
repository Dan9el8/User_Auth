from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import jwt
from django.utils import timezone
from django.conf import settings
import pytz
from accounts.models import Organisation
from rest_framework.test import APIClient


User = get_user_model()

class TokenGenerationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            firstName='Test',
            lastName='User',
            phone='+1234567890'
        )
        print("Setup: Created user with email 'testuser@example.com'")

    def test_token_generation_and_user_details(self):
        # Attempt to log in and get a token
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': 'testuser@example.com',
            'password': 'testpassword',
        })


        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extract the access token from the response
        access_token = response.data.get('access')

        # Proceed only if an access token was successfully obtained
        if access_token:
            # Decode the token to check its payload
            decoded_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            # print(f"Decoded token: {decoded_token}")

            # Assert the user ID in the token matches the user's ID
            self.assertEqual(decoded_token['user_id'], self.user.userId)

            # Convert the exp timestamp to a datetime object and make it offset-aware
            exp_datetime = datetime.fromtimestamp(decoded_token['exp'], pytz.utc)

            # Assert the token has not expired
            now = timezone.now()
            self.assertGreaterEqual(exp_datetime, now)

            # Assert the token contains the correct user details
            self.assertEqual(decoded_token['email'], 'testuser@example.com')
            self.assertEqual(decoded_token['firstName'], 'Test')
            self.assertEqual(decoded_token['lastName'], 'User')
            self.assertEqual(decoded_token['phone'], '+1234567890')
            print("Token contains the correct user details")
            print("Test for test_token_generation_and_user_details Passed")
        else:
            print("Access token not found in response")

class OrganisationAccessTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpassword1',
            firstName='User',
            lastName='One',
            phone='+1234567891'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpassword2',
            firstName='User',
            lastName='Two',
            phone='+1234567892'
        )

        # Create organisations
        self.org1 = Organisation.objects.create(
            name="Organisation One",
            description="Description for org one"
        )
        self.org2 = Organisation.objects.create(
            name="Organisation Two",
            description="Description for org two"
        )

        # Associate users with organisations
        self.org1.users.add(self.user1)
        self.org2.users.add(self.user2)

    def test_user_cannot_access_unauthorized_organisation(self):
        # Log in user1 to get the access token
        client = APIClient()
        login_response = client.post(reverse('token_obtain_pair'), {
            'email': 'user1@example.com',
            'password': 'testpassword1',
        })

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        access_token = login_response.data['access']
        
        # Authenticate with the access token
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        # Attempt to access data from org2 as user1
        response = client.get(reverse('organisation-detail', args=[self.org2.pk]))
        
        # Check if access is denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Print statements to confirm the test has passed
        print("Test  for test_user_cannot_access_unauthorized_organisation Passed.")


class RegisterEndpointTestCase(APITestCase):
    url = reverse('register')  # Assuming 'register' is the name of your registration endpoint

    def test_successful_registration(self):
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'testpassword',
            'phone': '+1234567890'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Optional: Check if user object was created in the database
        user = User.objects.get(email='john.doe@example.com')
        self.assertEqual(user.firstName, 'John')
        self.assertEqual(user.lastName, 'Doe')
        print("Test for test_successful_registration Passed")

    def test_unique_email_constraint(self):
        data1 = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'testpassword',
            'phone': '+254713511835'
        }
        data2 = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',  # Same email as data1
            'password': 'testpassword',
            'phone': '+254713511835'
        }

        response1 = self.client.post(self.url, data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(self.url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        print("Test for test_unique_email_constraint Passed")

    def test_missing_required_fields(self):
        # Test case for missing required fields
        data = {
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'testpassword'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('firstName', response.data['errors'][0]['field'])
        print("Test case for missing required fields passed")

    def test_invalid_email_format(self):
        # Test case for invalid email format
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'invalid-email-format',  # Invalid email format
            'password': 'testpassword'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('email', response.data['errors'][0]['field'])
        print("Test case for invalid email format Passed")

    def test_blank_password(self):
        # Test case for blank password
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': '',  # Blank password
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('password', response.data['errors'][0]['field'])
        print("Test case for blank password Passed")