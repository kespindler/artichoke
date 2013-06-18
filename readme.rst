Hey, if any of you use Evernote and read a lot of Journal articles, you might find the Mac Service that I just created to be somewhat useful.

https://github.com/kespindler/artichoke

Install it, right-click a journal article PDF, click the Service, then hit Cmd+C to copy the doc. In a moment, Evernote will pop up with a new Note containing the metadata for the PDF. Title, Author,  Abstract, Bibtex citation. Now Cmd+V  to attach the document to Evernote.

Install Instructions
--------------------

Download this, double-click it, and Mac OS should give you the option to install it. Do that.

The only requirement is xpdf, which can be installed with brew. See http://mxcl.github.io/homebrew/ for instructions on installing brew. Then, do a ``brew install xpdf`` and you'll be golden. Start throwing all your journal articles in Evernote.

If you find bugs, have feedback, etc, I'd love to hear it. Enjoy! Especially if you find PDFs this doesn't work on, that'd be awesome.

Known Bugs
----------
- Doesn't work for every PDF. I'm working on this, but I'd love to hear your reports. :)
- The Evernote notebook that I import to is hardcoded to be "Inbox". This is easy enough to change if you edit the python file, ``artichoke/Create Journal Note in Evernote.workflow/Contents/artichoke.py``. Towards the end of that is an AppleScript that, if you're just changing the Notebook name, should be easy enought to piece together.

- It seems like this doesn't work, period, if you install Evernote.app from the Apple App Store. (Reason  seems to be that sandboxing forbids the AppleScript script to access the PDF. Leave it to Apple to break backwards-compatibility..) Solution: Download your copy of Evernote from them directly.
