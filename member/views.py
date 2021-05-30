from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, status
from .models import Member, IoT
from .serializers import IoTSerializer, MemberCreateSerializer, EmailUniqueCheckSerializer
from .serializers import MemberLoginSerializer, UseridUniqueCheckSerializer, MemberUpdateSerializer
from .serializers import  MemberRegisterIoTSeriallizer
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
def iots_list(request):
    iot = IoT.objects.all()    
    serializer = IoTSerializer(instance=iot, many=True)
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
    member = None
    if not serializer.is_valid() or serializer.validated_data['userid'] == 'None':
        response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(serializer.error_messages).build()
        return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    member = Member.objects.get(userid=request.data['userid'])
    iots = None
    try:
        iots = IoT.objects.filter(name=member.userid).all()
    except: pass

    additional_data = []
    if iots is not None:
        for iot in iots:
            iot_dict = IoTSerializer(instance=iot).data
            additional_data.append({
                "serialNumber": iot_dict['num'],
                "location": iot_dict['location']
            })

    response_data = {
        'name': member.name,
        'road_addr': member.road_addr,
        'detail_addr': member.detail_addr,
        "iots": additional_data
    }
    response = ResponseMessage().add(SUCCESS_RESPONSE).add(serializer.data).add(response_data).build()
    print(response)
    return Response(data=response, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def iot_alive_view(request, serialid):
    try:
        iots = IoT.objects.filter(pk=serialid)
        if iots.is_alive == True:
            msg = {'detail': 'It is already alive'}
            response = Response().add(NOT_SUCCESS_RESPONSE).add(msg).build()
            return Response(data=response, status=status.HTTP_409_CONFLICT)
        
        iots.update(is_alive=True)
        return Response(data=SUCCESS_RESPONSE, status=status.HTTP_200_OK)

    except:
        return Response(data=NOT_SUCCESS_RESPONSE, status=status.HTTP_404_NOT_FOUND)
        
# The member registers or unregisters serial number of raspberry pi
@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def iot_view(request, userid):
    if request.method == 'POST':
        if len(request.data) > 3:
            response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            exist = IoT.objects.filter(name=userid).exists()
            if exist:
                iots = IoT.objects.filter(name=userid).all()
                iots.update(name=None)
            
            iots = request.data['iots']
            for iot in iots:
                if not iot['serialNumber']: continue
                new_iot = IoT.objects.filter(num=iot["serialNumber"])
                new_iot.update(name=userid, is_alive=True, location=iot['location'])

            return Response(data=SUCCESS_RESPONSE, status=status.HTTP_202_ACCEPTED)
                
        except :
            response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
            return Response(data=response, status=status.HTTP_404_NOT_FOUND)
    
    else:
        if len(request.data) > 2:
            response = ResponseMessage().add(SUCCESS_RESPONSE).add(TOO_MANY_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            result = IoT.objects.filter(pk=request.data, name=userid)
            result.update(name='null', is_alive=False)
            return Response(SUCCESS_RESPONSE, status=status.HTTP_200_OK)
        
        except:
            response = ResponseMessage().add(NOT_SUCCESS_RESPONSE).add(UNVALID_DATA).build()
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'DELETE'])
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