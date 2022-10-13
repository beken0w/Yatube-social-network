from django.test import Client, TestCase


class CoreTemplateTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_page_with_custom_template(self):
        """Проверка кастомного шаблона 404."""
        response = self.guest_client.get('/unexisting_url/')
        self.assertTemplateUsed(response, 'core/404.html')
