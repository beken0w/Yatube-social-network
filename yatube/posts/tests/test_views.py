import time
from string import ascii_letters

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post

from yatube.settings import AMOUNT_POSTS_ON_PAGE, AMOUNT_POSTS_ON_SECOND_PAGE

User = get_user_model()


class ViewsTemplateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_pages_name = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.user.username}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}),
            'posts/post_create.html': reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id})
        }
        for template, reverse_name in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_post_template(self):
        """Проверяет шаблон страницы создания поста"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_index_context(self):
        """Проверка контекста главной страницы index.html"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object, self.post)

    def test_group_posts_context(self):
        """Шаблон group_posts - проверка контекста"""
        response = (self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug})))
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_profile_context(self):
        """Тест шаблона profile - проверка контекста"""
        response = (self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username})))
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_post_detail_context(self):
        """Тест шаблона post_detail - проверка контекста"""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context.get('post'), self.post)

    def test_post_edit_context(self):
        """Тест шаблона post_edit - проверка контекста"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_context(self):
        """Тест шаблона post_create - проверка контекста"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_with_group(self):
        """
        Проверка поста на:
        - наличие на главной странице,
        - наличие на странице с постами оригинальной группы,
        - отсутствие на странице с другой группой
        """
        another_group = Group.objects.create(
            title='title_for_another_group',
            slug='another_slug_test',
            description='another_description')

        self.assertEqual(self.client.get(reverse(
            'posts:index')).context['page_obj'][0], self.post)

        self.assertEqual(self.client.get(reverse(
            'posts:group_posts', kwargs={
                'slug': self.group.slug})).context['page_obj'][0], self.post)

        self.assertNotEqual(self.post.group, self.client.get(reverse(
            'posts:group_posts', kwargs={
                'slug': another_group.slug})).context['group'])


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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

    def test_cache_after_delete_post(self):
        """Проверка работы кеша и наличия удаленного поста в течении 20 сек."""
        post2 = Post.objects.create(
            text='cache_text',
            author=self.user,
            group=self.group,
            id=81,
        )
        before = self.authorized_client.get(reverse('posts:index'))
        post2.delete()
        after = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(after.content, before.content)

    def test_cache_time(self):
        """Проверка работы кеша."""
        # время старта
        zero_time = time.time()
        self.guest_client.get(reverse('posts:index'))
        # время после первого запроса
        start_time = time.time()
        self.guest_client.get(reverse('posts:index'))
        # время после 2го запроса
        end_time = time.time()
        first_req = start_time - zero_time
        second_req = end_time - start_time
        self.assertGreater(first_req, second_req)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='title_for_paginator',
            slug='pagi-slug',
            description='description_test')
        data_text = [i for i in ascii_letters[:13]]
        for text in data_text:
            cls.post = Post.objects.create(
                text=text,
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_all_first_pages_with_paginator(self):
        """Проверка всех первых страниц c пагинатором"""
        responses = [
            self.authorized_client.get(reverse(
                'posts:index')),
            self.authorized_client.get(reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug})),
            self.authorized_client.get(reverse(
                'posts:profile', kwargs={'username': self.user.username}))
        ]

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj']), AMOUNT_POSTS_ON_PAGE)

    def test_all_second_pages_with_paginator(self):
        """Проверка всех вторых страниц с пагинатором"""
        responses = [
            self.authorized_client.get(reverse(
                'posts:index') + '?page=2'),
            self.authorized_client.get(reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}) + '?page=2'),
            self.authorized_client.get(reverse(
                'posts:profile',
                kwargs={'username': self.user.username}) + '?page=2')
        ]

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(len(response.context[
                                     'page_obj']), AMOUNT_POSTS_ON_SECOND_PAGE)


class FollowerTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_author = User.objects.create_user(username='user_author')
        cls.another_user = User.objects.create_user(username='another_user')
        cls.group = Group.objects.create(
            title='title_for_test',
            slug='slug-test',
            description='description_test',
        )

    def setUp(self):
        cache.clear()
        self.user_client = Client()
        self.user_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user_author)
        self.another_client = Client()
        self.another_client.force_login(self.another_user)

    def test_auth_user_can_follow_and_unfollow(self):
        """Проверка возможности подписок для авторизованного юзера."""
        self.user_client.get(reverse('posts:profile_follow', kwargs={
            'username': self.user_author.username}))
        self.assertEqual(Follow.objects.count(), 1)

        self.user_client.get(reverse('posts:profile_unfollow', kwargs={
            'username': self.user_author.username}))
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_in_follower_list(self):
        """Проверка наличия нового поста у автора и
        отсутствия у других юзеров.
        """
        self.user_client.get(reverse('posts:profile_follow', kwargs={
            'username': self.user_author.username}))
        Post.objects.create(
            text='text_follow',
            author=self.user,
            group=self.group,
            id=95,
        )
        subs = Follow.objects.all()
        for i in subs:
            # проверка подписки подписчика
            self.assertTrue(i.user == self.user
                            and i.author == self.user_author)
            # проверка подписки не подписчика
            self.assertFalse(i.user == self.another_user
                             and i.author == self.user_author)
