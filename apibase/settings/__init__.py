from django.conf import settings as dj_settings
from .settings import Settings

# True means this parameter is to be imported.
PARAMS = (
    ('URN_NID', (False, 'myservice')),
    ('HOST', (False, 'www')),
    ('DOMAIN', (False, 'local')),
)

apibase_settings = Settings(
    getattr(dj_settings, "APIBASE", None),
    dict((i[0], i[1][1]) for i in PARAMS),
    [i[0] for i in PARAMS if i[1][0]],
)
