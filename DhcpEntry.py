class DhcpEntry:
    
    hardware = None
    ip = None

    def __init__(self, hardware, ip):
        self.hardware = hardware
        self.ip = ip
    
    def getIp(self):
        return self.ip
    
    def getHardware(self):
        return self.hardware
