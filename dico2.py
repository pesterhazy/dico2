# test

from twisted.application import internet, service
from twisted.web import server

from Dico import toplevel

root = toplevel.ToplevelResource()
application = service.Application('web')
site = server.Site(root)
sc = service.IServiceCollection(application)
i = internet.TCPServer(8001, site)
i.setServiceParent(sc)
