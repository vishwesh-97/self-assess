from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from apps.users.models import User
from apps.users.serializers import SignupSerializer, LoginSerializer


class SignupView(generics.CreateAPIView):
    """
    Sign up view.
    """
    authentication_classes = [AllowAny]
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        # performing check for existing user with same email
        if User.objects.filter(email__iexact=email).exists():
            data = {
                'success': False,
                'message': 'User with this email already exists.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': email,
            'password': password
        }
        user = User.objects.create_user(**data)

        resp_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        }

        return Response(resp_data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """
    Login view
    """
    authentication_classes = [AllowAny]
    serializer_class = LoginSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user_obj = User.objects.filter(email__iexact=email).first()
        token = Token.objects.get_or_create(user=user_obj)[0]

        resp_data = {
            'user': {
                'user_id': user_obj.id,
                'email': user_obj.email,
            },
            'token': token.key,
            'message': 'login successful'
        }
        return Response(resp_data, status=status.HTTP_200_OK)
