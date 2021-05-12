from rest_framework import serializers
from .models import Serials
from .serializers import SerialsSerializer, MemberCreateSerializer, EmailUniqueCheckSerializer
from .serializers import MemberLoginSerializer, UseridUniqueCheckSerializer
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
    if serializer.is_valid():
        serializer.save()
        response = {'success': True}
        response['data'] = serializer.data
        return Response(data=response, status=201)

    response = {'success': False}
    response['data'] = serializer.errors
    return Response(data=response, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_email(request):
    serializer = EmailUniqueCheckSerializer(data=request.data)
    if serializer.is_valid(): return Response(data={'success': True}, status=201)
    return Response(data={'success': False}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_userid(request):
    serializers = UseridUniqueCheckSerializer(data=request.data)
    if serializers.is_valid(): return Response(data={'success': True}, status=201)
    return Response(data={'success': False}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if len(request.data) > 2:
        return Response({'success': False, 'detail': 'Too many data'}, status=400)

    serializer = MemberLoginSerializer(data=request.data)
    if not serializer.is_valid() or serializer.validated_data['userid'] == 'None':
        return Response({'success': False, 'detail': 'Email or password is wrong'}, status=400)
    
    response = {
        'success': True,
        'token': serializer.data['token']
    }

    return Response(response, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_serial(request, pk):
    if len(request.data) > 2: return Response({'success': False, 'detail': 'Too many data'}, status=400)
    try:
        result = Serials.objects.filter(pk=pk, name__isnull=True)
        result.update(name=request.data['userid'])
        return Response({'success': True}, status=201)

    except:
        return Response({'success': False, 'detail': 'The serial number does not exist or is already registered'}, status=400)