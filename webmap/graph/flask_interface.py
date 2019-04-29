from py2neo import Node, Relationship, Graph
from datetime import datetime
import re


"""
Bing returns: 
    ('ip', {'1.1.1.1' : ['https://blah.com', 'https://blahblah.com', ...]})

NSLookup returns:
    ('url', {'https://blah.com' : ['1.1.1.1', '2.2.2.2', ...]})

"""


NEO4J_PASS = 'admin'

graph = Graph(auth=('neo4j', '{}'.format(NEO4J_PASS)))


class URLNode(Node):
    def create(self):
        graph.create(self)
        self.submitted = True
        
    def __init__(self, path, domain=None, create_on_instantiation=True):
        self.submitted = False
        self.path = path
        self.domain = domain
        super(URLNode, self).__init__(self.path, path=self.path, domain=self.domain)
        if create_on_instantiation:
            self.create()
        


class IPNode(Node):
    def create(self):
        graph.create(self)
        self.submitted = True
    
    def __init__(self, addr, create_on_instantiation=True):
        self.submitted = False
        self.addr = addr
        super(IPNode, self).__init__(addr, addr=self.addr)
        if create_on_instantiation:
            self.create()


class POINTSAT(Relationship):
    def create(self):
        graph.create(self)
        self.submitted = True
    
    def __init__(self, url, ip, create_on_instantiation=True):
        self.submitted = False
        self.url = url
        self.ip = ip
        assert isinstance(self.ip, IPNode)
        assert isinstance(self.url, URLNode)
        self.date = str(datetime.now())
        super(POINTSAT, self).__init__(self.url, 'POINTSAT', self.ip, timestamp=self.date)
        # if create_on_instantiation:
        #     self.create()
        graph.create(self)




class Dispatcher:
    HYPERTEXT_PREFIX_STRIPPER = r'(^https?:\/\/)(www\.)?([^\/]*)(.*)$'
    
    @classmethod
    def get_simple_domainname(cls, url_string):
            """Uses regex grouping substitution."""    
            simple_dn = re.sub(cls.HYPERTEXT_PREFIX_STRIPPER, r'\3', url_string)
            return simple_dn

    @classmethod
    def submit_bing_results(cls, dictionary):
        
        #TODO: add logging
        for ip, urls in dictionary.items():
            ip_node = IPNode(ip)
            # assert ip_node.submitted
            url_nodes = [URLNode(url, domain=cls.get_simple_domainname(url)) for url in urls]
            # assert all([node.submitted for node in url_nodes])
        for url_node in url_nodes:
            rel = POINTSAT(url_node, ip_node)
            # assert rel.submitted
            

    @classmethod
    def submit_nslookup_results(cls, dictionary):
        #TODO: add logging
        for url, ips in dictionary.items():
            url_node = URLNode(url, domain=cls.get_simple_domainname(url))
            # assert url_node.submitted
            ip_nodes = [IPNode(ip) for ip in ips]
            # assert all([node.submitted for node in ip_nodes])
        for ip_node in ip_nodes:
            rel = POINTSAT(url_node, ip_node)
            # assert rel.submitted

    @classmethod
    def submit_data(cls, input_type, dictionary):
        if input_type == 'ip':
            cls.submit_bing_results(dictionary)
        elif input_type == 'url':
            cls.submit_nslookup_results(dictionary)
        else: 
            raise ValueError()


if __name__ == "__main__":
    pass