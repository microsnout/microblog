from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from blog.models import Blog, Post
from bs4 import BeautifulSoup
import requests
import sys, os, os.path
import inspect

# For exceptions only - slow - Finds name of calling function
thisfunc = lambda: inspect.stack()[1][3]



class Command(BaseCommand):
    help = 'Fill a blog with CNN articles for testing'

    def _boolean_input(self, question, default=None):
        result = input("%s " % question)
        if not result and default is not None:
            return default
        while len(result) < 1 or result[0].lower() not in "yn":
            result = input("Please answer yes or no: ")
        return result[0].lower() == "y"

    def add_arguments(self, parser):
        parser.add_argument('sub-command', type=str)
        parser.add_argument('-b', '--blog', required=True, type=str)
        parser.add_argument('-n', '--number', default=5, type=int)

    def cnnfill(self, blog_slug, n, **options):
        self.stdout.write( self.style.SUCCESS( f"CNN fill: blog= '{blog_slug}' n={n}" )) 

        URL = 'http://lite.cnn.com'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        alist = soup.find_all('a')
        articles = [ a for a in alist if 'en/article' in a.attrs.get('href') ]
        
        try:
            blog = Blog.objects.get(slug=blog_slug)
            user = blog.owner
            count = 0

            self.stdout.write( self.style.WARNING( f"Will create {n} posts in blog '{blog.title}'" ))
            if not self._boolean_input( self.style.WARNING( 'Do you want to continue?' )):
                return

            for art in articles[:n]:
                apage = requests.get( URL + art.attrs.get('href') )
                asoup = BeautifulSoup(apage.content, 'html.parser')
                plist = asoup.find_all('p')
                title = art.text
                slug  = slugify(title)

                # Create body of post as max 20 paragraphs
                strList = [str(tag) for tag in plist[:20]]
                bigStr = '\n'.join(strList)

                self.stdout.write(f"CNN title={title}")

                post = Post(
                    blog= blog,
                    author= user, 
                    status= 'published',
                    title= title, 
                    slug= slug,
                    body= bigStr
                )
                post.save()
                count += 1
        except:
            raise CommandError(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
        finally:
            self.stdout.write( self.style.SUCCESS( f"CNN fill: Created {count} posts." )) 

    def clear(self, blog_slug, **options):
            try:
                deleted = 0
                blog = Blog.objects.get(slug=blog_slug)
                posts = Post.objects.filter(blog=blog)

                self.stdout.write( self.style.WARNING( f"Will delete {posts.count()} posts in blog '{blog.title}'" ))
                if not self._boolean_input( self.style.WARNING( 'Do you want to continue?' )):
                    return

                deleted, _ = posts.delete()
            except:
                raise CommandError(f"{thisfunc()}: Exception:'{sys.exc_info()[0]}'")
            finally:
                self.stdout.write( self.style.SUCCESS( f"Clear Blog: Deleted {deleted} posts." )) 


    def handle(self, *args, **options):
        cmd = options.get('sub-command', 'list')
        blog = options['blog']
        n = options.get('number', 5)
        self.stdout.write( self.style.SUCCESS( f"Microblog: command= '{cmd}' blog= '{blog}' n={n}" )) 

        if cmd == 'cnnfill':
            self.cnnfill(blog, n, **options)
            return

        if cmd == 'clear':
            self.clear(blog, **options)
            return

