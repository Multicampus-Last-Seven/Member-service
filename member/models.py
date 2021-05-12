from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class Serials(models.Model):
    objects = models.Manager
    num = models.CharField(max_length=255, primary_key=True)
    name = models.ForeignKey('Member', related_name='member', on_delete=models.CASCADE,
     db_column='member_id', blank=True, null=True, default='null')


class MemberManager(BaseUserManager):
    def _create_user(self, email, password, **etc):
        if not email: raise ValueError('Members must have an email.')

        email = self.normalize_email(email)
        user = self.model(email=email, **etc)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **etc):
        etc.setdefault('is_superuser', False)
        return self._create_user(email, password, **etc)
    
    def create_superuser(self, email, password=None, **etc):
        etc.setdefault('is_staff', True)
        etc.setdefault('is_superuser', True)
        if not etc['is_superuser']: raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **etc)

    
class Member(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=191, primary_key=True)
    name = models.CharField(max_length=191)
    road_addr = models.CharField(max_length=191)
    detail_addr = models.CharField(max_length=191)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = MemberManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
    
    def get_short_name(self):
        return self.email

    class Meta:
        verbose_name = 'users'