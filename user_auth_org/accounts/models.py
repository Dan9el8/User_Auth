from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, email, firstName, lastName, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not firstName:
            raise ValueError('The first name field must be set')
        if not lastName:
            raise ValueError('The last name field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, firstName=firstName, lastName=lastName, **extra_fields)
        user.set_password(password)
        user.clean()  # Call clean method for validation
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstName, lastName, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, firstName, lastName, password, **extra_fields)

class User(AbstractBaseUser):
    userId = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=30, null=False)
    lastName = models.CharField(max_length=30, null=False)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # Ensure this field is added

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName']

    def __str__(self):
        return self.email

    def clean(self):
        # Validate email uniqueness
        if User.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError("Email already exists")

class Organisation(models.Model):
    org_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User, related_name='organisations')
    
    def __str__(self):
        return self.name