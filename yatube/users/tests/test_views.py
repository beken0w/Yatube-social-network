from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class ViewsTemplateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.new_user = {
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'email': 'testabc@mail.ru',
            'password1': 'abc123abc',
            'password2': 'abc123abc'
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_pages_name = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:password_reset_form'):
            'users/password_reset_form.html',
            reverse('users:password_reset_done'):
            'users/password_reset_done.html',
            reverse('users:password_reset_complete'):
            'users/password_reset_complete.html',
        }
        for url, template in template_pages_name.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                error_name = f'Ошибка в {response}'
                self.assertTemplateUsed(response, template, error_name)

    def test_password_change_and_done(self):
        """Проверка URL страницы изменения пароля
        и страницы успешной замены.
        """
        dict_data = {
            reverse('users:password_change_form'):
            'users/password_change_form.html',
            reverse('users:password_change_done'):
            'users/password_change_done.html',
        }
        for url, template in dict_data.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                error_name = f'Ошибка в {response}'
                self.assertTemplateUsed(response, template, error_name)

    def test_signup_context(self):
        """Проверка context формы при регистрации  через signup."""
        response = self.guest_client.post(reverse('users:signup'),
                                          self.new_user)
        self.assertEqual(
            response.context['form'].cleaned_data['email'],
            self.new_user['email'])
        self.assertEqual(
            response.context['form'].cleaned_data['username'],
            self.new_user['username'])
        self.assertEqual(
            response.context['form'].cleaned_data['first_name'],
            self.new_user['first_name'])
        self.assertEqual(
            response.context['form'].cleaned_data['last_name'],
            self.new_user['last_name'])
