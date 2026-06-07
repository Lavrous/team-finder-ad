from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_github_url(value):
    if not value:
        return

    parsed_url = urlparse(value)
    domain = parsed_url.netloc.lower().split(":")[0]

    if domain not in ["github.com", "www.github.com"]:
        raise ValidationError(
            "Ссылка должна вести именно на официальный сайт Github (github.com)."
        )
