from rest_framework import serializers

from apps.users.models import User


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(min_length=6,
                                     style={'input_type': 'password'}, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'}, required=True)

    def validate(self, attrs):
        email = attrs.get('email')

        if User.objects.filter(email__iexact=email).exists():
            password = attrs.get('password')
            user = User.objects.filter(email__iexact=email).first()
            if user.check_password(password):
                return attrs
        raise serializers.ValidationError({'message': 'Invalid credentials'})
