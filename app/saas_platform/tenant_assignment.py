"""Assign Tenant to users when PLATFORM_SAAS_ENABLED is on."""

from django.conf import settings
from django.utils.text import slugify

from .models import Tenant


def assign_tenant_for_new_user(user) -> None:
    if not getattr(settings, 'PLATFORM_SAAS_ENABLED', False):
        return
    org = (user.organization_name or '').strip()
    if org:
        slug = slugify(org)[:80] or 'org'
        base = slug
        i = 0
        while Tenant.objects.filter(slug=slug).exclude(organization_name_key=org).exists():
            i += 1
            slug = f'{base}-{i}'[:80]
        tenant, _ = Tenant.objects.get_or_create(
            organization_name_key=org,
            defaults={'name': org, 'slug': slug},
        )
        user.tenant = tenant
    else:
        tenant, _ = Tenant.objects.get_or_create(
            slug='default',
            defaults={'name': 'Default', 'organization_name_key': ''},
        )
        user.tenant = tenant
    user.save(update_fields=['tenant'])
