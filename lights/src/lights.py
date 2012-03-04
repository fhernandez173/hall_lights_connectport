#####################################################################
# This is the main project module
# Created on: 24 February 2012
# Author: Robert Diamond
# Description:
#####################################################################

web_template = """
<HEAD>
<TITLE>Light Control</TITLE>
<SCRIPT TYPE="text/javascript">
function setcolor(colordiv) {
    colordiv.style.margin = "";
    colordiv.style.border = "2px; black;";
    document.forms[0].color.value = colordiv.textContent;
    document.forms[0].submit();
}
HTMLElement.prototype.hasFocus = 0;
function updateAjax(url) {
    if (window.XMLHttpRequest) {// code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp=new XMLHttpRequest();
    } else {// code for IE6, IE5
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function() {
        if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            var x = xmlhttp.responseXML;
            var sel = document.getElementsByName("node")[0];
            var selNode = sel.options[sel.selectedIndex].value;
            var lights = x.getElementsByTagName("light");
            for (var lightno=0; lightno < lights.length; ++lightno) {
                var light = lights.item(lightno);
                if (light.attributes.getNamedItem("node").nodeValue == selNode) {
                    if (!document.getElementsByName("red")[0].hasFocus) {
                        document.getElementsByName("red")[0].value = 
                            x.getElementsByTagName("red")[0].firstChild.nodeValue;
                    }
                    if (!document.getElementsByName("green")[0].hasFocus) {
                        document.getElementsByName("green")[0].value = 
                            x.getElementsByTagName("green")[0].firstChild.nodeValue;
                    }
                    if (!document.getElementsByName("blue")[0].hasFocus) {
                        document.getElementsByName("blue")[0].value = 
                            x.getElementsByTagName("blue")[0].firstChild.nodeValue;
                    }
                    if (!document.getElementsByName("speed")[0].hasFocus) {
                        document.getElementsByName("speed")[0].value = 
                            x.getElementsByTagName("speed")[0].firstChild.nodeValue;
                    }
                    break;
                }
            }
        }
        if (xmlhttp.readyState == 4) {
            window.setTimeout("updateAjax('"+url+"')", 7000);
        }
    }
    xmlhttp.open("GET",url,true);
    xmlhttp.send();
}
</SCRIPT>
</HEAD>
<BODY onload="updateAjax(location.origin+'/query')">
<FORM METHOD="POST">
<TABLE>
<TR>
<TD>Choose Node</TD><TD><SELECT NAME="node">
%(nodes)s
</SELECT></TD>
</TR>
<TR>
<TD>Red</TD><TD><INPUT TYPE="text" NAME="red" VALUE="%(red)d" 
    onFocus="this.hasFocus = 1" onBlur="this.hasFocus=0"/></TD>
</TR>
<TR>
<TD>Green</TD><TD><INPUT TYPE="text" NAME="green" VALUE="%(green)d"
    onFocus="this.hasFocus = 1" onBlur="this.hasFocus=0"/></TD>
</TR>
<TR>
<TD>Blue</TD><TD><INPUT TYPE="text" NAME="blue" VALUE="%(blue)d"
    onFocus="this.hasFocus = 1" onBlur="this.hasFocus=0"/></TD>
</TR>
<TR>
<TD>Change Delay</TD><TD><INPUT TYPE="text" NAME="speed" VALUE="%(speed)d"
    onFocus="this.hasFocus = 1" onBlur="this.hasFocus=0"/></TD>
</TR>
<TR>
<TD>Or Choose a Predefined Color:</TD><TD>
<DIV STYLE="height:220;overflow:scroll;border:solid;">---select a color from the list---<br/>
%(colors)s
</DIV></TD>
</TR>
<TR>
<TD COLSPAN="2"><INPUT NAME="set_colors" TYPE="submit" VALUE="Set Colors"/><INPUT NAME="random" TYPE="submit" VALUE="Party Mode!"/>
<!--INPUT TYPE="submit" NAME="quit" VALUE="Stop Server" STYLE="background-color:red;"/-->
</TD>
</TR>
</TABLE>
<input type="hidden" name="color" value=""/>
</FORM>
</BODY>
"""
from colors import colors
import digiweb
import zigbee
from socket import *
import sys
import os
import select
import thread
import re

sd = None
th = None
th2 = None
recvData = {}
exitRequest = False
nodeData = {}

def serverPage(type, path, headers, args):
    if args is not None:
        if type == "POST": args = splitargs(args)
    if path == "/lights":
        return colorPage(args)
    elif path == "/query":
        return query(args)
    else:
        return (digiweb.TextHtml,"<h1>Invalid URL</h1>")

def colorPage(args):
    socketVal = {'r': 0, 'g':0, 'b':0}
    nodelist = []
    random_mode = False
    change_speed = 6
    change_speed_changed = False
    
    if args is not None:
        ignrgb = False
        for arg in args.keys():
            argkey = arg.lower()
            argval = args[arg]
            if argval is not None: argval = unquote(argval)
            print "key: "+argkey+" val: "+argval
            if not ignrgb and argkey == "red":
                socketVal['r'] = int(argval)
            elif not ignrgb and argkey == "green":
                socketVal['g'] = int(argval)
            elif not ignrgb and argkey == "blue":
                socketVal['b'] = int(argval)
            elif argkey == "speed":
                change_speed = int(argval)
                change_speed_changed = True
            elif argkey == "color":
                if colors.has_key(argval.lower()):
                    socketVal = colors[argval.lower()]
                    ignrgb = True
            elif argkey == "node":
                nodelist.append(argval)
            elif argkey == "random":
                random_mode = True
            elif argkey == "quit":
                print "Stopping server"
                sd.close()
                exitRequest = True
                sys.exit()
                return (digiweb.TextHtml, "exiting")
    
    if random_mode:
        socketdata = "n"
    else:
        socketdata = "".join([k+str(v) for k,v in socketVal.items()])
        if change_speed_changed:
            socketdata += "s"+str(change_speed)
    
    socketdata += "\n"
    print "sending "+socketdata+" to "+str(nodelist) + "\n"
        
    for node in nodelist:
        try:
            sd.sendto(socketdata, 0, (node, 0xe8, 0xc105, 0x11))
        except:
            print "Failed to send to "+node
                
    nodes = zigbee.get_node_list(False)
    nodeList = ""
    for node in nodes:
        if node.type != "end": continue 
        try:
            nodeaddr = node.addr_extended
            if not nodeData.has_key(nodeaddr):
                nodeData[nodeaddr] = {
                    "red":0, "green":0, "blue":0, "speed":0,
                    "nodeaddr":nodeaddr, "nodeId":zigbee.ddo_get_param(nodeaddr, "NI")
                }
            nodeline = "<OPTION value='"+nodeaddr+"'>"+\
                zigbee.ddo_get_param(nodeaddr, "NI")+\
                "</OPTION>"
            nodeList += nodeline
        except:
            pass
    
    colorList = ""
    ckeys = colors.keys()
    ckeys.sort()
    for c in ckeys:
        comps = colors[c]
        luma=comps['r']*.3 + comps['g']*.59 + comps['b']*.11
        if luma < 128: textcolor = 'white' 
        else: textcolor = 'black'
        colorEntry = "<DIV style=\"background-color:#%02x%02x%02x;color:%s;text-align:center;margin:2px 0px;cursor:pointer;\" onclick=\"setcolor(this)\">%s</DIV>" % (comps['r'], comps['g'], comps['b'], textcolor, c)
        colorList += colorEntry

    if len(nodelist) > 0:
        try:
            nodeaddr = nodelist[0]
            nodeData[nodeaddr]['red'] = socketVal['r']
            nodeData[nodeaddr]['green'] = socketVal['g']
            nodeData[nodeaddr]['blue'] = socketVal['b']
            if change_speed_changed:
                nodeData[nodeaddr]['speed'] = change_speed
        except:
            exctype, value = sys.exc_info()[:2]
            print "failed to update nodeData: "+str(exctype)+", "+str(value)
    elif len(nodeData) > 0:
        nodeaddr = nodeData.keys()[0]
        socketVal = { 'r': nodeData[nodeaddr]['red'],
            'g': nodeData[nodeaddr]['green'],
            'b': nodeData[nodeaddr]['blue'] }

    return (digiweb.TextHtml, web_template % {
            'red':socketVal['r'], 'green':socketVal['g'], 'blue':socketVal['b'],'speed':change_speed,
            'nodes':nodeList, 'colors':colorList })

xmlTemplate = """
<lights>
    %s
</lights>
"""
lightTemplate = """
<light node="%(nodeaddr)s">
    <red>%(red)d</red>
    <green>%(green)d</green>
    <blue>%(blue)d</blue>
    <speed>%(speed)d</speed>
    <nodeId>%(nodeId)s</nodeId>
</light>\n
"""
def query(args):
    lightData = ""
    for nodeInfo in nodeData.keys():
        lightData += lightTemplate % nodeData[nodeInfo]
    return (digiweb.TextXml, xmlTemplate % (lightData,))

def splitargs(arglist):
    ret = {}
    for arg in arglist.split("&"):
        argsp = arg.split('=')
        if len(argsp) == 1:argsp.append(None)
        ret[argsp[0]] = argsp[1]
    return ret
    
def parseQ():
    pat = "Qr(\d+)g(\d+)b(\d+)s(\d+)"
    for nodeaddr,text in recvData.items():
        match = re.search(pat, text)
        if match is not None:
            print "found match"
            try:
                if not nodeData.has_key(nodeaddr):
                    nodeData[nodeaddr] = {
                        "red":0, "green":0, "blue":0, "speed":0,
                        "nodeaddr":nodeaddr, "nodeId":zigbee.ddo_get_param(nodeaddr, "NI")
                    }
            except:
                exctype, value = sys.exc_info()[:2]
                print "failed to add node: "+str(exctype)+", "+str(value)
                continue
            recvData[nodeaddr] = ""
            nodeData[nodeaddr]['red'] = int(match.group(1))
            nodeData[nodeaddr]['green'] = int(match.group(2))
            nodeData[nodeaddr]['blue'] = int(match.group(3))
            nodeData[nodeaddr]['speed'] = int(match.group(4))

def monitor_read(sock):
    rlist = [sock]
    while not exitRequest:
        select.select(rlist, [], [])
        payload, addr = sock.recvfrom(8192)
        print "received "+payload+" from "+str(addr)+"\n"
        if not recvData.has_key(addr[0]):
            recvData[addr[0]] = payload
        else:
            recvData[addr[0]] += payload
        parseQ()
            
        if len(recvData[addr[0]]) > 500:
            recvData[addr[0]] = recvData[addr[0]][-500:]
    print "goodbye from monitor_read\n"
    
def query_params(sock):
    print "starting query params\n"
    import time
    while not exitRequest:
        try:
            nodes = zigbee.get_node_list(True)
            for n in nodes:
                print "sending query to "+n.addr_extended
                sock.sendto("Q\n", 0, (n.addr_extended, 0xe8, 0xc105, 0x11))
        except:
            exctype, value = sys.exc_info()[:2]
            print "failed to query node: "+str(exctype)+", "+str(value)
        time.sleep(10)
    print "goodbye from query_params\n"

def unquote(str):
    str = str.replace('+',' ')
    str = re.sub('%[\da-fA-F]{2}', lambda(x) : chr(int(x.group(0)[1:],16)), str)
    return str

if __name__ == "__main__":
    sd = socket(AF_XBEE, SOCK_DGRAM, XBS_PROT_TRANSPORT)
    sd.bind(("", 0xe8, 0, 0))
    sd.setblocking(0)

    th = thread.start_new(monitor_read, (sd,))
    th2 = thread.start_new(query_params, (sd,))
    
    hnd = digiweb.Callback(serverPage)
    
    print "ready"
    while True: pass
   