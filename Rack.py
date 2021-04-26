class Rack:
    
    #id is old naming convention (ie. 2nd byte of ip)
    #the real identifier is subnet though
    id = -1
    subnet = ""
    gateway = ""
    
    nodes = []

    def __init__(self, node):
        self.id = node.getRack()
        self.subnet = node.getSubnet()
        self.gateway = node.getGateway()
        self.nodes = []
        self.nodes.append( node )
    
    def addNode(self, node):
        self.nodes.append(node)

    def getId(self):
        return self.id

    def getSubnet(self):
        return self.subnet

    def getGateway(self):
        return self.gateway
    
    def getNodes(self):
        return self.nodes

    def hasClevOS(self):
        for node in self.nodes:
            if( node.getStorageRole() == "SLICESTOR" ):
                return True
        return False
