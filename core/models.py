from typing import List

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager  # type: ignore
from django.contrib.auth.models import PermissionsMixin  # type: ignore
from django.db import models  # type: ignore

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _  # type: ignore


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        UserProfile.objects.create_profile(user=user)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), blank=False, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Un-select this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # type: List

    objects = UserManager()

    def get_short_name(self):
        return self.email.split('@')[0]

    def get_full_name(self):
        return self.email


class UserProfileQuerySet(models.QuerySet):
    pass


class UserProfileManager(models.Manager):
    def create_profile(self, user):
        profile = UserProfile()
        profile.user = user
        profile.save()
        return profile


class UserProfile(models.Model):
    """
    A model to hold the user account details (name, avatar, etc) for a particular user.
    """
    user = models.ForeignKey(to='core.User', null=False, blank=False)
    avatar = models.FileField(upload_to='avatars', max_length=250, null=True, blank=True)
    full_name = models.CharField(max_length=250)

    class Meta:
        pass

    def __repr__(self):
        avatar = None
        if self.avatar:
            avatar = self.avatar.name
        return 'UserProfile(user={user}, avatar={avatar}, full_name={full_name}'.format(
            user=self.user.email,
            avatar=avatar,
            full_name=self.full_name
        )

    def __str__(self):
        return 'Profile for User {email}'.format(email=self.user.email)

    objects = UserProfileManager.from_queryset(UserProfileQuerySet)()
