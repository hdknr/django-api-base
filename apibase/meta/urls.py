from rest_framework.routers import Route, SimpleRouter

from . import viewsets


class CustomReadOnlyRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """

    routes = [
        Route(
            url=r"^(?P<app_label>[^/]+)/(?P<model_name>[^/]+)/(?P<field_name>[^/]+)$",
            mapping={"get": "retrieve"},
            name="{basename}-detail",
            detail=True,
            initkwargs={"suffix": "Detail"},
        ),
        Route(
            url=r"^(?:(?P<app_label>[^/]+)/)?(?:(?P<model_name>[^/]+)/)?$",
            mapping={"get": "list"},
            name="{basename}-list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
    ]


router = CustomReadOnlyRouter()
router.register("", viewsets.ModelFieldViewSet, basename="modelfield")
urlpatterns = router.urls
