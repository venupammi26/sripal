



#!{PYTHON_LOCATION}

import os
import sys
import argparse
import subprocess
from lkutils.lkmetadata import DatacenterCtrl

def getParser(argv):
    parser = argparse.ArgumentParser(description='mbrowser parser')

    #if in the future we want to add support to run on LK DC we will need to make this
    #option 'required=False'
    parser.add_argument('--dc-name', action="store", dest="dcName", required=True)
    parser.add_argument('--list-machines', action="store_true", dest="listMachines", default=False, required=False)
    parser.add_argument('--list-racks', action="store_true", dest="listRacks", default=False, required=False)
    parser.add_argument('--storage-role', action="store", dest="storageRole", required=False)
    parser.add_argument('--ecs-cluster', action="store", dest="ecsCluster", required=False)
    parser.add_argument('--ecs-racks', action="store", dest="ecsRacksCluster", required=False)
    parser.add_argument('--validate', action="store_true", dest="validate", required=False)
    parser.add_argument('--attribute', action="store", dest="attribute", required=False)
    parser.add_argument('--publish', action="store", dest="publish", metavar="vzid password", nargs="+",default=False, required=False)

    return parser

def printNodeEntry(node):
    ipmiMac = None
    mgmtMac = None
    machineID = None
    ipmiMac = None
    nodeType = None
    nodeSlot = None
    serialNumber = None

    try:
        ipmiMac = node.getVendorIpmiMac()
    except:
        ipmiMac = "query failed"

    try:
        mgmtMac = node.getVendorMgmtMac()
    except:
        mgmtMac = "query failed"

    try:
        machineID = node.getVendorMachineID()
    except:
        machineID = "query failed"

    try:
        serialNumber = node.getVendorSerialNumber()
    except:
        serialNumber = "query failed"

    try:
        nodeSlot = node.getVendorSlotID()
    except:
        nodeSlot = "query failed"

    try:
        nodeType = node.getVendorNodeType()
    except:
        nodeType = "query failed"


    if( node.hasPort1Mac() ):
        #print "(WARN: using port 1 mac) "+node.getMac()+", "+node.getIp()+", "+node.getNodeStor()+", "+node.getData()+", serialno="+serialNumber+", slot="+nodeSlot+", machineID="+machineID+", ipmiMac="+ipmiMac+", ipmiIp="+node.getIpmiIp()+", nodeType="+nodeType
         print "(WARN: using port 1 mac) "+node.getMac()+", "+node.getIp()+", "+node.getNodeStor()+", "+node.getData()+", serialno="+serialNumber+", slot="+nodeSlot+", machineID="+machineID+", ipmiMac="+ipmiMac+", nodeType="+nodeType
    else:
        #print ""+node.getMac()+", "+node.getIp()+", "+node.getNodeStor()+", "+node.getData()+", serialno="+serialNumber+", slot="+nodeSlot+", machineID="+machineID+", ipmiMac="+ipmiMac+", ipmiIp="+node.getIpmiIp()+", nodeType="+nodeType
        print ""+node.getMac()+", "+node.getIp()+", "+node.getNodeStor()+", "+node.getData()+", serialno="+serialNumber+", slot="+nodeSlot+", machineID="+machineID+",  ipmiIp="+node.getIpmiIp()+", nodeType="+nodeType

def printRackEntry(rack):
    #get vendor rack ID
    someNode = rack.getNodes()[0]

    #print rack entry
    #print "rack: "+str(rack.getId())+" vendor-rackid: "+someNode.getVendorRackID()+" subnet: "+rack.getSubnet() + " gateway: "+rack.getGateway() + " numNodes: "+str(len(rack.getNodes()))
    print 'rack: {:3d} vendor-rackID: {:12s} subnet: {} gateway: {} numNodes: {:2d}'.format(rack.getId(), someNode.getVendorRackID(), rack.getSubnet(), rack.getGateway(), len(rack.getNodes()))

def printEcsRack(rack, ecsCluster):

    headerPrinted = False

    for node in rack.getNodes():
        if( node.getEcsCluster() == ecsCluster ):
            if( not headerPrinted):
                print '\nRack: {:12s}'.format(rack.getNodes()[0].getVendorRackID())
                print "="*(6 + len(rack.getNodes()[0].getVendorRackID()))
                headerPrinted = True
            #print '\tmac: {:17s} ip: {:12s} ecsCluster: {:5s} ipmiIp: {:12s}'.format(node.getMac(), node.getIp(), node.getEcsCluster(), node.getIpmiIp())
            print '\tmac: {:17s} ip: {:12s} ecsCluster: {:5s} '.format(node.getMac(), node.getIp(), node.getEcsCluster())

    #possibly discover how much storage is on each node + total storage

def printRackWithAttribute(rack, attribute):

    headerPrinted = False
    keyval = attribute.split("=")
    if( len(keyval) < 2 ):
        raise Exception("--attribute must contain key/val pair <attr=val>")


    for node in rack.getNodes():
        if( node.getAttribute( keyval[0]) == keyval[1] ):
            if( not headerPrinted ):
                print '\nRack: {:12s}'.format(rack.getNodes()[0].getVendorRackID())
                print "="*(6 + len(rack.getNodes()[0].getVendorRackID()))
                headerPrinted = True
            #print '\tmac: {:17s} ip: {:12s} {}: {} ipmiIp: {:12s}'.format(node.getMac(), node.getIp(), keyval[0], keyval[1], node.getIpmiIp())
            print '\tmac: {:17s} ip: {:12s} {}: {} '.format(node.getMac(), node.getIp(), keyval[0], keyval[1])

def printNodeError(node):
        print 'mac: {}, ip: {:12s} storageRole: {:12s} ecsCluster: {:5s} serialno: {} rackID: {:12s} vendorNodeType: {:10s}'.format(node.getMac(), node.getIp(), node.getStorageRole(), node.getEcsCluster(), node.getVendorSerialNumber(), node.getVendorRackID(), node.getVendorNodeType())

def printNodeErrorWithMessage(errStr, node):
    print 'ERROR: {:80s} mac: {}, ip: {:12s} storageRole: {:12s} ecsCluster: {:5s} serialno: {} rackID: {:12s} vendorNodeType: {:10s}'.format(errStr, node.getMac(), node.getIp(), node.getStorageRole(), node.getEcsCluster(), node.getVendorSerialNumber(), node.getVendorRackID(), node.getVendorNodeType())


def printNodeWarningWithMessage(errStr, node):
    print 'WARNING: {:80s} mac: {}, ip: {:12s} storageRole: {:12s} ecsCluster: {:5s} serialno: {} rackID: {:12s} vendorNodeType: {:10s}'.format(errStr, node.getMac(), node.getIp(), node.getStorageRole(), node.getEcsCluster(), node.getVendorSerialNumber(), node.getVendorRackID(), node.getVendorNodeType())

def queryVendorData(vNode, fieldName):
    try:
        return vNode[fieldName]
    except:
        return "query-failed"

def printVendorNodeMissing(vNode):
    serialNo = queryVendorData(vNode, "SerialNo")
    rackID = queryVendorData(vNode, "RackID")
    slotID = queryVendorData(vNode, "SlotID")
    machineID = queryVendorData(vNode, "MachineID")
    ipmiMac = queryVendorData(vNode, "IpmiMAC")
    mgmtMac = queryVendorData(vNode, "MgmtMAC")
    nodeType = queryVendorData(vNode, "NodeType")
    v10gMac = queryVendorData(vNode, "10GPort0_MAC")

    #print '10gmac: {:17s} serialno: {:14s} rackid: {:12s} slotid: {:12s} machineid: {:20s} ipmimac: {:17s} mgmtmac: {:17s} nodetype: {:10s}'.format(v10gMac, serialNo, rackID, slotID, machineID, ipmiMac, mgmtMac, nodeType)
    print '10gmac: {:17s} serialno: {:14s} rackid: {:12s} slotid: {:12s} machineid: {:20s}  mgmtmac: {:17s} nodetype: {:10s}'.format(v10gMac, serialNo, rackID, slotID, machineID, mgmtMac, nodeType)


def checkMissingVendorNodes(dc_ctrl, vendor_metadata):
    print "\nNODES FOUND IN VENDOR METADATA BUT NOT IN NODEMETADATA"
    print "--------------------------------------------------------"

    #now check vendor metadata against live data (for missing nodes)
    for rack in vendor_metadata:
        for node in rack:
            if( "10GPort0_MAC" not in node ):
                continue

            dcNode = dc_ctrl.getNode( node["10GPort0_MAC"] )

            if( dcNode is None ):
                #check if its using port 1
                if( "10GPort1_MAC" not in node ):
                    continue

                dcNode = dc_ctrl.getNode( node["10GPort1_MAC"] )
                if( dcNode is None ):
                    printVendorNodeMissing(node)

def macExists(checkNode, seenMacs):

    for mac in seenMacs:
        if( checkNode.getMac() == mac ):
            return True
    return False

def checkDuplicateMacs(dc_ctrl):

    print "\nCHECKING FOR DUPLICATE MAC ADDRESSES IN NODEMETADATA"
    print "---------------------------------------------------------"
    seenMacs = []
    for rack in dc_ctrl.getRacks():
        for node in rack.getNodes():
            if( macExists( node, seenMacs ) ):
                printNodeError(node)
            else:
                seenMacs.append( node.getMac() )

def checkNodesWithoutVendorMetadata(dc_ctrl):

    print "\nCHECKING NODES FOR MISSING VENDOR METADATA"
    print "--------------------------------------------"

    for rack in dc_ctrl.getRacks():
        for node in rack.getNodes():

            #Dell won't have vendor metadata
            if( node.hasVendorMetadata() or (node.getHardwareVendor() == "DELL") ):
                continue
            else:
                printNodeError(node)


def checkNodeMetadataWithVendor(dc_ctrl):

    print "\nCOMPARING NODEMETADATA TO VENDOR METADATA"
    print "--------------------------------------------"


    #first check if live metadata matches vendor metadata
    for rack in dc_ctrl.getRacks():
        for node in rack.getNodes():

            #Only check if there is vendor metadata
            if( node.hasVendorMetadata() ):
                if( (node.getMac() != node.getVendor10GMac( 0 )) and (node.getMac() != node.getVendor10GMac(1)) ):
                    printNodeErrorWithMessage("vendor mac '"+node.getVendor10GMac(0)+"' mismatch", node)
                elif( node.hasPort1Mac() ):
                    printNodeWarningWithMessage("Node using 10G port 1", node)
                #if( (node.getStorageRole() == "NONE") and (node.getEcsCluster() == "NONE") and (node.getVendorNodeType() == "Storage") ):
                 #   printNodeError("vendor metadata shows node type storage but not declared in nodemetadata.py", node)
               # if( ((node.getStorageRole() != "NONE") and (node.getVendorNodeType() != "Storage"))
                #    or ((node.getEcsCluster() != "NONE") and (node.getVendorNodeType() != "Storage"))):
                 #   printNodeError("vendor metadata shows non-storage -- nodemetadata.py shows storage", node)

def checkNodeMetadataWithStash(dc_ctrl, stash_ctrl):

    print "\nCOMPARING LIVE NODEMETADATA TO STASH NODEMETADATA"
    print "----------------------------------------------"

    #go through from live side first
    for rack in dc_ctrl.getRacks():
        for node in rack.getNodes():

            stash_node = stash_ctrl.getNode( node.getMac() )

            if( stash_node is None ):
                printNodeErrorWithMessage("live node not found in stash", node)
                continue

            if( node.getStorageRole() != stash_node.getStorageRole() ):
                printNodeErrorWithMessage("StorageRole mismatch", node)

            if( node.getEcsCluster() != stash_node.getEcsCluster() ):
                printNodeErrorWithMessage("EcsCluster mismatch", node)

            if( node.getIp() != stash_node.getIp() ):
                printNodeErrorWithMessage("IP address mismatch", node)

    #now check from stash side
    for rack in stash_ctrl.getRacks():
        for node in rack.getNodes():

            liveNode = dc_ctrl.getNode( node.getMac() )

            if( liveNode is None ):
                printNodeErrorWithMessage("stash node not found in live nodemetadata", node)

def validateMetadata(dc_ctrl, stash_ctrl, vendor_metadata):

    checkNodesWithoutVendorMetadata(dc_ctrl)
    #checkNodeMetadataWithVendor(dc_ctrl)
    #checkMissingVendorNodes(dc_ctrl, vendor_metadata)
    checkNodeMetadataWithStash(dc_ctrl, stash_ctrl)
    checkDuplicateMacs(dc_ctrl)

def checkDevopsBranchUpdated(noprint):

    command = ["bash", "-c", "cd "+os.environ["STASH_METADATA_DIR"]+" && git rev-parse --abbrev-ref HEAD"]

    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    branch = proc.stdout.read()
    branch = branch.rstrip()

    if( branch == "development" ):
        return True
    else:
        if( noprint ):
            return False
        else:
            print "\n\n***WARNING***: Devops Repo currently on branch '"+branch+"'. Please use development branch."
            return False
    proc.communicate()

def updateDevopsRepo():
    print "Running git pull origin development on devops repo"
    command = ["bash", "-c", "cd "+os.environ["STASH_METADATA_DIR"]+" && git pull origin development"]
    proc = subprocess.Popen(command)
    proc.communicate()

def publishNodeEntry(node, file):
    try:
        nodeSlot = node.getVendorSlotID()
    except:
        nodeSlot = "query failed"
    try:
        nodeType = node.getVendorNodeType()
    except:
        nodeType = "query failed"
    '''file.write(
        "" + node.getMac() + ", " + node.getIp() + ", " + node.getIpmiIp() + ", " + nodeType + ", " + nodeSlot + ", " +
        node.getData().split(",")[1].split("=")[1])
    file.write("\n")'''
    
    file.write(
        "" + node.getMac() + ", " + node.getIp() + ", " + nodeType + ", " + nodeSlot + ", " +
        node.getData().split(",")[1].split("=")[1])
    file.write("\n")

def main(argv):

    parser = getParser(argv)
    args = parser.parse_args(argv[1:])

    #either user is running on desktop or on LK dc
    #if they dont use dcname and they're on their desktop
    #then lkmetadata lib will throw exception explaining
    if( args.dcName is not None ):
        #try:
        dcMain = DatacenterCtrl.using(args.dcName)
       # except:
        #    print "Running mbrowser on LK datacenter. Cannot specify --dc-name in this environment"
         #   exit(1)
    else:
        try:
            dcMain = DatacenterCtrl.local()
        except:
            print "Desktop version requires user specified datacenter name (--dc-name <dc-name>)"
            exit(1)

    dc_ctrl = dcMain.getDatacenterCtrl()
    stash_ctrl = dcMain.getStashCtrl()
    vendor_metadata = dcMain.getVendorMetadata()

    #only pull origin development if thats the branch the repo is on
    #otherwise just print warning message at bottom of output...maybe they meant to be in this state
    if( checkDevopsBranchUpdated(True) ):
        updateDevopsRepo()

    if( args.listMachines ):

        if( args.storageRole is not None ):

            for rack in dc_ctrl.getRacks():
                for node in rack.getNodes():
                    if( node.getStorageRole() == args.storageRole ):
                        printNodeEntry(node)

        else:

            for rack in dc_ctrl.getRacks():
                for node in rack.getNodes():
                    printNodeEntry(node)
    elif (args.publish):
        file = "/tmp/" + args.dcName + ".txt"
        f = open(file, "w")
        #f.write("" "MAC" + ", " + "IP" + ", " + "IPMI IP" + ", " + "Node Type" + ", " + "Slot" + ", " + "Rack")
        f.write("" "MAC" + ", " + "IP" + ", " + "Node Type" + ", " + "Slot" + ", " + "Rack")
        f.write("\n")
        for rack in dc_ctrl.getRacks():
            for node in rack.getNodes():
                publishNodeEntry(node, f)
        f.close()
        if (args.dcName == "twinsburg"):
            url = '/133763321/child/attachment/att133763323/data'
        elif (args.dcName == "arlington"):
            url = '/133763388/child/attachment/att133763390/data'
        elif (args.dcName == "omaha"):
            url = '/133763394/child/attachment/att133763419/data'
        elif (args.dcName == "perryman"):
            url = '/133763396/child/attachment/att133763422/data'
        elif (args.dcName == "rocklin"):
            url = '/133763402/child/attachment/att133763520/data'
        else:
            parser.print_help()
        command = 'curl -u '+str(args.publish[0]+':'+args.publish[1])+' -X POST -H "X-Atlassian-Token: nocheck" -F "file=@'+str(file)+'"'+ ' -F "comment=This is my updated File" -F "minorEdit=false" https://confluence.verizon.com/rest/api/content'+url
        subprocess.check_output(command, shell=True)
    elif( args.listRacks and ( args.attribute is not None ) ):
        for rack in dc_ctrl.getRacks():
            printRackWithAttribute(rack, args.attribute)
    elif( args.listRacks ):

        for rack in dc_ctrl.getRacks():
            printRackEntry(rack)
    elif( args.ecsCluster is not None ):
        for rack in dc_ctrl.getRacks():
            for node in rack.getNodes():
                if( node.getEcsCluster() == args.ecsCluster ):
                    if( node.hasPort1Mac() ):
                        #print '\t(WARN: using port 1 mac) mac: {:17s} ip: {:12s} ecsCluster: {:5s} ipmiIp: {:12s}'.format(node.getMac(), node.getIp(), node.getEcsCluster(), node.getIpmiIp())
                        print '\t(WARN: using port 1 mac) mac: {:17s} ip: {:12s} ecsCluster: {:5s} '.format(node.getMac(), node.getIp(), node.getEcsCluster())
                    else:
                        #print '\tmac: {:17s} ip: {:12s} ecsCluster: {:5s} ipmiIp: {:12s}'.format(node.getMac(), node.getIp(), node.getEcsCluster(), node.getIpmiIp())
                        print '\tmac: {:17s} ip: {:12s} ecsCluster: {:5s} '.format(node.getMac(), node.getIp(), node.getEcsCluster())
    elif( args.ecsRacksCluster is not None ):
        for rack in dc_ctrl.getRacks():
            printEcsRack( rack, args.ecsRacksCluster )
    elif( args.validate ):
        validateMetadata(dc_ctrl, stash_ctrl, vendor_metadata)
    elif( args.attribute is not None ):

        keyval = args.attribute.split("=")
        if( len(keyval) < 2 ):
            raise Exception("--attribute must contain key/val pair <attr=val>")

        for rack in dc_ctrl.getRacks():
            for node in rack.getNodes():
                value = node.getAttribute( keyval[0] )
                if(  value == keyval[1] ):
                    if( node.hasPort1Mac() ):
                        #print '\t(WARN: using port 1 mac) mac: {:17s} ip: {:12s} ipmiIp: {:12s} {:12s}: {:12s}'.format(node.getMac(), node.getIp(), node.getIpmiIp(), keyval[0], value)
                        print '\t(WARN: using port 1 mac) mac: {:17s} ip: {:12s}  {:12s}: {:12s}'.format(node.getMac(), node.getIp(),  keyval[0], value)
                    else:
                        #print '\tmac: {:17s} ip: {:12s} ipmiIp: {:12s} {:12s}: {:12s}'.format(node.getMac(), node.getIp(), node.getIpmiIp(), keyval[0], value)
                        print '\tmac: {:17s} ip: {:12s}  {:12s}: {:12s}'.format(node.getMac(), node.getIp(), keyval[0], value)
    #if user just specified --storagerole then assume --listmachines
    elif( args.storageRole is not None ):
        for rack in dc_ctrl.getRacks():
            for node in rack.getNodes():
                if( node.getStorageRole() == args.storageRole ):
                    printNodeEntry(node)
    else:
        parser.print_help()


main( sys.argv )
checkDevopsBranchUpdated(False)
