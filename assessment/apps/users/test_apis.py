from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIRequestFactory

from utils.tests import TestsMixin
from django.urls import reverse


User = get_user_model()


class APIBasicTests(TestsMixin, TestCase):
    """
    - user login signup url: defined
    - custom registration/signup: backend defined
    """

    # urls = 'tests.urls'
    FULL_NAME = "hello bob"
    FIRST_NAME = "hello"
    LAST_NAME = "bob"
    USERNAME = 'hello_bob'
    EMAIL = "hellobob@world.com"
    PASSWORD = 'check-pass'
    NEW_PASS = 'new-check-pass'
    # REGISTRATION_VIEW = 'rest_auth.runtests.RegistrationView'

    REGISTRATION_DATA = {
        "email": EMAIL,
        "password": PASSWORD,
        "first_name": PASSWORD,
        "last_name": FULL_NAME
    }

    def setUp(self):
        # self.init()
        self.init_data()

    def init_data(self):
        settings.DEBUG = True
        self.login_url = reverse('users:user-login')
        self.register_url = reverse('users:user-signup')
        # self.user_url = reverse('rest_user_details')

    def _login(self):
        payload = {
            "email": self.EMAIL,
            "password": self.PASSWORD
        }
        self.post(self.login_url, data=payload, status_code=status.HTTP_200_OK)

    def create_user(self):
        user_data = {"first_name": self.FIRST_NAME, "last_name": self.LAST_NAME}
        user = get_user_model().objects.create_user(email=self.EMAIL, username=self.EMAIL, password=self.PASSWORD,
                                                    **user_data)
        return user

    # def _logout(self):
    #     self.post(self.logout_url, status=status.HTTP_200_OK)

    def _generate_uid_and_token(self, user):
        result = {}
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode

        result['uid'] = urlsafe_base64_encode(force_bytes(user.pk))
        result['token'] = default_token_generator.make_token(user)
        return result

    def test_login_failed_email_validation(self):
        payload = {
            "email": "",
            "password": self.PASSWORD
        }

        resp = self.post(self.login_url, data=payload, status_code=400)
        self.assertEqual(resp.json['email'][0], 'This field may not be blank.')

    def test_login_failed_password_validation(self):
        payload = {
            "email": self.EMAIL,
            "password": ""
        }

        resp = self.post(self.login_url, data=payload, status_code=400)
        self.assertEqual(resp.json['password'][0], 'This field may not be blank.')

    def test_login_with_email(self):
        payload = {
            "email": self.EMAIL,
            "password": self.PASSWORD
        }
        # there is no users in db so it should throw error (400)
        self.post(self.login_url, data=payload, status_code=400)

        # create user
        self.create_user()
        self.post(self.login_url, data=payload, status_code=200)

    def test_login_with_email_upper_lower(self):
        payload = {
            "email": self.EMAIL,
            "password": self.PASSWORD
        }
        # there is no users in db so it should throw error (400)
        self.post(self.login_url, data=payload, status_code=400)

        # create user
        user = self.create_user()

        # test auth by email
        payload = {
            "email": self.EMAIL.lower(),
            "password": self.PASSWORD
        }
        self.post(self.login_url, data=payload, status_code=200)

        payload = {
            "email": self.EMAIL.upper(),
            "password": self.PASSWORD
        }
        self.post(self.login_url, data=payload, status_code=200)

        # TODO: test inactive user
        # user.is_active = False
        # user.save()
        # self.post(self.login_url, data=payload, status_code=401)

    def test_login_with_incorrect_email(self):
        payload = {
            "email": self.EMAIL,
            "password": self.PASSWORD
        }
        # there is no users in db so it should throw error (400)
        self.post(self.login_url, data=payload, status_code=400)

        # create user
        user = self.create_user()
        payload = {
            "email": 't' + self.EMAIL,
            "password": self.PASSWORD
        }
        self.post(self.login_url, data=payload, status_code=400)

    def test_login_with_incorrect_password(self):
        payload = {
            "email": self.EMAIL,
            "password": self.PASSWORD
        }
        # there is no users in db so it should throw error (400)
        self.post(self.login_url, data=payload, status_code=400)

        # create user
        user = self.create_user()
        payload = {
            "email": self.EMAIL,
            "password": 'p' + self.PASSWORD
        }
        self.post(self.login_url, data=payload, status_code=400)

    def test_login_with_no_data(self):
        payload = {
            "email": self.EMAIL,
            "password": self.PASSWORD
        }
        # there is no users in db so it should throw error (400)
        self.post(self.login_url, data=payload, status_code=400)

        self.post(self.login_url, data={}, status_code=400)

    def test_registration(self):
        user_count = get_user_model().objects.all().count()

        # test empty payload
        self.post(self.register_url, data={}, status_code=400)

        data = self.REGISTRATION_DATA.copy()

        result = self.post(self.register_url, data=data, status_code=201)

        self.assertEqual(get_user_model().objects.all().count(), user_count + 1)

        new_user = get_user_model().objects.latest('id')
        self.assertEqual(new_user.email, self.REGISTRATION_DATA['email'])

    def test_registration_without_password(self):
        data = self.REGISTRATION_DATA.copy()
        data.pop('password')

        self.post(self.register_url, data=data, status_code=400)

    def test_registration_without_email(self):
        data = self.REGISTRATION_DATA.copy()
        data.pop('email')

        self.post(self.register_url, data=data, status_code=400)

    def test_registration_first_name(self):
        data = self.REGISTRATION_DATA.copy()
        data.pop('first_name')

        self.post(self.register_url, data=data, status_code=400)

    def test_registration_last_name(self):
        data = self.REGISTRATION_DATA.copy()
        data.pop('last_name')

        self.post(self.register_url, data=data, status_code=400)
