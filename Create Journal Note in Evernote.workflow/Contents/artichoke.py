#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import subprocess as sub
import argparse
import re
import gscholar
import urllib2
import os

def is_title_like(s):
    return not re.search('\\.\w{3,4}$', s)

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
        if fixedkey == 'title' and not is_title_like(val):
            continue
        if val:
            info[fixedkey] = val
    return info
        
def extract_from_pdftext(article_fname, guess=False):
    text = sub.check_output(['/usr/local/bin/pdftotext', '-enc', 'UTF-8', article_fname, '-'])
    text = text.decode('utf8')

    results = {}
    splitlines = text.splitlines()
    first_100_lines = '\n'.join(splitlines[:100])
    doimatch = re.search('10\.[0-9]{4,}\/[^\s]*[^\s\.,]', first_100_lines)
    if doimatch:
        results['doi'] = doimatch.group()

    abstract_re = u'^abstract[^a-zA-Z]+'
    match = re.search(abstract_re, first_100_lines, re.IGNORECASE|re.MULTILINE) #I: ignore case
    if match:
        start_index = match.end()
        end_index = first_100_lines.find('\n', start_index)
        abstract = first_100_lines[start_index:end_index].strip()
        results['abstract'] = abstract
    
    if guess:
        for i, l in enumerate(splitlines[:5]):
            if (re.search('study|method|tour|analysis', l, re.IGNORECASE) and 
                    len(l) < 400):
                title_guess1 = splitlines[i]
                results['title'] = title_guess1
                break
    return results

def update_info_with_bibtex(info, bibtex, keys, replace = False):
    for key in keys:
        val = gscholar._get_bib_element(bibtex, key)
        if val and (replace or key not in info):
            info[key] = val

def display_info(fpath):
    if not os.path.exists(fpath):
        raise IOError('File Not Found')
    info = pdfinfo(fpath)
    
    guessed_data = ['title', 'author']
    guess = not all(guess in info for guess in guessed_data)
    info_from_text = extract_from_pdftext(fpath, guess)
    for k in info_from_text:
        if k not in info or (k is 'title' and not is_title_like(info[k])):
            info[k] = info_from_text[k]

    query_string = info['doi'] if 'doi' in info else (
            info['title'] if 'title' in info else 
            info['abstract'] if 'abstract' in info else 
            None)

    bibtex = ''
    if query_string: # query google
        try:
            query_string = query_string.encode('ascii','replace')
            text = gscholar.query(query_string.decode('utf8', 'replace'), gscholar.FORMAT_BIBTEX, False)
            if text:
                text = text[0] # assume the first one
                lines = text.splitlines()
                if 'doi' in info:
                    lines.insert(1,'  doi={{{}}},'.format(info['doi']))
                bibtex = '\n'.join(lines)
        except urllib2.URLError:
            pass

    if bibtex:
        update_info_with_bibtex(info, bibtex, guessed_data, True)

    notetitle = ''.join([info.get('title', 'Unknown Title'),
        ' - ', info.get('author', 'Authors Unknown')])
    if guess:
        notetitle += ' METADATA NEEDS REVIEW'

    notebody = u''
    if 'abstract' in info:
        notebody += info['abstract'] + u'\n\n'
    if bibtex:
        notebody += bibtex.decode('utf8') + u'\n\n'

    insert_into_evernote(notetitle, notebody, fpath)

def asquote(astr):
  "Return the AppleScript equivalent of the given string."
  astr = unicode(astr).replace(u'"', u'" & quote & "')
  astr = astr.replace('\\', '\\\\')
  return u'"{}"'.format(astr)

def insert_into_evernote(title, body, attachment):
    args = [asquote(t) for t in [body, attachment, title]]
    ascript = u"""\
tell application "Evernote"
  activate
  set note1 to create note with text {}
  append note1 attachment {}
  set title of note1 to {}
end tell""".format(*args)
    #this should work, but it doesn't for some reason
    sub.call([u'/usr/bin/osascript', u'-e', ascript])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Take an article and insert it into Evernote')
    parser.add_argument( 'articles', nargs='+', help='articles to be inserted')
    parsed = parser.parse_args()
    for fpath in parsed.articles:
        display_info(fpath)
    print('Complete!')
