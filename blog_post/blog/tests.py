from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.utils import timezone
from django.contrib.auth.models import User

# Create your tests here.
def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(
        name = name,
        description = description,
    )
    return category

def create_post(title, content, author, category=None):
    blog_post = Post.objects.create(
        title = title,
        content = content,
        created = timezone.now(),
        author = author,
        category = category,
    )

    return blog_post

class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username = 'Meg', password='nopassword')

    def test_category(self):
        category = create_category()

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
            category = category,
        )

        self.assertEqual(category.post_set.count(), 1)


    def test_post(self):
        category = create_category()

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
            category = category,
        )



class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username = 'Meg', password='nopassword')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

    def test_post_list_no_post(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, 'BLOG')

        self.check_navbar(soup)

        #글이 아직 없을 때
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('No Posts Yet.', soup.body.text)

    def test_post_list_with_post(self):

        #글이 생겼을 때
        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )
        
        post_001 = create_post(
            title = 'The second post',
            content = 'It is next Post!',
            author = self.author_000,
            category = create_category(name='python'),
        )

        self.assertGreater(Post.objects.count(), 0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('No Posts Yet.', body.text)
        self.assertIn(post_000.title, body.text)

        post_000_read_more_btn = body.find('a', id='read-more-post-{}'.format(post_000.pk))
        self.assertEqual(post_000_read_more_btn['href'], post_000.get_absolute_url())

        #category card에서
        category_card = body.find('div', id='category-card')
        #no category(1) 있어아함
        self.assertIn('no category (1)', category_card.text)
        #python(1) 있어야 함
        self.assertIn('python (1)', category_card.text)
        
        #main_div를 가져옴
        main_div = body.find('div', id='main_div')
        #첫번째 포스트에는 "python" 있어야함
        self.assertIn('python', main_div.text)
        #두번째 포스트에는 "no category" 있어야함
        self.assertIn('no category', main_div.text)

    def test_post_detail(self):

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )

        self.assertGreater(Post.objects.count(), 0)
        post_000_url = post_000.get_absolute_url()
        self.assertEqual(post_000_url, '/blog/{}/'.format(post_000.pk))


        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertEqual(title.text, '{} - Blog'.format(post_000.title))
        self.check_navbar(soup)

        body = soup.body

        main_div = body.find('div', id='main_div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)

        self.assertIn(post_000.content, main_div.text)


        
