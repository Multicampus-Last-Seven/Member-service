from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from .models import Serials, Member
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings


class SerialsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Serials
        fields = ['num']


class MemberCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, validators=[
        UniqueValidator(queryset=Member.objects.all())
    ])
    name = serializers.CharField(required=True)
    road_addr = serializers.CharField(required=True)
    detail_addr = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        user = Member.objects.create(
            email = validated_data['email'],
            name = validated_data['name'],
            road_addr = validated_data['road_addr'],
            detail_addr = validated_data['detail_addr']            
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class EmailUniqueCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, validators=[
        UniqueValidator(queryset=Member.objects.all())
    ])


class MemberLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)
        print(data)
        user = authenticate(email=email, password=password)

        if user is None: return {'email': 'None'}

        try:
            JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
            JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        
        except Member.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        
        return {'email': user.email, 'token': jwt_token}