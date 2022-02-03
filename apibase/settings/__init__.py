from .settings import Settings

apibase_settings = Settings.create(
    "APIBASE",
    (
        ("URN_NID", (False, "x-nid")),
        ("URN_NSS", (False, "self")),
        ("HOST", (False, "self")),
        ("DOMAIN", (False, None)),
        ("SCHEME", (False, "https")),
        ("STORAGE_PREFIX", (False, "storage")),
    ),
)
