#!/usr/bin/env python
from __future__ import print_function
import subprocess as sub
import argparse
import re
import gscholar
import urllib2
import os

## Gives:
##   title, subject, keywords, author, creator, producer, creationdate, 
##   moddate, tagged, form, pages, encrypted, page size, file size, optimized,
##   pdfversion
def pdfinfo(article_fname):
    text = sub.check_output(['/usr/local/bin/pdfinfo', '-enc', 'UTF-8', article_fname])
    text = text.decode('utf8')
    lines = text.splitlines()
    info = {}
    for l in lines:
        key, val = re.split(':\s*', l, 1)
        fixedkey = key.replace(' ', '').lower()
        info[fixedkey] = val
    return info
        
def extract_from_pdftext(article_fname):
    text = sub.check_output(['/usr/local/bin/pdftotext', '-enc', 'UTF-8', article_fname, '-'])
    text = text.decode('utf8')

    first100lines = '\n'.join(text.splitlines()[:100])
    doimatch = re.search('10\.[0-9]{4,}\/[^\s]*[^\s\.,]', first100lines)
    doi = doimatch.group() if doimatch is not None else ''

    abstractstring = 'Abstract\n'
    abstractindex = first100lines.find(abstractstring)
    if abstractindex != -1:
        abstractstartindex = abstractindex + len(abstractstring)
        abstractendindex = first100lines.find('\n', abstractstartindex)
        abstract = first100lines[abstractstartindex:abstractendindex]
    else:
        abstract = ''
    
    return doi, abstract

def display_info(article_fname):
    info = pdfinfo(article_fname)
    
    doi, abstract = extract_from_pdftext(article_fname)

    query_string = doi if doi else info['title']
    if query_string:
        # query google
        try:
            text = gscholar.query(query_string, gscholar.FORMAT_BIBTEX, False)[0]
            if text:
                lines = text.splitlines()
                lines.insert(1,'  doi={{{}}},'.format(doi))
                bibtex = '\n'.join(lines)
        except urllib2.URLError:
            pass

    if 'bibtex' not in locals():
        bibtex = ''

    notetitle = ''.join([info['title'],' - ',info['author']])
    notebody = '\n\n'.join([abstract, bibtex])
    insert_into_evernote(notetitle, notebody, article_fname)

def asquote(astr):
  "Return the AppleScript equivalent of the given string."
  
  astr = unicode(astr).replace(u'"', u'" & quote & "')
  astr = astr.replace('\\', '\\\\')
  return u'"{}"'.format(astr)

def insert_into_evernote(title, body, attachment):
    args = [asquote(t) for t in [title, body]]
    ascript = u"""\
tell application "Evernote"
  activate
  set note1 to create note title {} with text {} notebook "Inbox"
  open note window with note1
end tell""".format(*args)
  #tell note1 to append attachment file {}
    sub.call([u'/usr/bin/osascript', u'-e', ascript])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Take an article and insert it into Evernote')
    parser.add_argument( 'articles', nargs='+', help='articles to be inserted')
    parsed = parser.parse_args()
    for article_fname in parsed.articles:
        # TODO fix next line... duh
        fname = article_fname.replace("~", "/Users/kurt")
        machd = 'Macintosh HD'
        if fname.startswith(machd):
            fname = fname[len(machd):].replace(':','/')
        display_info(fname)
    print('Complete!')
