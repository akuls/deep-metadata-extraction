from __future__ import division
from __future__ import print_function

import codecs
from xml.sax import make_parser, ContentHandler
from xml.sax.handler import feature_namespaces, feature_external_ges
from pdf_objects import *

# SAX content handler to assemble words and lines from the characters, print them to the specified file
# TODO: update this to use the same preproccessing as the word embeddings (same tokenization, replace unicode with ascii)
class ParsTrueViz(ContentHandler):

    def __init__(self, doc):
        # pass in empty document object
        self.doc = doc
        self.cur_page = None
        self.cur_zone = None
        self.cur_line = None
        self.cur_word = None
        self.wordText = ""
        self.word_label = None
        self.num_pages = 0
        self.num_zones = 0
        self.num_lines = 0
        self.num_words = 0
        self.bb_type = "" # keep track of whether the current vertices mark a zone, line, or word bounding box
        self.num_vert = 0 # keep track of whether this is the first or second vertex in a bounding box

    def startElement(self, name, attrs):
        ## PAGE ELELMENT HANDLERS
        if name == 'Page':
            self.num_pages += 1
            # set the id to be the current number of pages, update it with given id later
            self.cur_page = Page()

        elif name == 'PageID':
            self.cur_page.id = attrs.get('Value')

        ## ZONE ELEMENT HANDLERS
        elif name == 'Zone':
            self.num_zones += 1
            self.cur_zone = Zone()

        elif name == 'ZoneID':
            self.cur_zone.id = attrs.get('Value')

        elif name == 'ZoneCorners':
            # mark the bounding box as a zone box
            self.bb_type = "zone"

        elif name == 'Category' and not self.cur_zone is None:
            # if we see a classification label, apply it to the current zone and store it til we see a new one
            self.word_label = attrs.get('Value')
            self.cur_zone.label = self.word_label

        ## LINE ELEMENT HANDLERS
        elif name == 'Line':
            self.num_lines += 1
            self.cur_line = Line()
            self.cur_line.label = self.word_label

        elif name == 'LineID':
            self.cur_line.id = attrs.get('Value')

        elif name == 'LineCorners':
            # mark the bounding box as a line box
            self.bb_type = "line"

        ## WORD ELEMENT HANDLERS
        elif name == 'Word':
            self.num_words += 1
            self.cur_word = Word()
            self.cur_word.label = self.word_label

        elif name == 'WordID':
            self.cur_word.id = attrs.get('Value')

        elif name == 'WordCorners':
            # mark the bounding box as a line box
            self.bb_type = "word"

        ## CHARACTER ELEMENT HANDLERS
        # append character text to the current word
        elif name == 'GT_Text':
            self.wordText += attrs.get('Value', "")

        elif name == 'CharacterCorners':
            self.bb_type = 'char'

        ## BOUNDING BOX HANDLERS
        elif name == 'Vertex':
            # todo I think these are stored as strings, we probably want them as doubles
            (x, y) = (float(attrs.get('x')), float(attrs.get('y')))
            if self.bb_type == 'zone' and self.num_vert == 0:
                self.cur_zone.top_left = (x, y)
                self.num_vert += 1
            elif self.bb_type == 'zone' and self.num_vert == 1:
                self.cur_zone.bottom_right = (x, y)
                self.num_vert = 0
            elif self.bb_type == 'line' and self.num_vert == 0:
                self.cur_line.top_left = (x, y)
                self.num_vert += 1
            elif self.bb_type == 'line' and self.num_vert == 1:
                self.cur_line.bottom_right = (x, y)
                self.num_vert = 0
            elif self.bb_type == 'word' and self.num_vert == 0:
                self.cur_word.top_left = (x, y)
                self.num_vert += 1
            elif self.bb_type == 'word' and self.num_vert == 1:
                self.cur_word.bottom_right = (x, y)
                self.num_vert = 0

    def endElement(self, name):
        ## PAGE ELELMENT HANDLERS
        if name == 'Page':
            self.doc.addPage(self.cur_page)

        ## ZONE ELEMENT HANDLERS
        elif name == 'Zone':
            self.cur_page.addZone(self.cur_zone)


        ## LINE ELEMENT HANDLERS
        elif name == 'Line':
            self.cur_zone.addLine(self.cur_line)

        ## WORD ELEMENT HANDLERS
        elif name == 'Word':
            self.cur_word.text = self.wordText
            self.wordText = ""
            self.cur_line.addWord(self.cur_word)


def parse_doc(doc_path):
    parser = make_parser()
    parser.setFeature(feature_namespaces, False)
    parser.setFeature(feature_external_ges, False)

    # todo come up with docid
    doc = Document()
    dh = ParsTrueViz(doc)

    parser.setContentHandler(dh)
    parser.parse(doc_path)
    return doc

def main():
    doc = parse_doc('C:\Users\Molly\Google_Drive\spring_17\deep-metadata-extraction\\grotoap\grotoap2\\dataset\\00\\1276794.cxml')
    # print(doc.getFullText())
    # print()
    print(doc.toString())
    print("\nWORDS\n")
    words = doc.words()
    print("\nLINES\n")
    lines = doc.lines()
    print("\nZONES\n")
    zones = doc.zones()

    print(words[0].text)
    print("top left vertex: ",words[0].top_left)
    print("bottom right vertex: ",words[0].bottom_right)
    print("shape: ",words[0].shape())
    print("width: ", words[0].width())
    print("height: ",words[0].height())
    print("center: ",words[0].centerpoint())

if __name__ == '__main__':
    main()