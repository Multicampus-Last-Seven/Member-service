from django.contrib.auth.models import update_last_login
from django.core.checks.messages import Error
from django.db.models import fields
from rest_framework import serializers
from .models import IoT, Member
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from rest_framework_jwt.settings import api_settings

class IoTSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IoT
        fields = ['num', 'location']

class MemberCreateSerializer(serializers.Serializer):
    userid = serializers.CharField(required=True, validators=[
        UniqueValidator(queryset=Member.objects.all())
    ])
    email = serializers.EmailField(required=True, validators=[
        UniqueValidator(queryset=Member.objects.all())
    ])
    name = serializers.CharField(required=True)
    road_addr = serializers.CharField(required=True)
    detail_addr = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        user = Member.objects.create(
            userid = validated_data['userid'],
            email = validated_data['email'],
            name = validated_data['name'],
            road_addr = validated_data['road_addr'],
            detail_addr = validated_data['detail_addr']            
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UseridUniqueCheckSerializer(serializers.Serializer):
    userid = serializers.CharField(required=True, validators=[
        UniqueValidator(queryset=Member.objects.all())
    ])

class EmailUniqueCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, validators=[
        UniqueValidator(queryset=Member.objects.all())
    ])

class MemberLoginSerializer(serializers.Serializer):
    userid = serializers.CharField(max_length=191)
    password = serializers.CharField(max_length=191, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        userid = data.get('userid', None)
        password = data.get('password', None)
        user = authenticate(userid=userid, password=password)

        if user is None: return {'userid': 'None'}

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
        
        return {'userid': user.userid, 'token': jwt_token}

class MemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['name', 'password', 'road_addr', 'detail_addr', 'email']
        extra_kwargs = {
            'name': {'required': False},
            'password': {'required': False},
            'road_addr': {'required': False},
            'detail_addr': {'required': False},
            'email': {'required': False}
        }
    
    def validate(self, data):
        email = data.get('email', None)
        if email is not None:
            result = Member.objects.filter(email=email).count()
            if result != 0: return {'count': 1}
        return {'count': 0}
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.road_addr = validated_data.get('road_addr', instance.road_addr)
        instance.detail_addr = validated_data.get('detail_addr', instance.detail_addr)
        if 'email' in validated_data.keys():
            instance.email = validated_data['email']
            instance.is_active = False

        if 'password' in validated_data.keys():
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance

class MemberRegisterIoTSeriallizer(serializers.ModelSerializer):
    class meta:
        model = IoT
        fields = ['name', 'is_alive', 'location']
        extra_kwargs = {
            'name': {'required': False},
            'is_alive': {'required': False},            
            'location': {'required': False},
        }
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('userid', instance.name)
        instance.is_alive = True
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance
    