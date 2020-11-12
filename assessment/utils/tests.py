import json

from rest_framework.test import APIClient
from django.utils.encoding import force_text
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status


class TestsMixin(object):
    """
    base for API tests:
        * easy request calls, f.e.: self.post(url, data), self.get(url)
        * easy status check, f.e.: self.post(url, data, status_code=200)
    """
    EMAIL = "hellobob@world.com"
    PASSWORD = 'check-pass'
    FULL_NAME = "hello bob"
    FIRST_NAME = "hello"
    LAST_NAME = "bob"
    USERNAME = "hello_bob"

    def send_request(self, request_method, *args, **kwargs):
        request_func = getattr(self.client, request_method)
        status_code = None
        if 'content_type' not in kwargs and request_method != 'get':
            kwargs['content_type'] = 'application/json'
        if 'data' in kwargs and request_method != 'get' and kwargs['content_type'] == 'application/json':
            data = kwargs.get('data', '')
            kwargs['data'] = json.dumps(data)  # , cls=CustomJSONEncoder
        if 'status_code' in kwargs:
            status_code = kwargs.pop('status_code')

        # check_headers = kwargs.pop('check_headers', True)
        if hasattr(self, 'token'):
            kwargs['HTTP_AUTHORIZATION'] = 'Token %s' % self.token

        self.response = request_func(*args, **kwargs)
        is_json = bool(
            [x for x in self.response._headers['content-type'] if 'json' in x])

        self.response.json = {}
        if is_json and self.response.content:
            self.response.json = json.loads(force_text(self.response.content))

        if status_code:
            self.assertEqual(self.response.status_code, status_code)

        return self.response

    def post(self, *args, **kwargs):
        return self.send_request('post', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.send_request('get', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.send_request('patch', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.send_request('delete', *args, **kwargs)

    def init(self):
        settings.DEBUG = True
        # self.client = APIClient()
        self.login_url = reverse('users:user-login')
        # self.logout_url = reverse('rest_logout')
        # self.password_change_url = reverse('rest_password_change')
        # self.register_url = reverse('rest_register')
        # self.password_reset_url = reverse('rest_password_reset')
        # self.user_url = reverse('rest_user_details')
        # self.verify_email_url = reverse('rest_verify_email')
        # self.fb_login_url = reverse('fb_login')

    def _login(self):
        payload = {
            "email": self.EMAIL,
            "password": self.PASSWORD
        }
        return self.post(self.login_url, data=payload, status_code=status.HTTP_200_OK)

    # def _logout(self):
    #     self.post(self.logout_url, status=status.HTTP_200_OK)

    # TODO: update create  user
    # def create_user(self):
    #     user_data = {"full_name": self.FULL_NAME}
    #     user = get_user_model().objects.create_user(email=self.EMAIL, password=self.PASSWORD, **user_data)
    #     return user
