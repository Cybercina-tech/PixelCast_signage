# Generated manually — seed hardware-specific buyer-intent guides.

from django.db import migrations
from django.utils import timezone


POSTS = [
    {
        'title': 'Guide: How to set up PixelCast on LG WebOS TV Browser',
        'slug': 'setup-pixelcast-on-lg-webos-tv-browser',
        'excerpt': 'Step-by-step LG WebOS setup guide for teams who want to run PixelCast on TV browser signage workflows.',
        'meta_title': 'Guide: How to set up PixelCast on LG WebOS TV Browser',
        'meta_description': 'Follow this practical LG WebOS TV browser guide to set up PixelCast, pair screens, publish schedules, and keep signage running reliably.',
        'body': """Many operators ask: **How do I set up digital signage on an LG TV without extra complexity?**

This guide shows how to configure PixelCast on an **LG WebOS TV Browser** in a repeatable workflow.

## Before you start

- A stable internet connection on the TV
- Access to your PixelCast admin account
- The TV browser app available on your WebOS version

## Step 1: Open the LG TV browser

1. On your LG WebOS home screen, launch the browser.
2. Enter your PixelCast pairing URL (usually `/player/connect` on your domain).
3. Wait for the pairing screen to appear.

## Step 2: Pair the screen in PixelCast

1. In the PixelCast dashboard, open screen management.
2. Confirm the new device and assign a clear screen name (for example: `Branch-12-Counter-Menu`).
3. Add tags or groups for location-based scheduling.

## Step 3: Publish your first content schedule

1. Select an existing template or create one.
2. Attach content assets and define playback timing.
3. Publish the schedule to the paired LG screen.

## Step 4: Validate playback and recovery behavior

- Confirm autoplay works after browser launch.
- Verify content switches on schedule.
- Test remote refresh/reload command from the dashboard.

## Operational best practices for LG WebOS

- Keep browser homepage pinned to the PixelCast player URL.
- Use consistent naming conventions across all branches.
- Monitor heartbeat and uptime from the dashboard to catch offline screens quickly.

## Troubleshooting quick checks

- If pairing does not show: verify network + correct URL.
- If content does not update: check schedule assignment and timezone.
- If TV exits playback: review power-saving/browser session settings on WebOS.

## Next steps

- Cloud deployment path: `/solutions/cloud-digital-signage-tv-browser`
- Smart TV workflow guide: `/guides/turn-smart-tv-into-digital-signboard`
- Plan comparison: `/pricing`
""",
    },
    {
        'title': 'How to auto-start TV browser on Tizen OS for digital signage',
        'slug': 'auto-start-tv-browser-on-tizen-os-digital-signage',
        'excerpt': 'A practical Tizen OS playbook for auto-starting TV browser signage with PixelCast and reducing manual intervention.',
        'meta_title': 'How to auto-start TV browser on Tizen OS for digital signage',
        'meta_description': 'Learn how to auto-start TV browser on Tizen OS for digital signage, pair with PixelCast, and improve uptime for always-on displays.',
        'body': """Samsung operators often search for one specific workflow: **How to auto-start TV browser on Tizen OS for digital signage**.

This guide focuses on reliability and reduced manual recovery for always-on display operations.

## Why auto-start matters

Without auto-start browser behavior, power interruptions can leave displays idle or on the wrong screen. A proper startup flow improves uptime and reduces field visits.

## Step 1: Prepare Tizen browser launch path

1. Open browser settings on the Samsung Tizen TV.
2. Set startup behavior to reopen the last used page (if supported by model/firmware).
3. Set the PixelCast player URL as the last active browser page.

## Step 2: Configure PixelCast pairing

1. Open the pairing page from the TV browser.
2. Pair the screen in the PixelCast dashboard.
3. Assign content and a default fallback template.

## Step 3: Tune power and reboot behavior

- Disable aggressive eco/sleep modes that terminate browser sessions.
- If your model supports startup app preferences, prioritize browser reopen behavior.
- Test controlled reboot and verify automatic return to the player URL.

## Step 4: Add operational guardrails

- Use monitoring alerts for offline Tizen endpoints.
- Keep a fallback playlist for network interruptions.
- Use remote commands for refresh/recovery before dispatching on-site teams.

## Tizen troubleshooting checklist

- Browser opens home page instead of player URL: re-check startup and homepage config.
- Content appears stale: force refresh and verify schedule publish time.
- Intermittent disconnects: check network stability and DNS resolution.

## Recommended architecture

Use PixelCast cloud scheduling + browser-based playback for distributed signage fleets where consistency and fast updates are critical.

## Next steps

- TV browser cloud solution: `/solutions/cloud-digital-signage-tv-browser`
- Browser-first solution page: `/solutions/browser-based-digital-signage-software`
- Start rollout planning: `/signup`
""",
    },
]


def forwards(apps, schema_editor):
    BlogPost = apps.get_model('blog', 'BlogPost')
    now = timezone.now()
    for post in POSTS:
        if BlogPost.objects.filter(slug=post['slug']).exists():
            continue
        BlogPost.objects.create(
            title=post['title'],
            slug=post['slug'],
            excerpt=post['excerpt'],
            body=post['body'],
            status='published',
            published_at=now,
            meta_title=post['meta_title'],
            meta_description=post['meta_description'],
        )


def backwards(apps, schema_editor):
    BlogPost = apps.get_model('blog', 'BlogPost')
    BlogPost.objects.filter(slug__in=[post['slug'] for post in POSTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0004_seed_intent_keyword_posts'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
