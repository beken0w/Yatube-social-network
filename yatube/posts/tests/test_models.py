from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='new_group')
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            created='Дата публикации тестового поста',
            author=cls.user,
            group=cls.group
        )

    def test_all_strings_and_their_arguments_in_post(self):
        dict_data = {
            self.post.text[:15]:
                str(self.post),
            self.post._meta.get_field(
                'text').verbose_name: 'Текст поста',
            self.post._meta.get_field(
                'created').verbose_name: 'Дата создания',
            self.post._meta.get_field(
                'author').verbose_name: 'Автор',
            self.post._meta.get_field(
                'group').verbose_name: 'Группа',
            self.post._meta.get_field(
                'text').help_text: 'Введите текст поста',
            self.post._meta.get_field(
                'group').help_text: 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in dict_data.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Названиегруппы',
            slug='Слаг название',
            description='Описание группы'
        )

    def test_group_title(self):
        """проверка поля с названием группы"""
        title = self.group.title
        self.assertEqual(title, 'Названиегруппы')
