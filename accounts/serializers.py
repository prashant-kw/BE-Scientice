from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User

# Whitelist of roles permitted for self-registration by the public
PUBLIC_REGISTRATION_ROLES = [
    User.Role.DOCTOR,
    User.Role.RESEARCHER,
    User.Role.PHARMACIST,
    User.Role.STUDENT,
    User.Role.PATIENT,
    User.Role.OTHERS,
]

# Sensitive permission and status fields forbidden in non-admin write requests
PROTECTED_WRITE_FIELDS = {
    'is_staff',
    'is_superuser',
    'is_verified',
    'isStaff',
    'isSuperuser',
    'isVerified',
    'groups',
    'user_permissions',
}

def get_tokens_for_user(user):
    """
    Generate JWT access and refresh tokens for a user.

    NOTE ON CLAIMS:
    Display attributes (email, role, full_name, is_staff, is_superuser) are embedded in
    the access token strictly for client-side UI presentation and convenience.
    Backend authorization (e.g. `IsPortalAdmin`) MUST NEVER read privilege from token claims;
    it must always evaluate `request.user.is_staff`/`is_superuser` fetched live from the database.
    """
    refresh = RefreshToken.for_user(user)

    # Add display-only custom claims to the access token
    refresh['email'] = user.email
    refresh['fullName'] = user.full_name
    refresh['role'] = user.role
    refresh['is_staff'] = user.is_staff
    refresh['is_superuser'] = user.is_superuser

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }

class UserProfileSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source='full_name', required=False)
    licenseNumber = serializers.CharField(source='license_number', allow_blank=True, required=False)
    isStaff = serializers.BooleanField(source='is_staff', read_only=True)
    isSuperuser = serializers.BooleanField(source='is_superuser', read_only=True)
    isVerified = serializers.BooleanField(source='is_verified', read_only=True)
    dateJoined = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'fullName',
            'role',
            'isStaff',
            'isSuperuser',
            'licenseNumber',
            'specialty',
            'city',
            'state',
            'isVerified',
            'dateJoined',
        ]
        read_only_fields = ['id', 'email', 'isStaff', 'isSuperuser', 'isVerified', 'dateJoined']

    def validate(self, attrs):
        # Strict security check: reject any attempt to supply protected privilege fields
        initial_keys = set(self.initial_data.keys()) if hasattr(self, 'initial_data') and self.initial_data else set()
        forbidden_present = initial_keys.intersection(PROTECTED_WRITE_FIELDS)
        if forbidden_present:
            raise serializers.ValidationError({
                'security_violation': f"The following fields are strictly read-only and cannot be supplied: {', '.join(sorted(forbidden_present))}"
            })

        # Disallow changing role to admin via profile update
        if 'role' in attrs and attrs['role'] == User.Role.ADMIN and not (self.instance and self.instance.is_staff):
            raise serializers.ValidationError({
                'role': "Administrative roles cannot be self-assigned."
            })

        return attrs

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    fullName = serializers.CharField(max_length=255, required=False)
    full_name = serializers.CharField(max_length=255, required=False)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.DOCTOR)
    licenseNumber = serializers.CharField(max_length=100, allow_blank=True, required=False, default='')
    license_number = serializers.CharField(max_length=100, allow_blank=True, required=False, default='')
    specialty = serializers.CharField(max_length=100, allow_blank=True, required=False, default='')
    city = serializers.CharField(max_length=100, allow_blank=True, required=False, default='')
    state = serializers.CharField(max_length=100, allow_blank=True, required=False, default='')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email address already exists.')
        return value.lower()

    def validate(self, attrs):
        # 1. Strict security check: Reject request immediately if protected privilege keys are present
        initial_keys = set(self.initial_data.keys()) if hasattr(self, 'initial_data') and self.initial_data else set()
        forbidden_present = initial_keys.intersection(PROTECTED_WRITE_FIELDS)
        if forbidden_present:
            raise serializers.ValidationError({
                'security_violation': f"Field '{list(forbidden_present)[0]}' is restricted and cannot be specified during registration."
            })

        # 2. Strict role whitelist check: Disallow self-registration with non-public roles (e.g. admin)
        role = attrs.get('role', User.Role.DOCTOR)
        if role not in PUBLIC_REGISTRATION_ROLES:
            raise serializers.ValidationError({
                'role': f"Registration with role '{role}' is not permitted. Please select a valid professional role."
            })

        # 3. Normalize fullName / full_name
        full_name = attrs.get('fullName') or attrs.get('full_name')
        if not full_name:
            raise serializers.ValidationError({'fullName': 'Full name is required.'})
        attrs['full_name'] = full_name

        # 4. Normalize licenseNumber / license_number
        license_num = attrs.get('licenseNumber') or attrs.get('license_number', '')
        attrs['license_number'] = license_num

        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        full_name = validated_data['full_name']
        role = validated_data.get('role', User.Role.DOCTOR)
        license_number = validated_data.get('license_number', '')
        specialty = validated_data.get('specialty', '')
        city = validated_data.get('city', '')
        state = validated_data.get('state', '')

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            license_number=license_number,
            specialty=specialty,
            city=city,
            state=state,
        )

        tokens = get_tokens_for_user(user)
        return {
            'user': UserProfileSerializer(user).data,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        }

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')

        if not email or not password:
            raise serializers.ValidationError('Both email and password are required.')

        user = authenticate(email=email, password=password)
        if not user:
            if not User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError('No account found with this email address.')
            raise serializers.ValidationError('Invalid password. Please check your credentials.')

        if not user.is_active:
            raise serializers.ValidationError('This account has been deactivated.')

        tokens = get_tokens_for_user(user)
        attrs['user_obj'] = user
        return {
            'user': UserProfileSerializer(user).data,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            '_user_obj': user,
        }
