"""Group website form sources for analytics and filtering."""

from collections import defaultdict

from django.db.models import Count

from .models import Lead

# Raw DB values saved from home / services / contact quote forms before canonical storage
WEBSITE_LEAD_SOURCES = frozenset({'website', 'contact_form', 'services_page'})

# Distinct hex colors per source so doughnut/list match and segments never duplicate greys.
SOURCE_COLORS = {
    'website': '#2563eb',
    'call': '#10b981',
    'whatsapp': '#14b8a6',
    'google': '#f59e0b',
    'referral': '#8b5cf6',
    'telemarketing': '#ec4899',
    'social_media': '#3b82f6',
    'import': '#ea580c',  # orange — distinct from "other"
    'other': '#64748b',  # slate
}

# Extra palette for rare / custom source keys (deterministic)
_FALLBACK_PALETTE = (
    '#0d9488',
    '#c026d3',
    '#ca8a04',
    '#4f46e5',
    '#dc2626',
    '#0891b2',
    '#65a30d',
    '#be123c',
)


def color_for_source_key(key: str) -> str:
    if key in SOURCE_COLORS:
        return SOURCE_COLORS[key]
    s = str(key)
    idx = sum(ord(c) for c in s) % len(_FALLBACK_PALETTE)
    return _FALLBACK_PALETTE[idx]


def canonical_source(source):
    """Map any website form variant to the stored primary key ``website``."""
    if not source:
        return 'other'
    s = str(source).strip()
    if s in WEBSITE_LEAD_SOURCES:
        return 'website'
    return s


def source_display_label(canonical_key):
    if canonical_key == 'website':
        return 'Website Leads'
    labels = dict(Lead.LEAD_SOURCE)
    return labels.get(canonical_key, canonical_key.replace('_', ' ').title())


def grouped_leads_by_source():
    """
    Lead counts by canonical source (all web forms → one bucket).
    Each item: source, label, name, count, color (for charts).
    """
    merged = defaultdict(int)
    for row in Lead.objects.values('source').annotate(c=Count('id')):
        merged[canonical_source(row['source'])] += row['c']

    rows = []
    for key in sorted(merged.keys(), key=lambda k: merged[k], reverse=True):
        label = source_display_label(key)
        rows.append({
            'source': key,
            'label': label,
            'name': label,
            'count': merged[key],
            'color': color_for_source_key(key),
        })
    return rows


def apply_source_filter(qs, source_key):
    """Filter queryset by lead source; ``website`` includes all website form variants."""
    if not source_key:
        return qs
    if source_key == 'website':
        return qs.filter(source__in=WEBSITE_LEAD_SOURCES)
    return qs.filter(source=source_key)
