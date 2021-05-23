from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from .models import Member, Serials
from .serializers import SerialsSerializer, MemberCreateSerializer, EmailUniqueCheckSerializer
from .serializers import MemberLoginSerializer, UseridUniqueCheckSerializer, MemberUpdateSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from .token import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.shortcuts import render
from .simple_utils import get_new_password
from .messages import NOT_SUCCESS_RESPONSE, SUCCESS_RESPONSE, ResponseMessage, TOO_MANY_DATA
from .messages import UNVALID_DATA, ALREADY_EXIST

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serialsList(request):
    serials = Serials.objects.all()    
    serializer = SerialsSerializer(instance=serials, many=True)
    detail = {'detail': serializer.data}
    response = ResponseMessage().add(SUCCESS_RESPONSE).add(detail).build()
    return Response(data=response, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = MemberCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        response = ResponseMessage().add(SUCCESS_RESPONSE).add(serializer.data).build()
        user = Member.objects.get(pk=request.data['userid'])
        current_site = get_current_site(request) 
        message = render_to_string('member/activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.userid)).encode().decode(),
            'token': account_activation_token.make_token(user),
        })

        mail_subject = "Verify your e-mail."
        user_email = user.email
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.send()
        return Response(data=response, status=status.HTTP_201_CREATED)

    detail = {'detail': serializer.errors}
    response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(detail).build()
    return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_email(request):
    serializer = EmailUniqueCheckSerializer(data=request.data)
    if serializer.is_valid(): return Response(data=SUCCESS_RESPONSE, status=status.HTTP_200_OK)
    return Response(data=NOT_SUCCESS_RESPONSE, status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_userid(request):
    serializers = UseridUniqueCheckSerializer(data=request.data)
    if serializers.is_valid(): return Response(data=SUCCESS_RESPONSE, status=status.HTTP_200_OK)
    return Response(data=NOT_SUCCESS_RESPONSE, status=status.HTTP_409_CONFLICT)

@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request, userid, token):
    uid = force_text(urlsafe_base64_decode(userid))
    try:
        user = Member.objects.get(pk=uid)
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, 'member/activation_success.html')
        else:
            return render(request, 'member/activation_fail.html')
    
    except:
        return render(request, 'member/activation_fail.html')

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if len(request.data) > 2:
        response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    serializer = MemberLoginSerializer(data=request.data)
    if not serializer.is_valid() or serializer.validated_data['userid'] == 'None':
        response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    
    token = {'token': serializer.data['token']}
    response = ResponseMessage().add(SUCCESS_RESPONSE).add(token).build()
    return Response(data=response, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def serial_alive_view(request, serialid):
    exist = Serials.objects.filter(pk=serialid).count()
    if exist > 0:
        response = Response().add(NOT_SUCCESS_RESPONSE).add(ALREADY_EXIST).build()
        return Response(data=response, status=status.HTTP_409_CONFLICT)
        
    return Response(data=SUCCESS_RESPONSE, status=status.HTTP_200_OK)

# The member registers or unregisters serial number of raspberry pi
@api_view(['POST', 'DELETE'])
def serial_view(request, userid, serialid):
    if request.method == 'POST':
        if len(request.data) > 2:
            response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = Serials.objects.filter(pk=serialid, name__isnull=True)
            result.update(name=request.data['userid'])
            return Response(SUCCESS_RESPONSE, status=status.HTTP_200_OK)

        except:
            response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        if len(request.data) > 2:
            response = ResponseMessage().add(SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            result = Serials.objects.filter(pk=serialid, name=userid)
            result.update(name='null')
            return Response(SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        
        except:
            response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'DELETE'])
#@permission_classes([AllowAny])
def update_user(request, userid):
    if request.method == 'PATCH':
        if len(request.data) > 6: 
            response = ResponseMessage().add(SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        
        try:      
            result = Member.objects.get(userid=userid)
            update_serializer = MemberUpdateSerializer(instance=result, data=request.data)
            if update_serializer.is_valid() and update_serializer.validated_data['count'] == 0:
                if 'email' in request.data.keys():
                    current_site = get_current_site(request) 
                    message = render_to_string('member/activate_email.html', {
                        'user': result,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(result.userid)).encode().decode(),
                        'token': account_activation_token.make_token(result),
                    })

                    mail_subject = "Verify your e-mail."
                    user_email = result.email
                    email = EmailMessage(mail_subject, message, to=[user_email])
                    email.send()
                 

                update_serializer.update(result, request.data)   
                return Response(SUCCESS_RESPONSE, status=status.HTTP_200_OK)
            
            else:
                response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA)
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        except:
            response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        if len(request.data) > 2:
            response = ResponseMessage().add(SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = Member.objects.filter(pk=userid)
            result.delete()
            return Response(SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        
        except:
            response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def find_userid(request):
    if len(request.data) > 2:
        response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        member = Member.objects.get(
            name=request.data['name'],
            email=request.data['email']
        )
        
        detail = {'detail': {'userid': member.userid}}
        response = ResponseMessage().add(SUCCESS_RESPONSE).add(detail).build()
        return Response(data=response, status=status.HTTP_200_OK)
    
    except:
        response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def find_password(request):
    if len(request.data) > 3:
        response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        member = Member.objects.get(
            userid=request.data['userid'],
            name=request.data['name'],
            email=request.data['email']
        )
     
        pw = get_new_password()
        password = {'password': pw}
        update_serializer = MemberUpdateSerializer()
        update_serializer.update(member, password)

        message = render_to_string('member/new_password.html', {
            'user': member,
            'password': pw
        })

        mail_subject = "{0}'s new password".format(member.userid)
        user_email = member.email
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.send()

        return Response(SUCCESS_RESPONSE, status=status.HTTP_200_OK)

    except:
        response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
