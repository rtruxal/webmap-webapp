from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from py2neo import Relationship, Node
from py2neo import Graph
import re
from datetime import datetime

graph = Graph(auth=('neo4j', 'admin'))

POINTS_AT = Relationship.type('POINTS_AT')

class IP(GraphObject):
    __primarykey__ = "addr"

    addr = Property()
    sites = RelatedFrom("URL", "POINTS_AT")

class URL(GraphObject):
    __primarykey__ = "path"

    path = Property()
    domain = Property()

    points_at = RelatedTo(IP)



class Dispatcher:
    HYPERTEXT_PREFIX_STRIPPER = r'(^https?:\/\/)(www\.)?([^\/]*)(.*)$'
    @staticmethod
    def try_get_node(nodetype, **kwargs):
        return graph.nodes.match(nodetype, **kwargs).first()

    @classmethod
    def get_or_create(cls, node_type, new_node, **kwargs):
        old_node = cls.try_get_node(node_type, **kwargs)
        if old_node:
            return old_node
        else:
            graph.create(new_node)
            return new_node
    
    @classmethod
    def get_simple_domainname(cls, url_string):
            """Uses regex grouping substitution."""    
            simple_dn = re.sub(cls.HYPERTEXT_PREFIX_STRIPPER, r'\3', url_string)
            return simple_dn

    @classmethod
    def submit_bing_results(cls, dictionary):
        #TODO: add logging
        for ip, urls in dictionary.items():
            ip_node = Node('IP', addr=ip)
            ip_node = cls.get_or_create('IP', ip_node, addr=ip)
            url_nodes = [cls.get_or_create('URL', Node('URL', path=url, domain=cls.get_simple_domainname(url)), path=url, domain=cls.get_simple_domainname(url)) for url in urls]
        for url_node in url_nodes:
            # rel = Relationship(url_node,'POINTS_AT', ip_node, timestamp=datetime.now().isoformat())
            rel = Relationship(url_node,'POINTS_AT', ip_node)
            
            graph.create(rel)
            


    @classmethod
    def submit_nslookup_results(cls, dictionary):
        #TODO: add logging
        for url, ips in dictionary.items():
            url_node = Node('URL', path=url, domain=cls.get_simple_domainname(url))
            url_node = cls.get_or_create('URL', url_node, path=url, domain=cls.get_simple_domainname(url))
            ip_nodes = [cls.get_or_create('IP', Node('IP', addr=ip), addr=ip) for ip in ips]
        for ip_node in ip_nodes:
            # rel = Relationship(url_node, 'POINTS_AT', ip_node, timestamp=datetime.now().isoformat())
            rel = Relationship(url_node, 'POINTS_AT', ip_node)
            graph.create(rel)


    @classmethod
    def submit_data(cls, input_type, dictionary):
        if input_type == 'ip':
            cls.submit_bing_results(dictionary)
        elif input_type == 'url':
            cls.submit_nslookup_results(dictionary)
        else: 
            raise ValueError()


if __name__ == "__main__":
    url1 = Node('URL', path='https://fake.com', domain='fake.com')
    url2 = Node('URL', path='https://fake.org', domain='fake.org')
    ip = Node("IP", addr='1.1.1.1')
    # graph.create(url1 | url2 | ip)
    # print(try_get_node('IP', addr='1.1.1.1').first())
    print(try_get_node('IP', addr='1.1.1.2').first())