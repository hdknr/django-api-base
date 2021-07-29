from rest_framework.renderers import BrowsableAPIRenderer, StaticHTMLRenderer
from rest_framework.settings import api_settings
from rest_framework_csv import renderers


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the forms."""

    def get_rendered_html_form(self, data, view, method, request):
        return None


class CsvRenderer(renderers.CSVRenderer):
    pass


class PdfRenderer(renderers.BaseRenderer):
    media_type = "application/pdf"
    format = "pdf"
    charset = None
    render_style = "binary"

    def render(self, data, media_type=None, renderer_context=None):
        return data


class XlsxRenderer(renderers.BaseRenderer):
    media_type = "application/xlsx"
    format = "xlsx"
    charset = None
    render_style = "binary"

    def render(self, data, media_type=None, renderer_context=None):
        return data


RENDERERS = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (
    CsvRenderer,
    XlsxRenderer,
    PdfRenderer,
    StaticHTMLRenderer,
)
