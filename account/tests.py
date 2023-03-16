from django.test import TestCase
from account.models import UserAccount, UserAccountManager, UserProfile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from account.api.serializers import UserAccountSerializer, UserProfileSerializer
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class UserAccountManagerTest(TestCase):
    def setUp(self):
        self.manager = UserAccountManager()
        self.email = 'testuser@example.com'
        self.username = 'testuser'
        self.password = 'password123'
        self.otheremal = 'admin@test.com'
        self.otherusername = 'testadmin'
        self.user = UserAccount.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.superuser = UserAccount.objects.create_superuser(
            username='testsuperuser',
            email='testsuperuser@example.com',
            password='testpass'
        )

    def test_create_user(self):
        self.assertTrue(UserAccount.objects.filter(username='testuser').exists())
        self.assertTrue(self.user.check_password('testpass'))
        self.assertFalse(self.user.is_admin)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertEqual(self.user.groups.count(), 0)
        self.assertEqual(self.user.user_permissions.count(), 0)

    def test_create_superuser(self):
        self.assertTrue(UserAccount.objects.filter(username='testsuperuser').exists())
        self.assertTrue(self.superuser.check_password('testpass'))
        self.assertTrue(self.superuser.is_admin)
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)
        self.assertEqual(self.superuser.groups.count(), 0)
        self.assertEqual(self.superuser.user_permissions.count(), 0)

    def test_username_max_length(self):
        max_length = UserAccount._meta.get_field('username').max_length
        self.assertEquals(max_length, 30)

    def test_email_max_length(self):
        max_length = UserAccount._meta.get_field('email').max_length
        self.assertEquals(max_length, 100)

    def test_username_uniqueness(self):
        with self.assertRaises(Exception):
            UserAccount.objects.create_user(
                username='testuser',
                email='testuser2@example.com',
                password='testpass2'
            )

    def test_email_uniqueness(self):
        with self.assertRaises(Exception):
            UserAccount.objects.create_user(
                username='testuser2',
                email='testuser@example.com',
                password='testpass2'
            )

    def test_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_has_module_perms(self):
        self.assertTrue(self.user.has_module_perms('something'))
        self.assertTrue(self.superuser.has_module_perms('something'))

    def test_create_user_no_email(self):
        # Test that create_user raises a ValueError when no email is provided
        with self.assertRaises(ValueError):
            self.manager.create_user(email='', username=self.username, password=self.password)

    def test_create_user_no_username(self):
        # Test that create_user raises a ValueError when no username is provided
        with self.assertRaises(ValueError):
            self.manager.create_user(email=self.email, username='', password=self.password)

class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user_account = UserAccount.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass'
        )
        self.profile = UserProfile.objects.create(
            user=self.user_account,
            name='Test',
            last_name='User',
            status='Test status',
            bio='Test bio',
            location='Test location',
        )

    def test_profile_creation(self):
        self.assertEqual(str(self.profile), 'testuser profile')

    def test_friends_m2m(self):
        self.profile.friends.add(self.profile)
        with self.assertRaises(ValidationError):
            self.profile.clean()

    def test_profile_image_upload(self):
        self.assertTrue(self.profile.profile_img.url.endswith('profile_pics/default_profile.jpg'))

    def test_background_image_upload(self):
        self.assertTrue(self.profile.background_img.url.endswith('background_pics/default_bg.jpg'))


class UserAccountSerializerTest(TestCase):
    def test_create_user_account(self):
        data = {
            "email": "test@test.com",
            "username": "testuser",
            "password": "password123"
        }
        serializer = UserAccountSerializer(data=data)
        serializer.is_valid()
        user = serializer.save()
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_account_with_existing_email(self):
        user = UserAccount.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='password123'
        )
        data = {
            "email": "test@test.com",
            "username": "testuser2",
            "password": "password123"
        }
        serializer = UserAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_create_user_account_with_existing_username(self):
        user = UserAccount.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='password123'
        )
        data = {
            "email": "test2@test.com",
            "username": "testuser",
            "password": "password123"
        }
        serializer = UserAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_create_user_account_without_password(self):
        data = {
            "email": "test@test.com",
            "username": "testuser",
        }
        serializer = UserAccountSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class UserAccountSerializerTestCase(TestCase):
    def setUp(self):
        self.user_data = {'email': 'testuser@example.com', 'username': 'testuser', 'password': 'testpassword'}

    def test_valid_user_account_serializer(self):
        serializer = UserAccountSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user_account = serializer.save()
        self.assertEqual(user_account.email, self.user_data['email'])
        self.assertEqual(user_account.username, self.user_data['username'])
        self.assertTrue(user_account.check_password(self.user_data['password']))

    def test_unique_email_user_account_serializer(self):
        # create a user with the same email
        user = get_user_model().objects.create_user(**self.user_data)
        serializer = UserAccountSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_unique_username_user_account_serializer(self):
        # create a user with the same username
        user = get_user_model().objects.create_user(**self.user_data)
        self.user_data['email'] = 'another@example.com'
        serializer = UserAccountSerializer(data=self.user_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)


class UserProfileSerializerTestCase(TestCase):
    def setUp(self):
        self.user_account = get_user_model().objects.create_user(email='testuser@example.com', username='testuser', password='testpassword')
        self.user_profile_data = {
            'user': self.user_account.pk,
            'name': 'Test',
            'last_name': 'User',
            'status': 'Test Status',
            'bio': 'Test Bio',
            'location': 'Test Location'
        }

    def test_valid_user_profile_serializer(self):
        serializer = UserProfileSerializer(data=self.user_profile_data)
        self.assertTrue(serializer.is_valid())
        user_profile = serializer.save()
        self.assertEqual(user_profile.user, self.user_account)
        self.assertEqual(user_profile.name, self.user_profile_data['name'])
        self.assertEqual(user_profile.last_name, self.user_profile_data['last_name'])
        self.assertEqual(user_profile.status, self.user_profile_data['status'])
        self.assertEqual(user_profile.bio, self.user_profile_data['bio'])
        self.assertEqual(user_profile.location, self.user_profile_data['location'])

    def test_nonexistent_user_user_profile_serializer(self):
        # provide a user that doesn't exist in the db
        self.user_profile_data['user'] = 99999
        serializer = UserProfileSerializer(data=self.user_profile_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)

    def test_existing_friends_user_profile_serializer(self):
        # create a user profile instance
        user_profile = UserProfile.objects.create(user=self.user_account)
        # add another user profile as a friend
        friend_profile = UserProfile.objects.create(user=get_user_model().objects.create_user(email='friend@example.com', username='frienduser', password='friendpassword'))
        self.user_profile_data['friends'] = [friend_profile.pk]
        serializer = UserProfileSerializer(instance=user_profile, data=self.user_profile_data)


User = get_user_model()

class AuthenticationTest(APITestCase):
    
    def setUp(self):
        self.username = "testuser"
        self.password = "testpass"
        self.email = 'test@email.com'
        self.user = User.objects.create_user(
            username=self.username, password=self.password, email=self.email
        )
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh_token.access_token)

    def test_my_token_obtain_pair_view(self):
        url = reverse("token_obtain_pair")
        data = {
            "username": self.username,
            "password": self.password,
            "email": self.email

        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_register_filter_api_view_with_authenticated_user(self):
        url = reverse("register-filter")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), User.objects.all().count())

    def test_register_filter_api_view_with_anonymous_user(self):
        url = reverse("register-filter")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
