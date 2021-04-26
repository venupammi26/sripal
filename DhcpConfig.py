from DhcpEntry import DhcpEntry

class DhcpConfig:
    
    dhcpFile = None
    entries = []

    def __init__(self, dhcpFile):
        self.dhcpFile = dhcpFile
        self.entries = []
        

    def load(self):
        fd = open(self.dhcpFile)
        hostBlockOpen = False
        hardware = None
        ip = None
        
        for line in fd:
            if( hostBlockOpen ):
                args = line.split()
                
                if( args[0] == "hardware" ):
                    hardware = args[2].replace(";","")
                elif( args[0] == "fixed-address" ):
                    ip = args[1].replace(";","")
            
            #if hardware and ip are ready create entry
            if( (hardware != None) and (ip != None) ):
                entry = DhcpEntry(hardware, ip)
                self.entries.append( entry )
                ip = None
                hardware = None
            
            #start of host block
            if( ("{" in line) and ("host" in line) ):
                hostBlockOpen = True
            if( ("}" in line) and (hostBlockOpen) ):
                hostBlockOpen = False


    def getEntries(self):
        return self.entries
