from py2neo import Node, Relationship, Graph
from datetime import datetime


NEO4J_PASS = 'admin'

graph = Graph(auth=('neo4j', '{}'.format(NEO4J_PASS))


class URLNode:
    def __init__(self, path, domain=None):
        self.path = path
        self.domain = domain
        try:
            return self.create()
        except:
            return False
    
    def create(self):
        graph.create(Node(path, path=path, domain=domain))
        return True


class IPNode:
    def __init__(self, addr):
        self.addr = addr
        try:
            return self.create()
        except:
            return False
    
    def create(self):
        graph.create(Node(addr, addr=addr))
        return True


class PointsAt:
    def __init__(self, url, ip):
        try:
            self.url = url
            self.ip = ip
            assert isinstance(ip, IPNode)
            assert isinstance(url, URLNode)
            self.date = str(datetime.now())
            return self.create()
        except:
            return False

    def create(self):
        graph.create(Relationship(self.url, 'POINTSAT', self.ip, timestamp=self.date) ))
        return True

if __name__ == "__main__":
    pass