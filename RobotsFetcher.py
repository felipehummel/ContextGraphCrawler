import robotparser
from urlparse import urlparse
import pickle
import os
import pycurl
import StringIO
from robotexclusionrulesparser import RobotExclusionRulesParser

class RobotsFetcher:
    @staticmethod
    def can_fetch(url):
        domain = RobotsFetcher.extract_domain(url)
        robots_parser = RobotsFetcher.get_robots(domain);
        return robots_parser.is_allowed("*", url)

    @staticmethod
    def extract_domain(url):
        o = urlparse(url)
        return o.netloc

    @staticmethod
    def get_robots(url):
        robots_directory = 'robots'
        robots_file_path = robots_directory+'/'+url
        if os.path.isfile(robots_file_path):
            robots_file = open(robots_file_path,"rb")

#            robots_parser = RobotExclusionRulesParser()
#            robots_parser.parse(content)
            robots_parser = pickle.load(robots_file)
        else:
            buffer = StringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'http://'+url+'/robots.txt')
            c.setopt(c.REFERER,'')
            c.setopt(c.USERAGENT,'Curl')
            c.setopt(c.FOLLOWLOCATION, 1)
            c.setopt(c.WRITEFUNCTION, buffer.write)
            try:
                c.perform()
            except pycurl.error, e:
                print "Error code: ", e[0]
                print "Error message: ", e[1]
                c.close()
                robots_parser = RobotExclusionRulesParser()
                robots_parser.parse('')
                return robots_parser
            c.close()
#            print buffer.getvalue()
            robots_parser = RobotExclusionRulesParser()
            robots_parser.parse(buffer.getvalue())
            robots_file = open(robots_file_path,"wb")
            pickle.dump(robots_parser, robots_file)
        robots_file.close()
        return robots_parser



#robot_fetcher = RobotsFetcher()
#print robot_fetcher.can_fetch('http://www.googlediscovery.com/feed/');
#print robot_fetcher.can_fetch('http://www.googlediscovery.com/feeds/');
#print robot_fetcher.can_fetch('http://www.googlediscovery.com/trackback/');

#rp = robotparser.RobotFileParser()
#rp.set_url("http://www.googlediscovery.com/robots.txt")
#rp.read()
#print rp.can_fetch("*", "http://www.googlediscovery.com/")
#print rp.can_fetch("*", "http://www.googlediscovery.com/wp-admin/")

