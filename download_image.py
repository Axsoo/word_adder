from urllib.request import urlopen, Request, urlretrieve
from urllib.parse import quote
from urllib.error import URLError
from bs4 import BeautifulSoup
import logging
import uuid
import re

REQUEST_HEADER = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

def get_extension(url):
    if 'jpg' in url:
        return 'jpg'
    elif 'png' in url:
        return 'png'
    else:
        return 'gif'

def filter_url_list(url_list):
    url_list = [value for value in url_list if 'gstatic' not in value] #Remove google icons
    url_list = [value for value in url_list if 'trans-suite' not in value]
    url_list = [value for value in url_list if 'meaning-book' not in value]
    url_list = [value for value in url_list if 'cidianwang' not in value]
    url_list = [value for value in url_list if 'moedict' not in value]
    url_list = [value for value in url_list if 'business-textbooks' not in value]
    url_list = [value for value in url_list if 'jlptsensei' not in value]
    url_list = [value for value in url_list if 'japanesetest4you' not in value]
    url_list = [value for value in url_list if 'otonasalone' not in value]
    return url_list

def imageDownload(kanji):
    # Make query url
    query = quote(kanji)
    query = '+'.join(query.split())
    url = "https://www.google.co.in/search?q=%s&source=lnms&tbm=isch" % query

    # Getting image url addresses from google
    response = urlopen(Request(url, headers=REQUEST_HEADER))
    soup = BeautifulSoup(response, 'html.parser')
    img_url_matches = re.findall(r'(?:http(?:s?):)(?:[/|.|\w|\s|-])*\.(?:jpg|gif|png)',soup.text)

    # Remove bad urls
    sorted_url_list = filter_url_list(img_url_matches)

    # Download images
    for url in sorted_url_list:
        try:
            req = Request(url, headers=REQUEST_HEADER) # make request
            resp = urlopen(req, timeout=10.0) # open response, timeout if slower than 10 sec
            raw_image = resp.read()
            extension = get_extension(url) # Generate filename
            file_name = uuid.uuid4().hex + "." + extension
            return (raw_image, file_name)
        except URLError:
            print("Authentication failed...")
        except Exception:
            print("Other exception...")
        print("Trying for next image...")
    return (None, '404.jpg') # If nothing is found

if __name__ == "__main__":
    imageDownload("隔離イラスト")

    