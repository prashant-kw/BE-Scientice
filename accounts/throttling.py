from rest_framework.throttling import AnonRateThrottle

class LoginRateThrottle(AnonRateThrottle):
    """
    IP-based rate throttle for the authentication login endpoint.
    Restricts rapid login requests from a single client IP (default: 5 requests / minute).

    SECURITY NOTE:
    IP-based rate throttling mitigates naive automated brute-force attacks.
    For production environments with distributed botnets or credential-stuffing against
    specific target emails from rotating IPs, consider adding `django-axes` or an account-level
    consecutive failure lockout counter as a production hardening follow-up.
    """
    scope = 'login'
