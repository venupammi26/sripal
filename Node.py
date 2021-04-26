import os

class Node:
    
    mac = ""
    id = 0
    rack = 0
    nodeStor = ""
    data = ""
    vendor_metadata = None
    ipmi_ip = ""

    def __init__(self, mac, rack, id, nodeStor, data, vendor_metadata, ipmi_ip):
        self.mac = mac
        self.rack = rack
        self.id = id
        self.nodeStor = nodeStor
        self.data = data
        self.vendor_metadata = vendor_metadata
        self.ipmi_ip = ipmi_ip

    def getMac(self):
        return self.mac

    def hasPort1Mac(self):
        return (self.mac == self.getVendor10GMac(1) )

    def getId(self):
        return self.id
    
    def getNodeStor(self):
        return self.nodeStor

    def getData(self):
        return self.data
    
    def getRack(self):
        return self.rack
    
    def getBlock(self):
        if( self.id < 64 ):
            return 1
        else:
            return 2

    def getIp(self):
        return "10."+str(self.rack)+"."+str(self.id)+".1"

    def getIpmiIp(self):
        return self.ipmi_ip

    def getSubnet(self):
        ipbytes = self.getIp().split(".")
        netmaskbytes = os.environ["SUBNET_MASK"].split(".")

        ret = ""

        for i in range( len(ipbytes) ):
            byte = int(ipbytes[i]) & int(netmaskbytes[i])
            ret = ret + str(byte)

            if( i < 3 ):
                ret = ret + "."
        return ret

    def getGateway(self):
        subnetbytes = self.getSubnet().split(".")
        return subnetbytes[0] + "." + subnetbytes[1] + "." + subnetbytes[2] + "." + str((int(subnetbytes[3]) + 1))

    def getStorageRole(self):
        if( self.data == "" ):
            return "NONE"
        
        vars = self.data.split(",")
        return vars[7].split("=")[1]

    def getHardwareVendor(self):
        if( self.data == "" ):
            return "NONE"
        
        vars = self.data.split(",")
        model = ""
        for attribute in vars:
            keyval = attribute.split("=")

            if( len(keyval) < 2 ):
                continue

            if( keyval[0].lower() == "nodemodel" ):
                model = keyval[1]
                break
        
        #FYI: this check might not work for UTF8 characters
        if( ("radisys" in model.lower()) or ("DCE-SSLED-V2-3-001".lower() in model.lower()) ):
            return "RADISYS"
        elif( "dell" in model.lower() ):
            return "DELL"
        else:
            return model
    
    def getEcsCluster(self):
        if( self.data == "" ):
            return "NULL"
        if( "ECSCluster" not in self.data ):
            return "NULL"
        
        vars = self.data.split(",")
        ecsCluster = ""
        for attribute in vars:
            keyval = attribute.split("=")

            if( len(keyval) < 2 ):
                continue

            if( keyval[0].lower() == "ecscluster" ):
                ecsCluster = keyval[1]
                break;

        if( ecsCluster == "" ):
            raise Exception("ECSCluster key/val error!")

        return ecsCluster
    
    def getAttribute(self, attribute):
        
        if( self.data == "" ):
            return "NULL"
        
        vars = self.data.split(",")
        ret = ""
        for attr in vars:
            keyval = attr.split("=")

            if( len(keyval) < 2 ):
                continue
            
            if( keyval[0].lower() == attribute.lower() ):
                return keyval[1]

        #now check if its a vendor metadata attribute
        try:
            return self.vendor_metadata[attribute]
        except:
            return "NULL"

    def getVendorMetadata(self):
        return self.vendor_metadata

    def hasVendorMetadata(self):
        return (self.vendor_metadata is not None)

    def getVendorSerialNumber(self):
        if( self.vendor_metadata is not None ):
            try:
                return self.vendor_metadata["SerialNo"]
            except:
                return "query-failed"
        else:
            return "query-failed"

    def getVendorRackID(self):
        if( self.vendor_metadata is not None ):
            try:
                return self.vendor_metadata["RackID"]
            except:
                return "query-failed"
        else:
            return "query-failed"

    def getVendorSlotID(self):
        if( self.vendor_metadata is not None ):
            try:
                return self.vendor_metadata["SlotID"]
            except:
                return "query-failed"
        else:
            return "query-failed"
    
    def getVendorMachineID(self):
        if( self.vendor_metadata is not None ):
            try:
                return self.vendor_metadata["MachineID"]
            except:
                return "query-failed"
        else:
            return "query-failed"

    def getVendorIpmiMac(self):
        if( self.vendor_metadata is not None ):
            try:
                return self.vendor_metadata["IpmiMAC"]
            except:
                return "query-failed"
        else:
            return "query-failed"
    
    def getVendorMgmtMac(self):
        if( self.vendor_metadata is not None ):
            try:
                return self.vendor_metadata["MgmtMAC"]
            except:
                return "query-failed"
        else:
            return "query-failed"

    def getVendorNodeType(self):
        if( self.vendor_metadata is not None ):
            try:
                return self.vendor_metadata["NodeType"]
            except:
                return "query-failed"
        else:
            return "query-failed"

    def getVendor10GMac(self, port):
        if( self.vendor_metadata is not None ):
            if( port == 0 ):
                try:
                    return self.vendor_metadata["10GPort0_MAC"]
                except:
                    return "query-failed"
            elif( port == 1 ):
                try:
                    return self.vendor_metadata["10GPort1_MAC"]
                except:
                    return "query-failed"
            else:
                raise IndexError("10G Mac port index out of bounds")
        else:
            return "query-failed"
    
        


