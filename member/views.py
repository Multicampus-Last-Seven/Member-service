from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, status
from rest_framework import response
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
from random import randint

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serialsList(request):
    serials = Serials.objects.all()    
    serializer = SerialsSerializer(instance=serials, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = MemberCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        response = {'success': True}
        response['data'] = serializer.data
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

    response = {'success': False}
    response['detail'] = serializer.errors
    return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_email(request):
    serializer = EmailUniqueCheckSerializer(data=request.data)
    if serializer.is_valid(): return Response(data={'success': True}, status=status.HTTP_200_OK)
    return Response(data={'success': False}, status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_userid(request):
    serializers = UseridUniqueCheckSerializer(data=request.data)
    if serializers.is_valid(): return Response(data={'success': True}, status=status.HTTP_200_OK)
    return Response(data={'success': False}, status=status.HTTP_409_CONFLICT)

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
        return Response({'success': False, 'detail': 'Too many data sent'},
         status=status.HTTP_400_BAD_REQUEST)

    serializer = MemberLoginSerializer(data=request.data)
    if not serializer.is_valid() or serializer.validated_data['userid'] == 'None':
        return Response(
            {'success': False, 'detail': 'ID or password is wrong'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    response = {
        'success': True,
        'token': serializer.data['token']
    }

    return Response(response, status=status.HTTP_200_OK)

@api_view(['POST', 'DELETE'])
#@permission_classes([AllowAny])
def serial_view(request, userid, serialid):
    if request.method == 'POST':
        if len(request.data) > 2:
            return Response({'success': False, 'detail': 'Too many data sent'}, 
             status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = Serials.objects.filter(pk=serialid, name__isnull=True)
            result.update(name=request.data['userid'])
            return Response({'success': True}, status=status.HTTP_200_OK)

        except:
            return Response(
                {'success': False, 'detail': 'The serial number does not exist or is already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    else:
        if len(request.data) > 2:
            return Response({'success': False, 'detail': 'Too many data sent'}, 
             status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = Serials.objects.filter(pk=serialid, name=userid)
        result.update(name='null')
        return Response({'success': True}, status=status.HTTP_200_OK)
    
    except:
        return Response(
            {'success': False,
             'detail': '{0} or {1} does not exist'.format(userid, serialid)
            }
        )

@api_view(['PATCH', 'DELETE'])
@permission_classes([AllowAny])
def update_user(request, userid):
    if request.method == 'PATCH':
        if len(request.data) > 6: return Response({'success': False, 'detail': 'Too many data sent'},
        status=status.HTTP_400_BAD_REQUEST)
        
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
                return Response({'success': True}, status=status.HTTP_200_OK)
            
            else:
                return Response({'success': False, 'detail': 'email already exists'},
                 status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({
                'success': False,
                'detail': 'Object does not exist'
            }, status = status.HTTP_400_BAD_REQUEST)
        
        except AttributeError:
            return Response({
                'success': False,
                'detail': 'Unvalid input'
            }, status = status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response({
            'sucess': False,
            'detail': 'Unknown error'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        if len(request.data) > 2: return Response({'success': False, 'detail': 'Too many data sent'},
        status=status.HTTP_400_BAD_REQUEST)

        try:
            result = Member.objects.filter(pk=userid)
            result.delete()
            return Response({'success': True}, status=status.HTTP_200_OK)
        
        except:
            return Response({
                'success': False,
                'detail': 'Object does not exist'
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def find_userid(request):
    return Response({'success': True, 'detail': 'hello'}, status=status.HTTP_200_OK)
    """
    if len(request.data) > 2:
        response = {'success': False, 'detail': 'Too many data sent'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        member = Member.objects.get(name=request.data['name'],
         email=request.data['email'])
        
        response = {'success': True, 'detail': {'userid': member.userid}}
        return Response(response, status=status.HTTP_200_OK)
    
    except:
        response = {'success': False, 'detail': 'not valid name or email'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    """


@api_view(['POST'])
@permission_classes([AllowAny])
def find_password(request):
    if len(request.data) > 2:
        response = {'success': False, 'detail': 'Too many data sent'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        member = Member.objects.filter(pk=request.data['userid'])
        if member.name != request.data['name'] or member.email != request.data['email']:
            response = {'success': False, 'detail': 'name or email is not correct'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        chars = [[str(i) for i in range(10)]]
        chars.append(['!', '@', '#', '$', '%', '^', '&', '*'])
        chars.append([chr(i) for i in range(ord('a'), ord('z')+1)])
        pw = ''

        for _ in range(10):
            k = randint(0, len(chars)-1)
            th = randint(0, len(chars[k])-1)
            pw += chars[k][th]

        update_serializer = MemberUpdateSerializer()
        update_serializer.update(member, pw)

        message = render_to_string('member/new_password.html', {
            'user': member,
            'uid': urlsafe_base64_encode(force_bytes(member.userid)).encode().decode(),
            'password': pw
        })

        mail_subject = "{0}'s new password"
        user_email = member.email
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.send()

        response = {'success': True}
        return Response(response, status=status.HTTP_200_OK)

    except:
        response = {'success': False, 'detail': 'No userid'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
