import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Comment, Group, Post

small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B')
uploaded = SimpleUploadedFile(
    name='small.gif',
    content=small_gif,
    content_type='image/gif')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):
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
            image=uploaded,
            id=80,
        )
        cls.comment = Comment(
            post=cls.post,
            author=cls.non_author,
            text='text_for_comment',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.non_author_client = Client()
        self.non_author_client.force_login(self.non_author)

    def test_create_post(self):
        """Проверка создания новой записи."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new_post_text',
            'author': self.user,
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='new_post_text',
                author=self.user,
                group=self.group.id,
            ).exists())
        self.assertEqual(response.status_code, 302)

    def test_forms_after_update(self):
        """Проверка в случае создания поста с аналогичным """
        post_count = Post.objects.count()
        edited_form_data = {
            'text': 'editedtextfortest',
            'id': self.post.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=edited_form_data,)
        # проверка на неизменность кол-ва постов
        self.assertEqual(Post.objects.count(), post_count)
        # проверка на соответствие новых данных
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, edited_form_data['text'])

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        self.assertTrue(
            Post.objects.filter(
                image='posts/small.gif'
            ).exists()
        )

        response_index = self.authorized_client.get(
            reverse('posts:index')
        )
        index_obj = response_index.context['page_obj'][0].image
        self.assertEqual(index_obj, 'posts/small.gif')

        response_group_posts = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        group_obj = response_group_posts.context['page_obj'][0].image
        self.assertEqual(group_obj, 'posts/small.gif')

        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        profile_obj = response_profile.context['page_obj'][0].image
        self.assertEqual(profile_obj, 'posts/small.gif')

        response_post_detail = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post_detail_obj = response_post_detail.context['post'].image
        self.assertEqual(post_detail_obj, 'posts/small.gif')

    def test_image_has_correct_extension(self):
        """Проверка расширения изображения."""
        text_file = SimpleUploadedFile("assignment.txt", b"content")
        form_data = {
            'text': 'text_for_image_test',
            'author': self.user,
            'group': self.group.id,
            'image': text_file,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFormError(response, 'form', 'image',
                             errors=['Загрузите правильное изображение. '
                                     'Файл, который вы загрузили, поврежден '
                                     'или не является изображением.'])

    def test_comment_form(self):
        """Проверка формы коммента."""
        self.assertEqual(self.comment.text, 'text_for_comment')
