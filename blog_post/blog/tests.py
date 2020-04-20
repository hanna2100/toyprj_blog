from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment
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

def create_comment(post, text='Like it!', author=None):
    if author is None:
        author, is_created = User.objects.get_or_create(
            username = 'guest',
            password = 'guestpassword'
        )

    comment = Comment.objects.create(
        post=post,
        text=text,
        author=author
    )

    return comment


class TestModel(TestCase):
    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create_user(username = 'Meg', password='nopassword')

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
        self.assertEqual(tag_001.post_set.first(), post_001)  #하나의 tag는 자신을 가진 post들을 불러올 수 있음
        self.assertEqual(tag_001.post_set.last(), post_000)  #하나의 tag는 자신을 가진 last을 불러올 수 있음

    def test_comment(self):
        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )

        self.assertEqual(Comment.objects.count(), 0)

        comment_000 = create_comment(
            post=post_000,
        )

        comment_001 = create_comment(
            post=post_000,
            text = 'second comment'
        )

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(post_000.comment_set.count(), 2)


class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.author_000 = User.objects.create_user(username = 'Meg', password='nopassword')
        self.user_nia = User.objects.create_user(username = 'Nia', password='nopassword')

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

    def test_pagination(self):

        #포스트가 적은경우
        for i in range(0, 3):
            post = create_post(
                title = 'The post No. {}'.format(i),
                content = 'content {}'.format(i),
                author = self.author_000,
            )
        
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertNotIn('Older', soup.body.text)
        self.assertNotIn('Newer', soup.body.text)


        #포스트가 많은경우
        for i in range(3, 10):
            post = create_post(
                title = 'The post No. {}'.format(i),
                content = 'content {}'.format(i),
                author = self.author_000,
            )
        
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertIn('Older', soup.body.text)
        self.assertIn('Newer', soup.body.text)




    #포스트 상세보기를 눌렀을 때
    def test_post_detail(self):

        tag_django = create_tag(name='django')
        category_python = create_category(name='python')

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
            category = category_python,
        )

        comment_000 = create_comment(post_000, text='a first comment', author=self.user_nia)
        comment_001 = create_comment(post_000, text='a second comment', author=self.author_000)


        post_000.tags.add(tag_django)
        post_000.save()

        post_001 = create_post(
            title = 'The second post',
            content = 'It is next Post!',
            author = self.author_000,
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

        #comment 있는 지 확인
        comments_div = main_div.find('div', id='comment-list')
        self.assertIn(comment_000.author.username, comments_div.text)
        self.assertIn(comment_000.text, comments_div.text)
        

        #Tag 있는 지 확인
        self.assertIn('#django', main_div.text)

        #category가 main_div에 있음
        self.assertIn(category_python.name, main_div.text)
        #edit 버튼이 로그인 하지 않으면 보이지 않음
        self.assertNotIn('EDIT', main_div.text)

        #로그인을 한 경우에
        login_success = self.client.login(username = 'Meg', password='nopassword')
        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        btn_edit = main_div.find('button', id='btn-edit')

        self.assertTrue(login_success)

        #post.author와 로그인 한 사용자가 동일하면
        self.assertEqual(post_000.author, self.author_000)

        #Edit 버튼이 나옴
        self.assertEqual('EDIT', btn_edit.text)

        #동일하지 않으면 없다
        login_success = self.client.login(username = 'Nia', password='nopassword')
        response = self.client.get(post_000_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertTrue(login_success)
        #작성자는 로그인한 사람이 아닌 다른사람인지 확인
        self.assertEqual(post_000.author, self.author_000)
        #Edit 버튼이 안나옴
        self.assertNotIn('EDIT', main_div.text)

        comment_div = main_div.find('div', id='comment-list')
        comment_000_div = comment_div.find('div', id='comment-id-{}'.format(comment_000.pk))
        self.assertIn('edit', comment_000_div.text)
        self.assertIn('delete', comment_000_div.text)

        comment_001_div = comment_div.find('div', id='comment-id-{}'.format(comment_001.pk))
        self.assertNotIn('edit', comment_001_div.text)
        self.assertNotIn('delete', comment_001_div.text)

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

    def test_tag_page(self):

        tag_django = create_tag(name='django')
        tag_java = create_tag(name='java')

        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )
        post_000.tags.add(tag_django)
        post_000.tags.add(tag_java)
        post_000.save()

        post_001 = create_post(
            title = 'The second post',
            content = 'It is next Post!',
            author = self.author_000,
            category = create_category(name='python'),
        )
        post_001.tags.add(tag_java)
        post_001.save()

        response = self.client.get(tag_django.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        
        main_div = soup.find('div', id='main-div')
        h1 = main_div.find('h1', id='blog-list-title')
        self.assertIn('#{}'.format(tag_django.name), h1.text)
        self.assertIn(post_000.title, main_div.text)
        self.assertNotIn(post_001.title, main_div.text)

    def test_post_create(self):
        response = self.client.get('/blog/create/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username = 'Meg', password='nopassword')
        self.assertEqual(response.status_code, 302)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        #self.aseertIn('New Post', main_div.text)

    def test_post_update(self):
        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )

        self.assertEqual(post_000.get_update_url(), post_000.get_absolute_url() + 'update/')

        response = self.client.get(post_000.get_update_url())
        self.assertEqual(response.status_code, 302)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        # self.assertNotIn('Created', main_div.text)
        # self.assertNotIn('Author', main_div.text)
        
    def test_new_comment(self):
        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )

        login_success = self.client.login(username = 'Meg', password='nopassword')
        self.assertTrue(login_success)

        #서버에 뭔갈 날릴땐 post, 가져올땐 get
        response = self.client.post(
            post_000.get_absolute_url() + 'new_comment/',
            {'text': 'a comment for test'}, 
            follow = True
        ) #follow는 redirect까지 포함해서 response 받는다는 뜻
        
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')
        self.assertIn(post_000.title, main_div.text)
        self.assertIn('a comment for test', main_div.text)

    def test_delete_commet(self):
        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )

        comment_000 = create_comment(post_000, text='a first comment', author=self.user_nia)
        comment_001 = create_comment(post_000, text='a second comment', author=self.author_000)

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(post_000.comment_set.count(), 2)

        # 제 3자로 로그인
        login_success = self.client.login(username='Meg', password='nopassword')
        self.assertTrue(login_success)
        # 3자가 주소를 통해 본인 댓글이 아닌걸 지우려고 하면
        response = self.client.get('/blog/delete_comment/{}/'.format(comment_000.pk), follow=True)
        # 지워지면 안됨. 그대로 2개 유지
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(post_000.comment_set.count(), 2)

        #본인이 로그인하면 지워져야함
        login_success = self.client.login(username = 'Nia', password='nopassword')
        self.assertTrue(login_success)
        response = self.client.get('/blog/delete_comment/{}/'.format(comment_000.pk), follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(post_000.comment_set.count(), 1)

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main-div')

        self.assertNotIn('Nia', main_div.text)

    def test_edit_commet(self):
        post_000 = create_post(
            title = 'The first post',
            content = 'Hello World. We are the world.',
            author = self.author_000,
        )

        comment_000 = create_comment(post_000, text='a first comment', author=self.user_nia)
        comment_001 = create_comment(post_000, text='a second comment', author=self.author_000)

        #로그인 안할때
        with self.assertRaises(PermissionError):
            response = self.client.get('/blog/edit_comment/{}/'.format(comment_000.pk))

        #로그인 매그
        login_success = self.client.login(username = 'Meg', password='nopassword')
        self.assertTrue(login_success)

        with self.assertRaises(PermissionError):
            response = self.client.get('/blog/edit_comment/{}/'.format(comment_000.pk))

        #로그인 니아
        login_success = self.client.login(username = 'Nia', password='nopassword')
        self.assertTrue(login_success)

        response = self.client.get('/blog/edit_comment/{}/'.format(comment_000.pk))
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn('Edit Comment : ', soup.body.h3)

        response = self.client.post(
            '/blog/edit_comment/{}/'.format(comment_000.pk),
            {'text': 'i edited comment'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertNotIn('a first comment', soup.body.text)
        self.assertIn('i edited comment', soup.body.text)

    def test_search(self):
        post_000 = create_post(
            title = 'hello world!',
            content = 'hi there~!',
            author = self.author_000
        )

        post_001 = create_post(
            title = 'goodbye world!',
            content = "bye there~!",
            author = self.author_000
        )

        response = self.client.get('/blog/search/hello world!/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(post_000.title, soup.body.text)
        self.assertNotIn(post_001.title, soup.body.text)

        response = self.client.get('/blog/search/bye there~!/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(post_001.title, soup.body.text)
        self.assertNotIn(post_000.title, soup.body.text)

