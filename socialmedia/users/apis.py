from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from django.core.validators import MinLengthValidator
from .validators import number_validator, special_char_validator, letter_validator
from socialmedia.users.models import BaseUser, Profile
from socialmedia.api.mixins import ApiAuthMixin
from socialmedia.users.selectors import get_profile
from socialmedia.users.services import register
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from drf_spectacular.utils import extend_schema


class ProfileApi(ApiAuthMixin, APIView):

    class OutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Profile
            fields = ("bio", "posts_count", "subscriber_count", "subscription_count")

    @extend_schema(responses=OutPutSerializer)
    def get(self, request):
        query = get_profile(user=request.user)
        return Response(self.OutPutSerializer(query, context={"request": request}).data)


class RegisterApi(APIView):

    # serialize request fields
    class InputRegisterSerializer(serializers.Serializer):
        email = serializers.EmailField(max_length=255)
        bio = serializers.CharField(max_length=1000, required=False)
        # use validators to validate password
        password = serializers.CharField(
            validators=[
                number_validator,
                letter_validator,
                special_char_validator,
                MinLengthValidator(limit_value=10),
            ]
        )
        confirm_password = serializers.CharField(max_length=255)

        # this method is called when is_valid method is called
        def validate_email(self, email):
            if BaseUser.objects.filter(email=email).exists():
                raise serializers.ValidationError("email Already Taken")
            return email

        # this method is called when is_valid method is called
        def validate(self, data):
            if not data.get("password") or not data.get("confirm_password"):
                raise serializers.ValidationError(
                    "Please fill password and confirm password"
                )

            if data.get("password") != data.get("confirm_password"):
                raise serializers.ValidationError(
                    "confirm password is not equal to password"
                )
            return data

    class OutPutRegisterSerializer(serializers.ModelSerializer):

        # call get_token method to get token
        token = serializers.SerializerMethodField("get_token")

        # serialize response fields
        class Meta:
            model = BaseUser
            fields = ("email", "token", "created_at", "updated_at")

        def get_token(self, user):
            data = dict()
            # set which token class you want to get
            token_class = RefreshToken

            # get token for user
            refresh = token_class.for_user(user)

            # set token in data
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data

    # when POST request is sent
    @extend_schema(request=InputRegisterSerializer, responses=OutPutRegisterSerializer)
    def post(self, request):
        serializer = self.InputRegisterSerializer(data=request.data)
        # if something is wrong with the data it will raise an exception
        serializer.is_valid(raise_exception=True)
        try:
            user = register(
                email=serializer.validated_data.get("email"),
                password=serializer.validated_data.get("password"),
                bio=serializer.validated_data.get("bio"),
            )
        except Exception as ex:
            return Response(f"Database Error {ex}", status=status.HTTP_400_BAD_REQUEST)
        return Response(
            self.OutPutRegisterSerializer(user, context={"request": request}).data
        )
