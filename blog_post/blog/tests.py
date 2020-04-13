from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag
from django.utils import timezone
from django.contrib.auth.models import User

# Create your tests here.
def create_category(name='life', description=''):
    category, is_created = Category.objects.get_or_create(
        name = name,
        description = description,
    )

    category.slug = category.name.replace(' ', '-').replace('/', '')
    category.save()

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

def create_tag(name='nomal_tag'):
    tag, is_created = Tag.objects.get_or_create(
        name = name
    )
    tag.slug = tag.name.replace(' ', '-').replace('/', '')
    tag.save()

    return tag


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


    def test_tag(self):
        tag_000 = create_tag(name = 'django')
        tag_001 = create_tag(name = 'jquery')

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )
        post_000.tags.add(tag_000)
        post_000.tags.add(tag_001)
        post_000.save()

        post_001 = create_post(
            title = 'The second post',
            content = 'It is next Post!',
            author = self.author_000,
        )
        post_001.tags.add(tag_001)
        post_001.save()

        self.assertEqual(post_000.tags.count(), 2) #post는 여러개의 tag를 가질 수 있음
        self.assertEqual(tag_001.post_set.count(), 2)  #하나의 tag는 여러개의 post에 붙을 수 있음
        self.assertEqual(tag_001.post_set.first(), post_000)  #하나의 tag는 자신을 가진 post들을 불러올 수 있음
        self.assertEqual(tag_001.post_set.last(), post_001)  #하나의 tag는 자신을 가진 last을 불러올 수 있음


class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create(username = 'Meg', password='nopassword')

    def check_navbar(self, soup):
        navbar = soup.find('div', id='navbar')
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

    def check_right_side(self, soup):
        #category card에서
        category_card = soup.find('div', id='category-card')
        #no category(1) 있어아함
        self.assertIn('no category (1)', category_card.text)
        #python(1) 있어야 함
        self.assertIn('python (1)', category_card.text)


    #포스트가 없을 때
    def test_post_list_no_post(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title

        self.assertIn(title.text, 'Blog')

        self.check_navbar(soup)

        #글이 아직 없을 때
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('No Posts Yet.', soup.body.text)


    #포스트가 1개 이상 있을 때
    def test_post_list_with_post(self):

        tag_django = create_tag(name='django')
        #글이 생겼을 때
        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )
        post_000.tags.add(tag_django)
        post_000.save()
        
        post_001 = create_post(
            title = 'The second post',
            content = 'It is next Post!',
            author = self.author_000,
            category = create_category(name='python'),
        )
        post_001.tags.add(tag_django)
        post_001.save()

        self.assertGreater(Post.objects.count(), 0)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        body = soup.body
        self.assertNotIn('No Posts Yet.', body.text)
        self.assertIn(post_000.title, body.text)

        post_000_read_more_btn = body.find('a', id='read-more-post-{}'.format(post_000.pk))
        self.assertEqual(post_000_read_more_btn['href'], post_000.get_absolute_url())

        self.check_right_side(soup)

        #main_div를 가져옴
        main_div = soup.find('div', id='main-div')
        #첫번째 포스트에는 "python" 있어야함
        self.assertIn('python', main_div.text)
        #두번째 포스트에는 "no category" 있어야함
        self.assertIn('no category', main_div.text)

        #태그가 있는지 확안해보기 위해
        post_card_000 = main_div.find('div', id='post-card-{}'.format(post_000.pk))
        self.assertIn('#django', post_card_000.text)

    #포스트 상세보기를 눌렀을 때
    def test_post_detail(self):

        tag_django = create_tag(name='django')
        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )
        post_000.tags.add(tag_django)
        post_000.save()

        post_001 = create_post(
            title = 'The second post',
            content = 'It is next Post!',
            author = self.author_000,
            category = create_category(name='python'),
        )
        post_001.tags.add(tag_django)
        post_001.save()

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
        main_div = body.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn(post_000.author.username, main_div.text)

        self.assertIn(post_000.content, main_div.text)

        self.check_right_side(soup)

        #태그가 있는지 확안해보기 위해
        post_card_000 = main_div.find('div', id='post-card-{}'.format(post_000.pk))
        self.assertIn('#django', post_card_000.text)



    #특정 카테고리를 클릭했을 때
    def test_post_list_by_category(self):
        category_python = create_category(name='python')

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )

        post_001 = create_post(
            title = 'The second post',
            content = 'It is next Post!',
            author = self.author_000,
            category = category_python
        )

         #category_python을 누르면 해당 카테고리로 이동
        response = self.client.get(category_python.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual('Blog - {}'.format(category_python.name), soup.title.text)
        
        main_div = soup.find('div', id='main-div')
        self.assertNotIn('no category', main_div.text)
        self.assertIn(category_python.name, main_div.text)


    #no category를 클릭했을 때
    def test_post_list_no_category(self):
        category_python = create_category(name='python')

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )

        post_001 = create_post(
            title = 'The second post',
            content = 'It is next Post!',
            author = self.author_000,
            category = category_python
        )

         #no category를 눌러서 /blog/category/none/ 주소를 받을 때
        response = self.client.get('/blog/category/_none/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual('Blog - {}'.format(category_python.name), soup.title.text)
        
        main_div = soup.find('div', id='main-div')
        self.assertIn('no category', main_div.text)
        self.assertNotIn(category_python.name, main_div.text)
