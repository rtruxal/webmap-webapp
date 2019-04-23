from py2neo import Graph
from py2neo.ogm import GraphObject, Property, RelatedTo
from graphql import GraphQLError
import graphene


NEO4J_HOST = 'localhost'
NEO4J_PORT = 7687
NEO4J_USER = 'neo4j'
NEO4J_PASSWORD = 'Passw0rd1!'

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
        return self.select(graph)

    def save(self):
        graph.push(self)



class IP(BaseModel):
    __primarykey__ = 'addr'
    addr = Property()

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
        url = self.select(graph, self.domain).first()
        if url == None:
            raise GraphQLError('')
    
    def ad_dict(self):
        return {
            'domain' : self.domain,
            'name' : self.name,
        }


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

class Query(graphene.ObjectType):
    url = graphene.Field(lambda: URLSchema, domain=graphene.String())
    ip = graphene.List(lambda: IPSchema)

    def resolve_url(self, info, domain):
        url = URL(domain=domain).fetch()
        return URLSchema(**url.as_dict())
    
    def resolve_ip(self, info):
        return [IPSchema(**ip.as_dict()) for ip in IP().all]




schema = graphene.Schema(query=Query, auto_camelcase=False)

