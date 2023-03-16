from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an Emaill address")
        if not username :
            raise ValueError("Users must have an Username")
        user  = self.model(
                email=self.normalize_email(email),
                username=username
            )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
                email=self.normalize_email(email),
                password=password,
                username=username,
            )
        user.is_admin = True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user

class UserAccount(AbstractBaseUser, PermissionsMixin):
    alphanumeric_underscore = RegexValidator(r'^[0-9a-zA-z_]+$', 'Only alphanumeric characters and underscore are allowed')

    username = models.CharField(max_length=30, unique=True, validators=[alphanumeric_underscore])
    email = models.EmailField(verbose_name="email", max_length=100, unique=True)

    last_login=models.DateTimeField(verbose_name="last_login",auto_now=True)
    date_joined = models.DateField(auto_now_add=True, verbose_name="date_joined")
    
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='user_accounts',
        blank=True,
        verbose_name=_('groups'),
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='user_accounts',
        blank=True,
        verbose_name=_('user permissions'),
        help_text=_('Specific permissions for this user.'),
    )

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    def has_perm(self, perm, obj=None):
        return self.is_admin
    def has_module_perms(self, app_label ):
        return True

class UserProfile(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-z]+$', 'Only alphanumeric characters are allowed')
    
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, primary_key=True, related_name='profile')

    name = models.CharField(max_length=100, validators=[alphanumeric], blank=True, null=True)
    last_name = models.CharField(max_length=100, validators=[alphanumeric], blank=True, null=True)

    status = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    
    profile_img = models.ImageField(upload_to='profile_pics', default = 'profile_pics/default_profile.jpg')
    background_img = models.ImageField(upload_to='background_pics', default = 'background_pics/default_bg.jpg')
    location = models.CharField(max_length=100, null=True, blank=True)
    friends = models.ManyToManyField('self', blank=True, symmetrical=False)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.username} profile'
    
    def clean(self):
        super().clean()
        if self.friends.filter(pk=self.pk).exists() or self.friends.filter(pk=self.pk).exists():
            raise ValidationError('A user cannot be friend with themselves.')
    

