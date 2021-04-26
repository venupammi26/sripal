import socket
import os
import subprocess
import sys
import json
from Datacenter import Datacenter
from Rack import Rack
from Node import Node
from DhcpConfig import DhcpConfig

class DatacenterCtrl:

    dc_ctrl = None
    stash_ctrl = None
    vendor_metadata = None
    ipmi_dhcp = None
    vendor_metadata_root = None
    stash_metadata_dir = None
    dc_metadata_dir = None
    service_dir = "/opt/montana/services/core/lkutils"
    service_metadata_dir = None
    ipmi_dhcp_config = None
    
    def usingDc(self, dc):
        #install script will always create this dir
        self.source_env_file(os.path.join(self.service_dir, "config/deployment-config"))

        #check what type of library install we have
        if( os.environ["INSTALL_TYPE"] != "DESKTOP" ):
            raise Exception("Non Desktop library type detected. This feature not supported. Try using DatacenterCtrl.local()")

        #create dc metadata path
        self.stash_metadata_dir = os.path.join(os.environ["STASH_METADATA_DIR"], dc)

        #create dc metadata path
        self.dc_metadata_dir = os.path.join( self.getDcMetadataPath(dc) )
        
        #check if user dc exists
        if( (not os.path.isdir( self.stash_metadata_dir )) or (not os.path.isdir( self.dc_metadata_dir )) ):
            raise Exception("specified data center does not exist in stash metadata!")

        self.service_metadata_dir = os.path.join(self.service_dir, os.path.join("config", dc))
        self.vendor_metadata_root = os.path.join(self.service_metadata_dir, "vendor_metadata")
        self.ipmi_dhcp_config = os.path.join(self.service_metadata_dir, "ipmi-dhcpd.conf" )

        #copy stash files
        self.copy_stash_files()

        self.source_env_file(os.path.join(self.service_metadata_dir, "deployment-config.cfg"))
        sys.path.append(self.service_metadata_dir)
        sys.path.append(self.dc_metadata_dir)
        self.vendor_metadata = self.get_vendor_metadata()
        self.ipmi_dhcp = self.get_ipmi_dhcp()
        self.dc_ctrl = self.get_dc_ctrl_blk( "nodemetadata" )
        self.stash_ctrl = self.get_dc_ctrl_blk( "stashmetadata" )

    def lkDcInit(self):        
        self.source_env_file(os.path.join(self.service_dir, "config/deployment-config"))
        if( os.environ["INSTALL_TYPE"] != "LK" ):
            raise Exception("Non LK library type detected. This feature not supported. Try using DatacenterCtrl.using( <dc-name> )")
        
        self.stash_metadata_dir = "/opt/montana/services/core/lkutils/config/stash"
        self.vendor_metadata_dir = os.path.join(self.stash_metadata_dir, "vendor_metadata")
        self.vendor_metadata_root = self.vendor_metadata_dir
        self.dc_metadata_dir = "/etc/montana/config"

        self.source_env_file(os.path.join(self.dc_metadata_dir, "deployment-config.cfg"))
        sys.path.append(self.stash_metadata_dir)
        sys.path.append(self.dc_metadata_dir)
        self.vendor_metadata = self.get_vendor_metadata()
        self.dc_ctrl = self.get_dc_ctrl_blk( "nodemetadata" )
        self.stash_ctrl = self.get_dc_ctrl_blk( "stashmetadata" )

    
    def __init__(self, dc):

        if( dc == "LK_DATACENTER_INIT" ):
            self.lkDcInit()
        else:
            self.usingDc( dc )


    @classmethod
    def local(cls):
        return cls("LK_DATACENTER_INIT")

    @classmethod
    def using(cls, dc):
        return cls(dc)

    def getDcMetadataPath(self, dc):
        #config file can't use '-' character for variable name
        #so replace it with '_' character
        dc = dc.replace("-","_")
        for key in os.environ:
            newKey = key.replace("NODE_METADATA_DIR_","")

            if( dc.lower() == newKey.lower() ):
                return os.environ[key]
        raise Exception("Datacenter not found: "+dc)
    
    def copy_stash_files(self):
        ret = subprocess.call(["cp", "-r", self.stash_metadata_dir, os.path.join(self.service_dir, "config")])

        if( ret != 0 ):
            raise Exception("Failed to copy stash files to service directory...")
        else:
            #move stash metadata to stashmetadata.py to differentiate
            subprocess.call(["mv", os.path.join(self.service_metadata_dir, "nodemetadata.py"), os.path.join(self.service_metadata_dir, "stashmetadata.py")])     

    '''
    Function Name: source_env_file
    Function Description: Adds environment variables to 
                      os.environ from sourcefile
    Input: sourcefile - absolute path of sourcefile
    Output: void
    '''
    def source_env_file(self, sourcefile):

        if( not os.path.isfile( sourcefile ) ):
            print "source file not found: "+sourcefile
            exit( 1 )
    
        #run the bash source cmd
        command = ['bash', '-c', "set -a && source "+sourcefile+" && env"]
        proc = subprocess.Popen(command, stdout = subprocess.PIPE)

        #read all the env vars that were sourced
        for line in proc.stdout:
            (key, _, value) = line.partition("=")
            os.environ[key] = value.rstrip()
        proc.communicate()

    def get_vendor_metadata(self):
        ret = []
        json_data = None
        for dirpath , _, files in os.walk( self.vendor_metadata_root ):
            for file in files:
                #only load json files...
                if( ".json" not in file ):
                    continue

                json_file = open( os.path.join( dirpath, file ) )

                try:
                    json_data = json.load( json_file )
                except:
                    print "ERROR: failed to load json for file: "+os.path.join( dirpath, file )
                    continue

                ret.append( json_data )

        return ret

    def get_vendor_md_entry(self, vendor_mdata, mac):
        
        for rack in vendor_mdata:
            for node in rack:
                if( "10GPort0_MAC" not in node ):
                    continue
                
                if( (mac == node["10GPort0_MAC"]) ):
                    return node
                
                if( "10GPort1_MAC" not in node ):
                    continue
                
                if( mac == node["10GPort1_MAC"] ):
                    return node
        return None

    #create ipmi dhcp config object
    def get_ipmi_dhcp(self):
        dhcpConfig = DhcpConfig( self.ipmi_dhcp_config )
        dhcpConfig.load()
        return dhcpConfig
    
    
    def get_ipmi_ip(self, vendor_md_entry):

        if( vendor_md_entry is None ):
            return "query-failed"
        
        mac = ""
        try:
            mac = vendor_md_entry["IpmiMAC"]
        except:
            return "query-failed"
        
        for entry in self.ipmi_dhcp.getEntries():
            
            if( entry.getHardware() == mac ):
                return entry.getIp()
        
        return "query-failed"
        
        

    '''
    Function Name: get_dc_ctrl_blk
    Function Description: Loads nodemetadata into an object oriented
                          usable format
    Input: void
    Output: datacenter - object containing list of Rack objects. Rack
                     objects contain list of Node objects
    '''
    def get_dc_ctrl_blk(self, metadataFile):
        datacenter = Datacenter(os.environ["LK_DC_NAME"])
        module = __import__( metadataFile )
        METADATA = getattr(module, "METADATA")

        for entry in METADATA:
            
            #find vendor metadata entry that maps to this node
            vendor_md_entry = self.get_vendor_md_entry( self.vendor_metadata, entry[0] )

            #find ipmi ip
            ipmi_ip = self.get_ipmi_ip(vendor_md_entry)

            #create new node
            newNode = Node(entry[0], int(entry[1]), int(entry[2]), entry[3], entry[4], vendor_md_entry, ipmi_ip)

            if( datacenter.hasRack(newNode.getSubnet()) ):
                #rack exists. add node to it
                rack = datacenter.getRack(newNode.getSubnet())
                rack.addNode( newNode )
            else:
                #create new rack with first new node in it
                datacenter.addRack(  Rack(newNode) )

        return datacenter

    def getDatacenterCtrl(self):
        return self.dc_ctrl

    def getStashCtrl(self):
        return self.stash_ctrl

    def getVendorMetadata(self):
        return self.vendor_metadata

