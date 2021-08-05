from django.conf import settings as dj_settings

from .settings import Settings

# True means this parameter is to be imported.
PARAMS = (
    ("URN_NID", (False, "x-nid")),
    ("URN_NSS", (False, "self")),
    ("HOST", (False, "self")),
    ("DOMAIN", (False, None)),
    ("SCHEME", (False, "https")),
)

apibase_settings = Settings(
    getattr(dj_settings, "APIBASE", None),
    dict((i[0], i[1][1]) for i in PARAMS),
    [i[0] for i in PARAMS if i[1][0]],
)
