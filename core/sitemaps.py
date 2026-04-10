from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PublicStaticSitemap(Sitemap):
    """Public marketing pages for search engines."""

    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return ['home', 'services', 'about', 'contact']

    def location(self, item):
        return reverse(item)
