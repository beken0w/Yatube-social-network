from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_all_templates(self):
        dict_data = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        auth_list = [
            '/auth/password_change/',
            '/auth/password_change/done/'
        ]
        for url, template in dict_data.items():
            with self.subTest(url=url):
                if url in auth_list:
                    response = self.authorized_client.get(url)
                else:
                    response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
