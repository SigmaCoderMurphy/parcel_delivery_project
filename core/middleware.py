import re


class HtmlMinifyMiddleware:
    """
    Conservative HTML minifier for dynamic responses in production.
    Keeps behavior stable by only collapsing inter-tag whitespace.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.headers.get("Content-Type", "")
        if (
            request.method == "GET"
            and response.status_code == 200
            and "text/html" in content_type
            and not response.streaming
        ):
            html = response.content.decode(response.charset or "utf-8")
            html = re.sub(r">\s+<", "><", html)
            response.content = html.encode(response.charset or "utf-8")
            response["Content-Length"] = str(len(response.content))
        return response
