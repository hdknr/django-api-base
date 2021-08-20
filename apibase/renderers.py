from rest_framework.renderers import BrowsableAPIRenderer, StaticHTMLRenderer
from rest_framework.settings import api_settings
from rest_framework_csv import renderers


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the forms."""

    def get_rendered_html_form(self, data, view, method, request):
        return None


class CsvRenderer(renderers.CSVRenderer):
    pass


class BinaryRenderer(renderers.BaseRenderer):
    def render(self, data, media_type=None, renderer_context=None):
        return data


class PdfRenderer(BinaryRenderer):
    media_type = "application/pdf"
    format = "pdf"
    charset = None
    render_style = "binary"


class XlsxRenderer(BinaryRenderer):
    media_type = "application/xlsx"
    format = "xlsx"
    charset = None
    render_style = "binary"


class ZipballRenderer(BinaryRenderer):
    media_type = "application/zip"
    format = "zip"
    charset = None
    render_style = "binary"


RENDERERS = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (
    CsvRenderer,
    XlsxRenderer,
    PdfRenderer,
    StaticHTMLRenderer,
)
