# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.non_author = User.objects.create_user(username='non_author')
        cls.group = Group.objects.create(
            title='title_for_test',
            slug='slug-test',
            description='description_test',
        )
        cls.post = Post.objects.create(
            text='textfortest',
            author=cls.user,
            group=cls.group,
            id=80,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.non_author_client = Client()
        self.non_author_client.force_login(self.non_author)

    def test_all_templates(self):
        """Проверка всех шаблонов"""
        dict_data = {
            self.guest_client.get('/'): 'posts/index.html',
            self.guest_client.get(
                reverse('posts:group_posts',
                        args=[self.group.slug])): 'posts/group_list.html',
            self.guest_client.get(
                reverse('posts:profile',
                        args=[self.user.username])): 'posts/profile.html',
            self.guest_client.get(
                reverse('posts:post_detail',
                        args=[self.post.id])): 'posts/post_detail.html',
            self.authorized_client.get(
                reverse('posts:post_create')): 'posts/post_create.html',
            self.authorized_client.get(
                reverse('posts:post_edit',
                        args=[self.post.id])): 'posts/post_create.html',
        }
        for response, template in dict_data.items():
            with self.subTest(response=response):
                error_name = f'Несоответствие в {response}'
                self.assertTemplateUsed(response, template, error_name)

    def test_access_to_pages(self):
        dict_data = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user.username}/': 200,
            f'/posts/{self.post.id}/': 200,
            '/create/': 200,
            f'/posts/{self.post.id}/edit/': 200,
            f'/posts/{self.post.id}/comment/': 302,
            '/follow/': 200,
            f'/profile/{self.user.username}/follow/': 302,
            f'/profile/{self.user.username}/unfollow/': 302,
            '/unexisting_page/': 404,
        }
        auth_list = [
            '/create/',
            f'/posts/{self.post.id}/edit/',
            f'/posts/{self.post.id}/comment/',
            '/follow/',
            f'/profile/{self.user.username}/follow/',
            f'/profile/{self.user.username}/unfollow/',
        ]
        for url, status_code in dict_data.items():
            with self.subTest(url=url):
                if url in auth_list:
                    response = self.authorized_client.get(url)
                else:
                    response = self.guest_client.get(url)
                error_name = f'Несоответствие в {response}'
                self.assertEqual(response.status_code, status_code, error_name)
        # проверка доступа к странице пользователя по юзернейму
        # авторизованного пользователя
        response_with_username = self.authorized_client.get(
            f'/profile/{self.user.username}/')
        self.assertEqual(response_with_username.status_code, 200)

    def test_guest_redirect(self):
        """
        Проверка редиректа:

        проверки запросов GET
        - нет доступа к созданию поста гостем
        - нет доступа к редактирования готового(1го) поста

        проверки запросов POST
        - нет доступа к отправке формы создания 2го поста гостем
        - нет доступа к отправке формы редактирования готового(1го) поста
        - проверка на кол-во постов в конце
        """
        edit_form = {
            'text': 'edit_test_text',
            'author': self.user,
        }
        create_form = {
            'text': 'create_test_text',
            'author': self.user,
        }
        posts_count = Post.objects.count()
        response_create_get = self.guest_client.get(
            reverse('posts:post_create'))
        response_edit_get = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))

        response_create_post = self.guest_client.post(
            reverse('posts:post_create'), data=create_form)
        response_edit_post = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=edit_form)

        self.assertRedirects(response_create_get,
                             '/auth/login/?next=/create/')
        self.assertRedirects(response_edit_get,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')
        self.assertRedirects(response_create_post,
                             '/auth/login/?next=/create/')
        self.assertRedirects(response_edit_post,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_non_author_redirect(self):
        """
        Проверка редиректа:

        проверка запроса GET
        - нет доступа к отправке формы редактирования готового(1го) поста

        проверки запросов POST
        - нет доступа к отправке формы редактирования готового(1го) поста
        - проверка на кол-во постов в конце
        """
        edit_form = {
            'text': 'edit_test_text',
            'author': self.user,
        }
        posts_count = Post.objects.count()
        response_edit_get = self.non_author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        response_edit_post = self.non_author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=edit_form)

        self.assertRedirects(response_edit_get,
                             f'/posts/{self.post.id}/')
        self.assertRedirects(response_edit_post,
                             f'/posts/{self.post.id}/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_try_comment(self):
        """Проверка возможности комментирования и редиректа."""
        comment_form = {
            'text': 'текст комментария',
        }
        comment_count = Comment.objects.count()
        response_guest = self.guest_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form)
        response_user = self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}),
            data=comment_form)
        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(response_user.status_code, 302)
        self.assertRedirects(response_guest,
                             '/auth/login/?next=/posts/80/comment/')
        self.assertRedirects(response_user, '/posts/80/')
        self.assertEqual(Comment.objects.count(), comment_count + 1)
