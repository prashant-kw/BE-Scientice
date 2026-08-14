import re
from html.parser import HTMLParser
from html import escape

ALLOWED_TAGS = {
    'p', 'b', 'i', 'strong', 'em', 'u', 's', 'strike',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'a', 'span', 'div',
    'hr', 'br', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img'
}

ALLOWED_ATTRIBUTES = {
    'a': {'href', 'title', 'target', 'rel'},
    'img': {'src', 'alt', 'title', 'width', 'height'},
    '*': {'class'}
}

SELF_CLOSING_TAGS = {'br', 'hr', 'img', 'input', 'meta'}
DANGEROUS_TAGS = {'script', 'style', 'iframe', 'object', 'embed', 'form', 'link', 'svg'}

class SafeHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.result = []
        self.ignored_stack = []

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower in DANGEROUS_TAGS:
            self.ignored_stack.append(tag_lower)
            return

        if self.ignored_stack:
            return

        if tag_lower not in ALLOWED_TAGS:
            return

        # Sanitize attributes
        safe_attrs = []
        tag_allowed_attrs = ALLOWED_ATTRIBUTES.get(tag_lower, set()).union(ALLOWED_ATTRIBUTES.get('*', set()))

        is_blank_target = False
        has_rel = False

        for name, value in attrs:
            name_lower = name.lower()
            if name_lower.startswith('on') or name_lower not in tag_allowed_attrs:
                continue

            # Strip javascript: or data: in href/src
            clean_value = value.strip() if value else ''
            if name_lower in {'href', 'src'}:
                if re.match(r'^\s*(javascript|vbscript|data):', clean_value, re.IGNORECASE):
                    continue

            if name_lower == 'target' and clean_value == '_blank':
                is_blank_target = True

            if name_lower == 'rel':
                has_rel = True

            safe_attrs.append(f'{name_lower}="{escape(clean_value)}"')

        if is_blank_target and not has_rel:
            safe_attrs.append('rel="noopener noreferrer"')

        attrs_str = (' ' + ' '.join(safe_attrs)) if safe_attrs else ''
        if tag_lower in SELF_CLOSING_TAGS:
            self.result.append(f'<{tag_lower}{attrs_str} />')
        else:
            self.result.append(f'<{tag_lower}{attrs_str}>')

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if self.ignored_stack:
            if self.ignored_stack[-1] == tag_lower:
                self.ignored_stack.pop()
            return

        if tag_lower in ALLOWED_TAGS and tag_lower not in SELF_CLOSING_TAGS:
            self.result.append(f'</{tag_lower}>')

    def handle_data(self, data):
        if not self.ignored_stack:
            self.result.append(escape(data))

    def handle_entityref(self, name):
        if not self.ignored_stack:
            self.result.append(f'&{name};')

    def handle_charref(self, name):
        if not self.ignored_stack:
            self.result.append(f'&#{name};')

    def get_html(self):
        return ''.join(self.result)

def sanitize_html(dirty_html: str) -> str:
    """
    Sanitize untrusted rich text HTML on the server.
    Ensures safe tags, clean URLs, stripped script/iframe tags, and removed event handlers.
    """
    if not dirty_html:
        return ''
    parser = SafeHTMLParser()
    parser.feed(dirty_html)
    return parser.get_html()

def sanitize_plain_text(dirty_text: str) -> str:
    """
    Strip all HTML tags and dangerous script/style blocks from plain text fields.
    """
    if not dirty_text:
        return ''
    # Strip script, style, and iframe blocks along with their inner contents
    clean = re.sub(r'<(script|style|iframe)[^>]*>.*?</\1>', '', dirty_text, flags=re.DOTALL | re.IGNORECASE)
    # Strip any remaining standalone tags
    clean = re.sub(r'<[^>]*>', '', clean)
    return clean.strip()

