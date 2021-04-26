class Datacenter:
    
    racks = []
    name = ""
    
    def __init__(self, name):
        self.name = name
        self.racks = []

    def addRack(self, rack):
        self.racks.append( rack )

    def getRack(self, subnet):
        for rack in self.racks:
            if( rack.getSubnet() == subnet ):
                return rack

    def getRacks(self):
        return self.racks

    def hasRack(self, subnet):
        for rack in self.racks:
            if( rack.getSubnet() == subnet ):
                return True
        return False

    def getName(self):
        return self.name

    def getNode(self, mac):
        for rack in self.racks:
            for node in rack.getNodes():
                if( node.getMac() == mac ):
                    return node
        return None
