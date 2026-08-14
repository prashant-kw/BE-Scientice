from rest_framework.throttling import AnonRateThrottle

class ContactSubmissionRateThrottle(AnonRateThrottle):
    """
    Rate throttle for unauthenticated contact form submissions.
    Restricts spam or automated flood requests (default: 10 requests / hour / IP).
    """
    scope = 'contact'

class ConferenceRegistrationRateThrottle(AnonRateThrottle):
    """
    Rate throttle for conference attendee RSVP / registrations.
    Restricts bot abuse on registration endpoints (default: 10 requests / minute / IP).
    """
    scope = 'conference_register'
