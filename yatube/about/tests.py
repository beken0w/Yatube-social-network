from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client

User = get_user_model()


class AboutURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_templates(self):
        """Проверка соответствия шаблонов и URL."""
        dict_data = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for url, template in dict_data.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_access_to_pages(self):
        """Проверка доступности URL приложения about."""
        url_dict = {
            reverse('about:author'): 200,
            reverse('about:tech'): 200
        }
        for url, status_code in url_dict.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)
