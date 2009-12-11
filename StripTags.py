import sgmllib, string
import re

class StrippingParser(sgmllib.SGMLParser):

    # These are the HTML tags that we will leave intact
    valid_tags = ('b', 'a', 'i', 'br', 'p')

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if string.lower(k[0:2]) != 'on' and string.lower(v[0:10]) != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = '</%s>' % tag
            self.endTagList.insert(0,endTag)
            self.result = self.result + '>'

    def unknown_endtag(self, tag):
        if tag in self.valid_tags:
            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag
            self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
                self.result = self.result + self.endTagList[j]


    def strip_tags(self,str):
        """Remove all tags from a String using regular expression"""
        from re import sub
        buffer = list(str)
        i=0
        for charac in buffer:
            if charac == '\n':
                buffer[i] = ' '
            i=i+1
        str = ''.join(buffer)

        str_stripped = sub('<script.*?>.*?</script>', '', str)
        str_stripped = sub('<style.*?>.*?</style>', '', str_stripped)
        str_stripped = sub('<[^>]*="javascript:[^"]*"[^>]*>','',str_stripped)
        str_stripped = sub('<!DOCTYPE html PUBLIC.*?>','',str_stripped)
        str_stripped = sub('<!--.*-->','',str_stripped)
        return sub('</?\w+[^\>]*>', '', str_stripped)

    def strip(self,html_tostrip):
        """ Strip illegal HTML tags from string str """
        new_string = re.sub('\t\t', '', self.strip_tags(html_tostrip))
        new_string = re.sub('  ', ' ', new_string)
        new_string = re.sub('\t ', ' ', new_string)
        new_string = re.sub(' \t', ' ', new_string)
#        parser.feed(str)
#        parser.close()
#        parser.cleanup()
        return new_string

