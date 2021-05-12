from rest_framework import serializers
from .models import Serials
from .serializers import SerialsSerializer, MemberCreateSerializer, EmailUniqueCheckSerializer
from .serializers import MemberLoginSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


@api_view(['GET'])
def serialsList(request):
    serials = Serials.objects.all() 
    
    serializer = SerialsSerializer(instance=serials, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = MemberCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(data=serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_email(request):
    serializer = EmailUniqueCheckSerializer(data=request.data)
    if serializer.is_valid(): return Response(data={'available': True}, status=201)
    return Response(data={'available':False}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method != 'POST':
        return Response({'success': False, 'message': 'Request error'}, status=400)

    if len(request.data) > 2:
        return Response({'success': False, 'message': 'Too many data'}, status=400)

    serializer = MemberLoginSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True) or serializer.validated_data['email'] == 'None':
        return Response({'success': False, 'message': 'Email or password is wrong'}, status=400)
    
    response = {
        'success': True,
        'token': serializer.data['token']
    }

    return Response(response, status=201)
