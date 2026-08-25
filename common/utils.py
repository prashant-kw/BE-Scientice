from django.conf import settings

def build_absolute_media_url(request, file_field_or_url):
    """
    Given a request context and a file/image field or string URL, returns
    a fully-qualified absolute URL (e.g. http://localhost:8000/media/news/xxx.jpg).
    """
    if not file_field_or_url:
        return ''

    # If it's a FieldFile or ImageFieldFile instance
    if hasattr(file_field_or_url, 'url'):
        try:
            url = file_field_or_url.url
        except (ValueError, AttributeError):
            return ''
    else:
        url = str(file_field_or_url).strip()

    if not url:
        return ''

    # If already a fully qualified external URL
    if url.startswith('http://') or url.startswith('https://'):
        return url

    # If it's a relative media path not starting with MEDIA_URL, prepend MEDIA_URL
    media_url = getattr(settings, 'MEDIA_URL', '/media/')
    if not url.startswith('/') and not url.startswith(media_url):
        url = f"{media_url.rstrip('/')}/{url.lstrip('/')}"

    # Build absolute URI using request context if available
    if request:
        return request.build_absolute_uri(url)

    return url
