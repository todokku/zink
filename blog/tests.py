
#
# Zink
#

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from blog.models import Tag


import logging
logger = logging.getLogger('elevenbits')


class TagTestCase(TestCase):

    def setUp(self):
        self.linux = Tag.objects.create(tag="linux")
        self.nginx = Tag.objects.create(tag="nginx")

    def test_tag_creation(self):
        self.assertEqual(self.linux.tag, 'linux')
        self.assertEqual(self.nginx.tag, 'nginx')


class BlogTest(TestCase):

    fixtures = ['static', 'contact', 'treemenus', 'menu_extras', 'blog']

    def setUp(self):
        pass

    def testBlog(self):
        client = Client()
        response = client.get(reverse('blog:blog'))
        self.assertContains(response, "Welcome to our blog")
        self.assertContains(response, "Blog Categories")
        self.assertContains(response, '/">Java</a>')

    def testTag(self):
        client = Client()
        response = client.get(reverse('blog:tag', args=[4]))  # django
        self.assertContains(response, "<title>Tags - elevenbits</title>")
        self.assertContains(response, "2 entries tagged with")
        self.assertContains(response, "Django")
        self.assertContains(response, "Blog Categories")
        self.assertContains(response, '/">Java</a>')

    def testTag(self):
        client = Client()
        # get the 'how to access cherokee-admin...' entry
        response = client.get(reverse('blog:detail', args=[21]))
        self.assertContains(response, 'How to access cherokee-admin')

    def testPageTag(self):
        client = Client()
        # page 1
        response = client.get(reverse('blog:tagpage', args=[6, 1]))  # linux
        self.assertContains(response, 'How to access cherokee-admin')
        self.assertContains(response, 'Howto merge PDF documents')
        self.assertContains(response, 'How to ask questions the smart way')
        # page 2
        response = client.get(reverse('blog:tagpage', args=[6, 2]))  # linux
        self.assertContains(response, 'My first own blog!')
        self.assertContains(response, 'Howto create your own Ubuntu')

    def testInactiveTag(self):
        """Only active tags must be shown."""
        client = Client()
        response = client.get(reverse('blog:tag', args=[7]))  # python
        self.assertContains(response, 'Eclipse and Django development setup')
        self.assertContains(response, 'My first own blog!')
        # the inactive one must not be there!
        self.assertNotContains(response, 'Temporary entry')

    def testMarkup(self):
        """Make sure the codehilite works."""
        client = Client()
        response = client.get(reverse('blog:detail', args=[21]))
        self.assertContains(response, '<div class="codehilite"><pre>'
                                      '<span class="gp">')

    # TODO: this must be somewhere else
    def test404(self):
        client = Client()
        response = client.get("/this_page_does_not_exist")
        self.assertContains(response, "404 message", status_code=404)