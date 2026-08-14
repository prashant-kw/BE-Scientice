from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from common.models import TimeStampedModel

class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier for authentication.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.DOCTOR)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        DOCTOR = 'doctor', 'Physician / Doctor'
        RESEARCHER = 'researcher', 'Researcher / Scientist'
        PHARMACIST = 'pharmacist', 'Pharmacist'
        STUDENT = 'student', 'Medical Student'
        PATIENT = 'patient', 'Patient / Caregiver'
        OTHERS = 'others', 'Others'

    username = None  # Remove username field
    email = models.EmailField('email address', unique=True)
    full_name = models.CharField('full name', max_length=255)
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.DOCTOR,
        help_text='Professional role or identity badge (Display only; authorization relies on is_staff/is_superuser)'
    )
    license_number = models.CharField(
        'medical council registration number',
        max_length=100,
        blank=True,
        default='',
        help_text='Registration or license number (optional for non-clinical roles)'
    )
    specialty = models.CharField(
        'medical specialty',
        max_length=100,
        blank=True,
        default='',
        help_text='Primary medical specialty or practice focus'
    )
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    is_verified = models.BooleanField(
        'verified professional',
        default=False,
        help_text='Designates whether this user has been verified by the medical council / editorial board.'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name or self.email} ({self.get_role_display()})"
