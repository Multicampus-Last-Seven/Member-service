from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class Serials(models.Model):
    objects = models.Manager
    num = models.CharField(max_length=255, primary_key=True)
    name = models.ForeignKey('Member', related_name='member', on_delete=models.CASCADE,
     db_column='member_name', blank=True, null=True, default='null')

class MemberManager(BaseUserManager):
    def _create_user(self, userid, email, password, **etc):
        if not userid: raise ValueError('Members must have an email.')

        email = self.normalize_email(email)
        user = self.model(userid=userid, email=email, **etc)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, userid, email, password=None, **etc):
        etc.setdefault('is_superuser', False)
        return self._create_user(userid, email, password, **etc)
    
    def create_superuser(self, userid, email, password=None, **etc):
        etc.setdefault('is_staff', True)
        etc.setdefault('is_superuser', True)
        if not etc['is_superuser']: raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(userid, email, password, **etc)

    
class Member(AbstractBaseUser, PermissionsMixin):
    userid = models.CharField(max_length=191, primary_key=True)
    email = models.EmailField(max_length=191, unique=True)
    name = models.CharField(max_length=191)
    road_addr = models.CharField(max_length=191)
    detail_addr = models.CharField(max_length=191)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = MemberManager()

    USERNAME_FIELD = 'userid'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.userid
    
    def get_short_name(self):
        return self.userid

    class Meta:
        verbose_name = 'users'