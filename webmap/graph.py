from py2neo import Graph
from py2neo.ogm import GraphObject, Property, RelatedTo
from graphql import GraphQLError
import graphene

# this has been a very interesting experience.

NEO4J_HOST = 'localhost'
NEO4J_PORT = 7687
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'admin'

graph = Graph(
    host=NEO4J_HOST,
    port=NEO4J_PORT,
    user=NEO4J_USER,
    password=NEO4J_PASSWORD,
)

class BaseModel(GraphObject):
    """
    Implements some basic functions to guarantee some standard functionality
    across all models. The main purpose here is also to compensate for some
    missing basic features that we expected from GraphObjects, and improve the
    way we interact with them.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def all(self):
        return self.match(graph)

    def save(self):
        graph.push(self)



class IP(BaseModel):
    __primarykey__ = 'addr'
    addr = Property()

    def fetch(self):
        ip = self.match(graph, self.addr).first()
        if ip == None:
            raise GraphQLError('')
        return ip

    def as_dict(self):
        return {
            'addr' : self.addr,
        }

class IPSchema(graphene.ObjectType):
    addr = graphene.String()

class IPInput(graphene.InputObjectType):
    addr = graphene.String(required=True)


class URL(BaseModel):
    __primarykey__ = 'domain'

    name = Property()
    domain = Property()

    ips = RelatedTo('IP', 'POINTS_TO')

    def fetch(self):
        url = self.match(graph, self.domain).first()
        if url == None:
            raise GraphQLError('')
        return url
    
    def as_dict(self):
        return {
            'domain' : self.domain,
            'name' : self.name,
            'ips' : self.ips
        }

    def __add_link(self, addr):
        ip = IP(addr=addr).fetch()
        self.ips.add(ip)        

    def associate_ip(self, addr):
        #THIS MAY BE TOO SIMPLE.
        self.__add_link(addr)

class URLSchema(graphene.ObjectType):
    name = graphene.String()
    domain = graphene.String()
    # crawl_date = graphene.DateTime()
    ips = graphene.List(IPSchema)

class URLInput(graphene.InputObjectType):
    domain = graphene.String(required=True)

    def __init__(self, **kwargs):
        self._id = kwargs.pop('_id')
        super().__init__(**kwargs)



class CreateURL(graphene.Mutation):
    class Arguments:
        domain = graphene.String(required=True)
        name = graphene.String()
    success = graphene.Boolean()
    url = graphene.Field(lambda: URLSchema)

    def mutate(self, info, **kwargs):
        url = URL(**kwargs)
        url.save()
        return CreateURL(url=url, success=True)

class CreateIP(graphene.Mutation):
    class Arguments:
        addr = graphene.String(required=True)
    success = graphene.Boolean()
    ip = graphene.Field(lambda: IPSchema)

    def mutate(self, info, **kwargs):
        ip = IP(**kwargs)
        ip.save()
        return CreateIP(ip=ip, success=True)

class ConnectURLtoIP(graphene.Mutation):
    class Arguments:
        domain = graphene.String(required=True)
        addr = graphene.String(required=True)
    success = graphene.Boolean()
    url = graphene.Field(lambda: URLSchema)
    ip = graphene.Field(lambda: IPSchema)

    def mutate(self, info, **kwargs):
        # print(kwargs)
        url = URL(domain=kwargs.pop('domain')).fetch()
        url.associate_ip(**kwargs)
        url.save()
        return ConnectURLtoIP(url=url, success=True)


class Query(graphene.ObjectType):
    url = graphene.Field(lambda: URLSchema, domain=graphene.String())
    ip = graphene.Field(lambda: IPSchema, addr=graphene.String())

    def resolve_url(self, info, domain):
        url = URL(domain=domain).fetch()
        return URLSchema(**url.as_dict())
    
    def resolve_ip(self, info, addr):
        ip = IP(addr=addr).fetch()
        return IPSchema(**ip.as_dict())

class Mutations(graphene.ObjectType):
    create_url = CreateURL.Field()
    create_ip = CreateIP.Field()
    connect_url_to_ip = ConnectURLtoIP.Field()





schema = graphene.Schema(query=Query, mutation=Mutations, auto_camelcase=False)

