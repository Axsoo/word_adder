#!/usr/bin/env python
import sys, os, json, csv
from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo, askUserDialog, askUser, getText
from aqt.qt import *
from .download_audio import audioDownload
from .download_image import imageDownload

CWD = os.getcwd() # Get our working directory
addon_config = mw.addonManager.getConfig(__name__)
ResDir = os.path.join(os.path.dirname(__file__), "resources")

#################
#  Profile data #
#################
mainDeck = addon_config['mainDeck']
subDeck = addon_config['subDeck']
model = addon_config['model']

dstKanji = addon_config['dstKanji']
dstKana = addon_config['dstKana']
dstEnglish = addon_config['dstEnglish']
dstPosition = addon_config['dstPosition']
dstAudio = addon_config['dstAudio']
dstImage = addon_config['dstImage']
dstDefinition = addon_config['dstDefinition']
dstSentence = addon_config['dstSentence']
dstFreq = addon_config['dstFreq']

##################
# Main functions #
##################

def addNote(deckName, modelName, entry):
    '''Adds entry as a note in anki 
    plus image from google and audio from 
    japanesepos101 or wanikani'''

    # Get deck and model
    deck = mw.col.decks.byName(deckName)
    modelBasic = mw.col.models.byName(modelName)
    mw.col.decks.current()['mid'] = modelBasic['id']

    # Make new note
    note = mw.col.newNote()
    note.model()['did'] = deck['id']

    # Find frequency range
    word_freq = int(entry['freq'])
    if word_freq <= 5000:
        freq_range = 'wordfreq1-5000'
    elif word_freq > 5000 and word_freq <= 10000:
        freq_range = 'wordfreq5001-10000'
    elif word_freq > 10000 and word_freq <= 15000:
        freq_range = 'wordfreq10001-15000'
    elif word_freq > 15000 and word_freq <= 20000:
        freq_range = 'wordfreq15001-20000'
    elif word_freq > 20000 and word_freq <= 25000:
        freq_range = 'wordfreq20001-25000'
    else:
        freq_range = 'wordfreq25000+'
    
    # Set tag to auto-generated and frequency range
    tags = "auto-generated" + " " + freq_range
    note.tags = mw.col.tags.canonify(mw.col.tags.split(tags))
    m = note.model()
    m['tags'] = note.tags
    mw.col.models.save(m)

    # Fields
    note[dstKanji] = entry['kanji'] # Vocabulary-Kanji-Plain
    note[dstKana] = entry['kana'] # Vocabulary-Kana
    note[dstEnglish] = entry['en'] # Vocabulary-English
    note[dstPosition] = entry['pos'] # Vocabulary-Pos
    note[dstDefinition] = entry['def'] # Sanseido
    note[dstSentence] = entry['sentence'] # Expression
    note[dstFreq] = entry['freq'] # Frequency

    # Dupe checking
    isDupe = False
    for cid in mw.col.findNotes("deck:" + "\'" + mainDeck + "\'"):
        if mw.col.getNote(cid)[dstKanji] == entry['kanji']:
            isDupe = True
            #showInfo(f"Dupe found @ {entry['kanji']}")
            break

    # Add note to collection
    if not isDupe:
        #showInfo(f"No dupe found @ {entry['kanji']}")
        addAudio(note)
        addImage(note)
        mw.col.addNote(note)
        #showInfo(f"Added {note[dstKanji]}!")

    # Save collection
    mw.col.save()


def addAudio(db_note):
    (data, file_name) = audioDownload(db_note[dstKana], db_note[dstKanji])
    # If the audio is placeholder means it is not available
    if data != None:
        mw.col.media.writeData(file_name, data)
        db_note[dstAudio] = u'[sound:{}]'.format(file_name)
        print(f"New field: {db_note[dstAudio]}")
    else:
        db_note.tags.append("no_sound")


def addImage(db_note):
    (data, file_name) = imageDownload(db_note[dstKanji])
    if data:
        image_file = '<img src="' + file_name + '" />'
        mw.col.media.writeData(file_name, data)
        db_note[dstImage] = image_file
        print(f"New field: {db_note[dstImage]}")


def getFreqList(freq_range):
    freq_list = []
    with open(os.path.join(ResDir, "final_dict.json"),"r",encoding='utf-8') as dict_file:
        data = json.load(dict_file)
    for i in freq_range:
        freq_list.append(data['reverse frequency'].get(str(i)))
    return freq_list


def getWordSentence(word):
    with open(os.path.join(ResDir, 'jpn_sentences.tsv'), encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        for row in reader:
            if word in row[2]:
                return row[2]
        return ""


def createEntry(kanji_word):
    # Open dictionary
    with open(os.path.join(ResDir, "final_dict.json"),"r",encoding='utf-8') as dict_file:
        data = json.load(dict_file) # Get data from json file
    sentence = getWordSentence(kanji_word)
    entry_dict = {  'kanji': kanji_word, \
                    'kana': data["reading"].get(kanji_word), \
                    'pos': data["vocabulary position"].get(kanji_word), \
                    'en': data["translation"].get(kanji_word), \
                    'freq': str(data["frequency"].get(kanji_word)), \
                    'def': data["definition"].get(kanji_word), \
                    'sentence': sentence}
    
    # Definition may be None if not found
    if entry_dict['def'] == None:
        entry_dict['def'] = ''

    # If no kana found the word is not in dictionary
    if entry_dict['kana'] == None:
        return None
    else:
        return entry_dict

def main():
    start = int(getText('Enter beginning of frequency range: ')[0])
    end = int(getText('Enter end of frequency range: ')[0])
    if end > start and end != 0:
        word_list = getFreqList(range(start,end))

    # Iterate list and add notes
    for word in word_list:
        entry = createEntry(word)
        if entry:
            addNote(subDeck, model, entry)
    showInfo("Done!")

action = QAction("Add words", mw)
action.triggered.connect(main)
mw.form.menuTools.addAction(action)