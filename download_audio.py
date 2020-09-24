from urllib.request import urlopen, Request, URLError, urlretrieve, HTTPError
from urllib.parse import quote
from bs4 import BeautifulSoup
import logging
import hashlib
import re

BASE_URL = 'http://assets.languagepod101.com/dictionary/japanese/audiomp3.php?kanji='
WANI_URL = 'https://www.wanikani.com/vocabulary/'

def audioDownloadWani(kanji):
    kanji = re.sub('<[^<]+?>', '', kanji) # Remove trailing html
    url = WANI_URL + quote(kanji)

    """ Souping for mp3-files """
    try:
        response = urlopen(Request(url))
    except HTTPError:
        print(f'Exception occured returning (None,None)...')
        return (None,None)
    soup = BeautifulSoup(response, 'html.parser')
    mp3_url_matches = re.findall(r'(?:http(?:s?):)(?:[/|.|\w|\s|-])*\.(?:mp3)',str(soup))

    """ Check for matches """
    if mp3_url_matches:
        url = mp3_url_matches[0] # Choose the first mp3 available (lady voice)
    else:
        return (None,None)
    
    """ Create the file name """
    filename = u'wanikani_{}'.format(kanji)
    filename += u'.mp3'

    """ Get file from url """
    try:
        resp = urlopen(url)
        raw_sound = resp.read()
        return (raw_sound, filename)
    except URLError:
        print(f'Exception occured returning (None,None)...')
        return (None,None)

def audioDownloadYomi(kana, kanji):
    kana = re.sub('<[^<]+?>', '', kana) # Remove trailing html
    kanji = re.sub('<[^<]+?>', '', kanji) # Remove trailing html
    url = BASE_URL + quote(kanji)

    """ Create the file name """
    filename = u'yomichan_{}'.format(kana)
    if kanji:
        filename += u'_{}'.format(kanji)
    filename += u'.mp3'
    if kana:
        url += u'&kana={}'.format(quote(kana))

    """ Get file from url """
    try:
        resp = urlopen(url)
        raw_sound = resp.read()
        return (raw_sound, filename)
    except URLError:
        print(f'Exception occured returning (None,None)...')
        return (None,None)

def audioIsPlaceholder(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest() == '7e2c2f954ef6051373ba916f000168dc'

def audioDownload(kana, kanji):
    (sound_data, filename) = audioDownloadYomi(kana,kanji) # Test downloading from Yomichan
    if audioIsPlaceholder(sound_data):
        (sound_data, filename) = audioDownloadWani(kanji) # Test downloading from wanikani
        if sound_data == None:
            return (None, None) # No sound found Wanikani
        else:
            return (sound_data, filename) # Sound found for Wanikani
    else:
        return (sound_data, filename) # Sound found for Yomichan

if __name__ == "__main__":
    print("testing...")
    audioDownload('おとこ','男')
    audioDownload('ちょうしゅ','聴取')
    audioDownload('test', 'hej')
    audioDownload('いつごろ', 'いつ頃')
    audioDownload('はくしてっかい', '白紙撤回')
    


