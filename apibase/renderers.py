from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework_csv import renderers
from rest_framework.settings import api_settings


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the forms."""

    def get_rendered_html_form(self, data, view, method, request):
        return None

class CsvRenderer(renderers.CSVRenderer):
    pass


RENDERERS = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CsvRenderer, ) 
