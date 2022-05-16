import xml.sax
import subprocess
import mwparserfromhell
import re
import os

# Function where ContentHandler looks for opening and closing tags title and text 
# and adds characters enclosed within them to the buffer
# content saved to a dict with tag as key

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []
        self._counter = 0
        self._flag = True

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'id', 'text', 'timestamp'):         #do we need timestamp?
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            #print(name, self._buffer)
            if self._current_tag == "id": 
                if self._flag:
                    self._values[name] = ' '.join(self._buffer)
                    self._flag = False
            else:
                self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            self._flag = True
            self._pages.append((self._values['title'], self._values['id'], self._values['text']))
            #print(self._pages[-1])

data_path = r"/storage/corpora/wikipedia/el/elwiki-20220401-pages-articles-multistream.xml.bz2"
# Object for handling xml
handler = WikiXmlHandler()

# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

#lst = []

counter = 0

# Iterating through compressed file
for i, line in enumerate(subprocess.Popen(['bzcat'], stdin = open(data_path), stdout = subprocess.PIPE).stdout):
    
    parser.feed(line)
    
    #if len(handler._pages) > 70000:
    #    break
    counter += 1
    if counter % 10000 == 0:
        print("Current loop:", counter) 
# Create title list and append only titles (element 0 of tuples in wikified_dishes)

title_lst = [el[0] for el in wikified_dishes]

# Create id list and append only ids (el 1 of tuples in wikified_dishes)

id_lst = [el[1] for el in wikified_dishes]

# Create text list and append only texts (element 2 of tuples in wikified_dishes)

text_lst = [el[2] for el in wikified_dishes]

# Parse text list

text_lst = [mwparserfromhell.parse(text) for text in text_lst]

# Clean texts

text_lst = [text.strip_code().strip() for text in text_lst]

# Clean texts from 'Note' until the end and other undeleted tags with regex

clean_text_lst = [re.sub(r"(== Note == | ==Note== )\n *(.)*", "", el, flags=re.DOTALL) for el in text_lst]
clean_text_lst = [re.sub(r"( < ref > | < /ref > )", "", el) for el in clean_text_lst]
clean_text_lst = [re.sub(r"<[^>]+>", "", el) for el in clean_text_lst]

# Join title and text

wiki = ['\n'.join(x) for x in zip(title_lst, clean_text_lst)]
# Write texts in txt files with id as title

path = '/home/akorre/wiki_files/el'

for el, article in zip(wikified_dishes, wiki):
    ids = el[1]
    article = article
    file = f'{ids}.txt'
    if not any(ban in el[0] for ban in ["/", "Κατηγορία:"]): 
        with open(os.path.join(path, file), 'w+') as f:
            f.write(f'{article}')

#print(os.listdir(path))
       
      
