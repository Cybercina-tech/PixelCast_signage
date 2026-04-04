# Generated manually — seed first marketing article (legacy static /blog content as Markdown).

from django.db import migrations
from django.utils import timezone

MARKDOWN = """Whether you run retail stores, restaurants, offices, or a mixed estate, digital signage systems turn commercial displays into a coordinated channel for promotions, menus, wayfinding, and internal communications.

## Why teams invest in digital signage solutions

Static posters age quickly. Digital signage software lets you schedule campaigns, swap creative in minutes, and keep branding consistent across indoor digital signage, window displays, and meeting-room screens. For UK and international operators, the same platform can support local promotions while headquarters retains governance.

## Common use cases

- **Retail digital signage:** in-store promotion screens, pricing zones, and seasonal campaigns on digital display screens.
- **Restaurant & hospitality:** digital menu boards, dayparting, and allergen updates on LCD display solutions behind the counter or in dining rooms.
- **Corporate & workplace:** reception display screens, KPI boards, and corporate communication screens in lobbies.
- **Public venues:** wayfinding screens, waiting room screens, and outdoor digital signage where hardware supports the environment.

## How to choose signage software and hardware

Start with operating constraints: network reliability, who updates content, and whether you need interactive screens or passive loops. Then map vendors against:

1. **Content workflow:** template tools, approvals, and display content management for your team size.
2. **Player ecosystem:** support for your devices—Android, web players, or dedicated players for LED signage and high-brightness outdoor panels.
3. **Operations:** monitoring, remote reboot, and logs for a commercial screen network at scale.
4. **Security & hosting:** SSO, audit trails, and whether cloud or self-hosted digital signage fits policy.

## Next steps with PixelCast

PixelCast combines template editing, schedules, remote commands, and a secure web player so you can run branded display solutions without juggling spreadsheets of USB sticks.

## FAQ

### What is digital signage software?

Digital signage software lets you design, schedule, and publish content to a network of commercial displays—often LCD or LED screens—so every location shows the right message at the right time.

### Do I need special hardware for commercial digital signage?

You typically use commercial displays or players built for long runtimes. Many teams pair dedicated players with professional screens; some use secure web players for kiosks and meeting-room displays.

### How do I choose between cloud and self-hosted signage?

Cloud is faster to deploy; self-hosted can suit strict data residency or air-gapped networks. Evaluate uptime SLAs, backup strategy, and who maintains OS and player updates.
"""


def forwards(apps, schema_editor):
    BlogPost = apps.get_model('blog', 'BlogPost')
    if BlogPost.objects.filter(slug='digital-signage-for-business').exists():
        return
    BlogPost.objects.create(
        title='Digital signage for business: benefits, use cases, and how to choose the right solution',
        slug='digital-signage-for-business',
        excerpt=(
            'Whether you run retail stores, restaurants, offices, or a mixed estate, digital signage systems turn '
            'commercial displays into a coordinated channel for promotions, menus, wayfinding, and internal communications.'
        ),
        body=MARKDOWN,
        status='published',
        published_at=timezone.now(),
        meta_title='',
        meta_description='',
    )


def backwards(apps, schema_editor):
    BlogPost = apps.get_model('blog', 'BlogPost')
    BlogPost.objects.filter(slug='digital-signage-for-business').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
