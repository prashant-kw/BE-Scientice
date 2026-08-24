import io
from PIL import Image, ImageOps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP', 'GIF'}

def validate_and_clean_image(uploaded_file):
    """
    Validate uploaded image using Pillow byte inspection (preventing MIME spoofing)
    and strip EXIF metadata to protect user privacy and avoid EXIF exploits.
    """
    if not uploaded_file:
        return uploaded_file

    if uploaded_file.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(f"Image file size exceeds maximum allowed limit (15MB). Current size: {uploaded_file.size / (1024*1024):.1f}MB")


    try:
        # 1. Verify byte integrity
        uploaded_file.seek(0)
        img_probe = Image.open(uploaded_file)
        img_format = img_probe.format
        if img_format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError(f"Unsupported image format '{img_format}'. Allowed formats: JPEG, PNG, WEBP, GIF.")
        img_probe.verify()

        # 2. Re-open to strip EXIF and re-encode safely
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        
        # Auto-orient based on EXIF before stripping
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # Strip EXIF by saving fresh image buffer
        output_io = io.BytesIO()
        save_format = 'PNG' if img_format == 'PNG' else ('WEBP' if img_format == 'WEBP' else 'JPEG')
        
        if save_format == 'JPEG' and img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')

        img.save(output_io, format=save_format, quality=90, optimize=True)
        output_io.seek(0)

        cleaned_file = InMemoryUploadedFile(
            file=output_io,
            field_name=uploaded_file.field_name if hasattr(uploaded_file, 'field_name') else 'image',
            name=uploaded_file.name,
            content_type=f'image/{save_format.lower()}',
            size=output_io.getbuffer().nbytes,
            charset=None
        )
        return cleaned_file

    except (IOError, SyntaxError, ValueError) as e:
        raise ValidationError(f"Invalid or corrupted image file: {str(e)}")

MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

def validate_and_clean_pdf(uploaded_file):
    """
    Validate uploaded PDF using magic bytes inspection (preventing MIME spoofing)
    and enforce a maximum file size.
    """
    if not uploaded_file:
        return uploaded_file

    if uploaded_file.size > MAX_PDF_SIZE_BYTES:
        raise ValidationError(f"PDF file size exceeds maximum allowed limit (10MB). Current size: {uploaded_file.size / (1024*1024):.1f}MB")

    try:
        uploaded_file.seek(0)
        # Check magic bytes for PDF (%PDF-)
        magic_bytes = uploaded_file.read(5)
        if magic_bytes != b'%PDF-':
            raise ValidationError("Invalid file content: Not a valid PDF document.")
        
        uploaded_file.seek(0)
        return uploaded_file
    except Exception as e:
        raise ValidationError(f"Invalid or corrupted PDF file: {str(e)}")
