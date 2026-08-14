from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from common.models import AuditLog
from .models import User

class AccountsSecurityAndRBACAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.profile_url = reverse('auth-profile')
        self.logout_url = reverse('auth-logout')

        self.user = User.objects.create_user(
            email='testdoctor@scientice.org',
            password='TestPassword123!',
            full_name='Dr. Test Doctor',
            role=User.Role.DOCTOR,
            specialty='Cardiology',
            city='Boston',
            state='MA',
        )

    # -------------------------------------------------------------
    # 1. Registration Security & Hard 400 Rejections
    # -------------------------------------------------------------
    def test_registration_with_admin_role_rejected_with_400(self):
        """
        Asserts that self-registration with role='admin' returns HTTP 400
        and does NOT silently downgrade or create an admin account.
        """
        payload = {
            'email': 'evil_admin@scientice.org',
            'password': 'Password@123',
            'fullName': 'Attacking Admin',
            'role': 'admin',
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)
        self.assertIn("Registration with role 'admin' is not permitted", str(response.data['role']))
        self.assertFalse(User.objects.filter(email='evil_admin@scientice.org').exists())

    def test_registration_with_is_staff_rejected_with_400(self):
        """
        Asserts that providing 'is_staff' in the registration payload triggers
        a hard HTTP 400 rejection instead of silently ignoring it.
        """
        payload = {
            'email': 'staff_attacker@scientice.org',
            'password': 'Password@123',
            'fullName': 'Staff Attacker',
            'role': 'doctor',
            'is_staff': True,
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('security_violation', response.data)
        self.assertFalse(User.objects.filter(email='staff_attacker@scientice.org').exists())

    def test_registration_with_is_superuser_rejected_with_400(self):
        """
        Asserts that providing 'is_superuser' in the registration payload triggers
        a hard HTTP 400 rejection.
        """
        payload = {
            'email': 'root_attacker@scientice.org',
            'password': 'Password@123',
            'fullName': 'Root Attacker',
            'role': 'doctor',
            'is_superuser': True,
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('security_violation', response.data)
        self.assertFalse(User.objects.filter(email='root_attacker@scientice.org').exists())

    def test_registration_valid_doctor_succeeds(self):
        """
        Asserts that legitimate doctor registration succeeds with HTTP 201,
        and is_staff/is_superuser remain strictly False.
        """
        payload = {
            'email': 'valid_doctor@scientice.org',
            'password': 'DoctorPassword@123',
            'fullName': 'Dr. Valid Doctor',
            'role': 'doctor',
            'specialty': 'Neurology',
            'licenseNumber': 'MCI-99881',
            'city': 'Mumbai',
            'state': 'Maharashtra',
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['role'], 'doctor')
        self.assertFalse(response.data['user']['isStaff'])
        self.assertFalse(response.data['user']['isSuperuser'])

        user_db = User.objects.get(email='valid_doctor@scientice.org')
        self.assertFalse(user_db.is_staff)
        self.assertFalse(user_db.is_superuser)

    # -------------------------------------------------------------
    # 2. Authentication & Audit Logging
    # -------------------------------------------------------------
    def test_failed_login_creates_audit_log(self):
        """
        Asserts that failed login attempts produce an immutable AuditLog row with LOGIN_FAILED.
        """
        initial_count = AuditLog.objects.count()
        payload = {
            'email': 'testdoctor@scientice.org',
            'password': 'WrongPassword123',
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        log = AuditLog.objects.latest('timestamp')
        self.assertEqual(log.action, AuditLog.Action.LOGIN_FAILED)
        self.assertEqual(log.actor_email, 'testdoctor@scientice.org')

    def test_successful_login_creates_audit_log_and_returns_claims(self):
        """
        Asserts that successful login produces an AuditLog row with LOGIN_SUCCESS.
        """
        initial_count = AuditLog.objects.count()
        payload = {
            'email': 'testdoctor@scientice.org',
            'password': 'TestPassword123!',
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        log = AuditLog.objects.latest('timestamp')
        self.assertEqual(log.action, AuditLog.Action.LOGIN_SUCCESS)
        self.assertEqual(log.user, self.user)

    # -------------------------------------------------------------
    # 3. Manager Defaults Invariants
    # -------------------------------------------------------------
    def test_create_user_defaults_to_doctor_role(self):
        """
        Asserts that creating a user programmatically via manager defaults role to DOCTOR.
        """
        user = User.objects.create_user(
            email='auto_user@scientice.org',
            password='Password@123',
            full_name='Auto User'
        )
        self.assertEqual(user.role, User.Role.DOCTOR)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_sets_admin_role_and_staff(self):
        """
        Asserts that creating a superuser via manager sets role=ADMIN, is_staff=True, is_superuser=True.
        """
        superuser = User.objects.create_superuser(
            email='new_super@scientice.org',
            password='AdminPassword@123',
            full_name='Super User'
        )
        self.assertEqual(superuser.role, User.Role.ADMIN)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
