from .models import Service


DEFAULT_SERVICES = [
    {
        "slug": "retail-ecommerce-delivery",
        "title": "Retail & E-commerce Delivery",
        "short_description": "Fast, reliable delivery for local retailers and online stores.",
        "full_description": (
            "Same-day delivery across GTA, real-time tracking, flexible pickup schedules, "
            "and competitive volume pricing for clothing boutiques, electronics stores, "
            "cosmetic shops, and online retailers."
        ),
        "icon": "fas fa-store",
        "is_featured": True,
        "order": 1,
    },
    {
        "slug": "warehouse-distribution",
        "title": "Warehouse & Distribution",
        "short_description": "Last-mile solutions for warehouses and distribution centers.",
        "full_description": (
            "12ft to 26ft trucks, loading/unloading support, scheduled routes, and bulk "
            "shipment handling for warehouses and distribution teams."
        ),
        "icon": "fas fa-warehouse",
        "is_featured": True,
        "order": 2,
    },
    {
        "slug": "furniture-delivery",
        "title": "Furniture Delivery",
        "short_description": "Specialized handling for furniture stores and bulky items.",
        "full_description": (
            "Careful transport for furniture and mid-bulky goods, trained handling, and "
            "reliable placement-focused delivery support."
        ),
        "icon": "fas fa-couch",
        "is_featured": True,
        "order": 3,
    },
    {
        "slug": "pharmacy-delivery",
        "title": "Pharmacy Delivery",
        "short_description": "Secure and reliable local pharmacy delivery.",
        "full_description": (
            "Fast and compliant delivery support for pharmacies with signature-ready "
            "handoff and route reliability across the GTA."
        ),
        "icon": "fas fa-pills",
        "is_featured": True,
        "order": 4,
    },
    {
        "slug": "office-business-delivery",
        "title": "Office & Business Delivery",
        "short_description": "Reliable courier services for day-to-day business operations.",
        "full_description": (
            "Document and parcel runs, inter-office movement, and scheduled or on-demand "
            "courier support for offices and service providers."
        ),
        "icon": "fas fa-building",
        "is_featured": True,
        "order": 5,
    },
]


def ensure_default_services():
    """
    Seed legacy website services into DB so they can be managed from dashboard.
    Safe to run repeatedly (upserts by slug).
    """
    for data in DEFAULT_SERVICES:
        defaults = data.copy()
        slug = defaults.pop("slug")
        Service.objects.get_or_create(slug=slug, defaults=defaults)
