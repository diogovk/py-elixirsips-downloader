import getpass
import urllib.request as request
import http.cookiejar as cookiejar
from urllib.parse import urlencode
import re
import os


def request_setup():
  cj = cookiejar.CookieJar()
  cookieProcessor = request.HTTPCookieProcessor(cj)
  opener = request.build_opener(cookieProcessor)
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]
  request.install_opener(opener)


def download_post_files(post_url):
  req = request.Request(post_url)
  resp = request.urlopen(req)
  page = str(resp.read())
  for file_url, filename in re.findall('(/subscriber/download\?file_id=[0-9]+)">([^<]*)', page):
    if os.path.isfile(filename) and skip_existing:
      print("Skipping download of %s: File exists." % filename)
      continue
    url = base_url + file_url
    print("Please wait: downloading %s -> %s" % (url, filename))
    if os.path.isfile(filename):
      os.remove(filename + ".download")
    request.urlretrieve(url, filename=filename + ".download")
    print("%s: downloaded" % filename)
    os.rename(filename + ".download",filename)


def do_login(email, password):
  ''' Attempts to log in using given credentials returning the response object,
  which in case of successful login will contain the list with all the elixirsips posts '''
  login_url = base_url + "/subscriber/content"
  payload = {"username": email, "password": password }
  data = urlencode(payload)
  binary_data = data.encode('UTF-8')
  print("Logging in")
  req = request.Request(login_url, binary_data)
  return request.urlopen(req)


base_url = "https://elixirsips.dpdcart.com"
# set to False to force the download of existing files
skip_existing=True

request_setup()


print("To download this content you'll have to login with your elixirsips account")
login = input("Email:")
password = getpass.getpass()

resp = do_login(login, password)

posts_page = str(resp.read())

posts_paths = re.findall('/subscriber/post\?id=[0-9]+#files"', posts_page)
assert len(posts_paths) > 1, "Hmm. Could not find any posts. Wrong user/pass?"

print("Login: success")
os.makedirs('elixirsips', exist_ok=True)
os.chdir('elixirsips')


posts_paths.sort()

for post_path in posts_paths:
  download_post_files(base_url+post_path)
