import re

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

from templates.models import Content, Widget
from tests.base import BaseAPITestCase


UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class TemplateEditorSyncTests(BaseAPITestCase):
    def test_activate_on_screen_updates_screen_and_queues_commands(self):
        template = self.create_template(name="Editor Activation Template")
        screen = self.create_screen(name="Lobby Screen")

        cache_key = f"screen_template_{screen.id}"
        cache.set(cache_key, "stale-template", timeout=60)

        url = reverse("template-activate-on-screen", kwargs={"id": str(template.id)})
        response = self.client.post(
            url,
            {"screen_id": str(screen.id), "sync_content": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertTrue(response.data["commands_queued"])
        self.assertIn("screen", response.data)
        self.assertIsNone(cache.get(cache_key))

        screen.refresh_from_db()
        self.assertEqual(screen.active_template_id, template.id)
        self.assertTrue(screen.commands.filter(type="refresh").exists())
        self.assertTrue(screen.commands.filter(type="sync_content").exists())

    def test_template_save_syncs_widget_ids_to_backend_uuid(self):
        template = self.create_template(name="Widget Sync Template", config_json={})

        payload = {
            "config_json": {
                "widgets": [
                    {
                        "id": "widget-local-123",
                        "type": "text",
                        "name": "Headline",
                        "x": "10%",
                        "y": "20%",
                        "width": "30%",
                        "height": "15%",
                        "zIndex": 1,
                        "visible": True,
                        "content": "Hello",
                        "style": {"fontSize": "24px"},
                    }
                ]
            }
        }
        url = reverse("template-detail", kwargs={"id": str(template.id)})
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        template.refresh_from_db()
        self.assertEqual(Widget.objects.filter(layer__template=template).count(), 1)
        synced_widget_id = template.config_json["widgets"][0]["id"]
        self.assertRegex(synced_widget_id, UUID_REGEX)

    def test_template_save_links_content_id_to_synced_widget(self):
        template = self.create_template(name="Content Link Template", config_json={})
        content = Content.objects.create(
            name="Standalone Image",
            type="image",
            file_url="https://example.com/image.jpg",
            widget=None,
            is_active=True,
        )

        payload = {
            "config_json": {
                "widgets": [
                    {
                        "id": "tmp-widget-id",
                        "type": "image",
                        "name": "Image Widget",
                        "x": "5%",
                        "y": "5%",
                        "width": "40%",
                        "height": "40%",
                        "zIndex": 2,
                        "visible": True,
                        "content": "https://example.com/image.jpg",
                        "content_id": str(content.id),
                        "style": {"objectFit": "cover"},
                    }
                ]
            }
        }
        url = reverse("template-detail", kwargs={"id": str(template.id)})
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content.refresh_from_db()
        self.assertIsNotNone(content.widget_id)
        self.assertEqual(content.widget.layer.template_id, template.id)
