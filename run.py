#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import cherrypy
from cherrypy.process import plugins, servers
from cherrypy.process.plugins import Daemonizer
import platform
import os
import time
import json
#
cur_dir = os.path.dirname(os.path.abspath(__file__))

class Index(object):
    @cherrypy.expose 
    def index(self):
        return "hello cherrypy"

class Node(object):
    
    '''
    uri /node/dist/
    '''
    @cherrypy.expose
    def dist(self):
        dist_json = ''
        sysinstaller = ''
        installer = ''
        ostype = platform.dist()
        if(ostype[0] in ['Ubuntu','debian','ubuntu','Debian']):
            sysinstaller = 'apt-get'
            installer = 'dpkg'
        elif (ostype[0] in ['SuSE']):
            sysinstaller = 'zypper'
            installer = 'rpm'
        elif (ostype[0] in ['CentOS', 'centos', 'redhat','RedHat']):
            sysinstaller = 'yum'
            installer = 'rpm'
        
        machine = platform.machine()
        hostname = platform.node()

        dist_json = {
            'os.system':ostype[0],
            'os.version':ostype[1],
            'os.release':ostype[2],
            'os.sysinstall':sysinstaller,
            'os.installer':installer,
            'os.arch':machine,
            'os.hostname':hostname,
        }
        
        return json.dumps(dist_json, sort_keys=False, indent=4, separators=(',', ': '))
    
    '''
    uri /node/GetCpuInfo/ 
    '''
    @cherrypy.expose
    def GetCpuInfo(self):
        cpu = []
        cpuinfo = {} 
        f = open("/proc/cpuinfo")
        lines = f.readlines()
        f.close()

        for line in lines:
            if line == '\n':
                cpu.append(cpuinfo)
                cpuinfo = {}
            if len(line) < 2: continue
            name = line.split(':')[0].strip().replace(' ','_')
            var = line.split(':')[1].strip()
            cpuinfo[name] = var

        return json.dumps(cpu, sort_keys=False, indent=4, separators=(',', ': '))

    '''
    uri /node/GetMemInfo/
    '''
    @cherrypy.expose
    def GetMemInfo(self):
        mem = {}
        f = open("/proc/meminfo")
        lines = f.readlines()
        f.close()
        
        for line in lines:
            if len(line) < 2:
                continue
            name = line.split(':')[0]
            var = line.split(':')[1].split()[0]
            mem[name] = long(var)*1024.0
        mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
        return json.dumps(mem, sort_keys=False, indent=4, separators=(',', ': '))

    '''
    uri /node/GetLoadAvg/
    '''
    @cherrypy.expose
    def GetLoadAvg(self):
        loadavg = {}
        f = open("/proc/loadavg") 
        load = f.read().split()
        f.close()
        
        loadavg['lavg_1']=load[0]
        loadavg['lavg_5']=load[1]
        loadavg['lavg_15']=load[2]
        loadavg['nr']=load[3]
        loadavg['last_pid']=load[4]

        return json.dumps(loadavg, sort_keys=False, indent=4, separators=(',', ': '))

    '''
    uri /node/GetIfInfo/centos7_interface
    '''
    @cherrypy.expose
    def GetIfInfo(self, interface):
        f = open("/proc/net/dev")
        lines = f.readlines()
        f.close()

        intf = {}

        for line in lines:
            con = line.split()
            offset = con[0].split(':')
            if str(offset[0]) == interface:
                intf['interface'] = str(offset[0])
                intf['ReceiveBytes'] = str(offset[1])
                intf['ReceivePackets'] = str(con[1])
                intf['ReceiveErrs'] = str(con[2])
                intf['ReceiveDrop'] = str(con[3])
                intf['ReceiveFifo'] = str(con[4])
                intf['ReceiveFrames'] = str(con[5])
                intf['ReceiveCompressed'] = str(con[6])
                intf['ReceiveMulticast'] = str(con[7])
                intf['TransmitBytes'] = str(con[8])
                intf['TransmitPackets'] = str(con[9])
                intf['TransmitErrs'] = str(con[10])
                intf['TransmitDrop'] = str(con[11])
                intf['TransmitFifo'] = str(con[12])
                intf['TransmitFrames'] = str(con[13])
                intf['TransmitCompressed'] = str(con[14])
                intf['TransmitMulticast'] = str(con[15])

                return json.dumps(intf, sort_keys=False)

    '''
    get the traffic from net dev
    '''
    @cherrypy.expose
    def GetIfTraffic(self):           
        ifs = []
        nettraffic = {}
        f = open("/proc/net/dev")
        lines = f.readlines()
        f.close()
        
        for line in lines[2:]:
            con = line.split()
            ifname = con[0].split(':') 
            if(ifname[0].strip() != 'lo'):
                ifs.append(ifname[0].strip())
            else:
                continue
        for interface in ifs:
            nettraffic[interface] = self.GetIfInfo(interface)

        return json.dumps(nettraffic)
        
    '''
    get the infomation of df -h
    uri /node/GetHddInfo/
    '''
    @cherrypy.expose
    def GetHddInfo(self):
        hdds = []
        mount = {}
        file_system = []
        type = []
        size = []
        used = []
        avail = []
        used_percent = []
        mounted_on = []
        hdds = os.popen('df -lhT  | grep -v tmpfs | grep -v boot | grep -v usr | grep -v tmp | sed \'1d;/ /!N;s/\\n//;s/[ ]*[ ]/\\t/g;\'').readlines()
        for line in hdds:
            dict = {}
            file_system = line.replace('\\n','').replace('\\t',' ').split()[0]
            dict['type'] = line.replace('\\n','').replace('\\t',' ').split()[1]
            dict['size'] = line.replace('\\n','').replace('\\t',' ').split()[2]
            dict['used'] = line.replace('\\n','').replace('\\t',' ').split()[3]
            dict['avail'] = line.replace('\\n','').replace('\\t',' ').split()[4]
            dict['used_percent'] = line.replace('\\n','').replace('\\t',' ').split()[5]
            dict['mounted_on'] = line.replace('\\n','').replace('\\t',' ').split()[6]
            dict['file_system'] = file_system
            mount[file_system] = dict

        return json.dumps(mount) 

    '''
    get cpu usage
    uri /node/GetCpuDetail/
    '''
    @cherrypy.expose
    def GetCpuDetail(self):
        dist_json = self.dist()
        dist = json.loads(dist_json)
        if(dist['os.system'] in ['CentOS', 'centos', 'redhat', 'RedHat']):
            if(int(dist['os.version'].split('.')[0])  < 6):  #For CentOS only 
                cmd = 'mpstat 1 1 | sed \'1d;2d;3d;4d\' | awk \'{print "{\\\"user\\\":\\\"\"$3\"\\\",\\\"nice\\\":\\\"\"$4\"\\\",\\\"sys\\\":\\\"\"$5\"\\\",\\\"iowait\\\":\\\"\"$6\"\\\",\\\"irq\\\":\\\"\"$7\"\\\",\\\"soft\\\":\\\"\"$8\"\\\",\\\"steal\\\":\\\"\"$9\"\\\",\\\"idle\\\":\\\"\"$10\"\\\"}"}\''
            else:
                cmd = 'mpstat 1 1 | sed \'1d;2d;3d;4d\' | awk \'{print "{\\\"user\\\":\\\"\"$3\"\\\",\\\"nice\\\":\\\"\"$4\"\\\",\\\"sys\\\":\\\"\"$5\"\\\",\\\"iowait\\\":\\\"\"$6\"\\\",\\\"irq\\\":\\\"\"$7\"\\\",\\\"soft\\\":\\\"\"$8\"\\\",\\\"steal\\\":\\\"\"$9\"\\\",\\\"idle\\\":\\\"\"$12\"\\\"}"}\''
        else:
            cmd = 'mpstat 1 1 | sed \'1d;2d;3d;4d\' | awk \'{print "{\\\"user\\\":\\\"\"$3\"\\\",\\\"nice\\\":\\\"\"$4\"\\\",\\\"sys\\\":\\\"\"$5\"\\\",\\\"iowait\\\":\\\"\"$6\"\\\",\\\"irq\\\":\\\"\"$7\"\\\",\\\"soft\\\":\\\"\"$8\"\\\",\\\"steal\\\":\\\"\"$9\"\\\",\\\"idle\\\":\\\"\"$11\"\\\"}"}\''
        cpu = os.popen(cmd).readline().strip()
        return cpu


    '''
    get /proc/net/ip_vs_stats
    '''
    @cherrypy.expose
    def GetLvsStatsSumm(self):
        stats = {}
        conns = []
        in_pks = []
        out_pks = []
        in_bytes = []
        out_bytes = []
        
        f = open("/proc/net/ip_vs_stats")
        lines = f.readlines()
        f.close()

        conns.append(int(lines[2].split()[0], 16)) 
        in_pks.append(int(lines[2].split()[1], 16))
        out_pks.append(int(lines[2].split()[2], 16))
        in_bytes.append(int(lines[2].split()[3], 16))
        out_bytes.append(int(lines[2].split()[4], 16))

        stats = {"conns":conns,"in_pks":in_pks,"out_pks":out_pks,"in_bytes":in_bytes,"out_bytes":out_bytes}
        return json.dumps(stats, sort_keys=False, indent=4, separators=(',', ': '))

    '''
    get lvs rs stats
    uri /node/GetLvsConn/
    '''
    @cherrypy.expose
    def GetLvsConn(self):
        Conn = []
        node_list = []
        dict = {}
        num = 0
        cmd = "ipvsadm -ln"
        lines = os.popen(cmd).readlines()

        for line in lines[3:]:
            num += 1
            con = line.split()
            if con[0] == "TCP" or con[0] == "UDP":
                if num == 1:
                    pass
                else:
                    Conn.append(dict)
                dict = {}
                dict['lb_algo'] =  str(con[2])
                dict['vip'] = str(con[1])
                dict['node'] = []
                continue
            node_dict = {"rs":con[1],"lb_kind":con[2],"weight":con[3],"activeconn":con[4],"inactconn":con[5]}
            dict['node'].append(node_dict)
            if num == len(lines[3:]):
                Conn.append(dict)
        
        return json.dumps(Conn, sort_keys=False, indent=4, separators=(',', ': '))

    '''
    get GetLvsStatus
    uri /node/GetLvsStatus
    '''
    @cherrypy.expose
    def GetLvsStatus(self):
        Conn = []
        node_list = []
        dict = {}
        num = 0
        cmd = "ipvsadm -ln"
        lines = os.popen(cmd).readlines()
        for line in lines[3:]:
            num += 1
            con = line.split()
            if con[0] == "TCP" or con[0] == "UDP":
                if num == 1:
                    pass
                else:
                    Conn.append(dict)
                dict = {}
                dict['lb_algo'] = str(con[2])
                dict['vip'] = str(con[1])
                dict['node'] = []
                continue
            node_dict = {"rs":con[1],"lb_kind":con[2],"weight":con[3]}
            dict['node'].append(node_dict)
            if num == len(lines[3:]):
                Conn.append(dict)
        
        return json.dumps(Conn, sort_keys=False, indent=4, separators=(',', ': '))

    @cherrypy.expose
    def GetLvsTraffic(self):
        result = json.loads(open(os.path.join(cur_dir, 'data/', 'lvstraffic')).read())
        return json.dumps(result, sort_keys=False, indent=4, separators=(',', ': '))
            
























#

if "__main__" == __name__:
    settings = {
                'global': {
                    'server.socket_port': 61777,
                    'server.socket_host': '0.0.0.0',
                    'server.socket_queue_size': 100,
                    'server.protocol_version': 'HTTP/1.1',
                    'server.log_to_screen': True,
                    'server.log_file': '/var/log/cherrypy.log',
                    'server.reverse_dns': False,
                    'server.thread_pool': 200,
                    'server.environment': 'production',
                    'engine.timeout_monitor.on': False,
                    'engine.autoreload.on': True,
                }
        }
    
    #pidfile = os.path.join(cur_dir, "./", "cherrypy_pid.pid")
    #engine = cherrypy.engine
    #plugins.PIDFile(engine, pidfile).subscribe()

    cherrypy.config.update(settings)
    cherrypy.tree.mount(Index(), '/')
    cherrypy.tree.mount(Node(), '/node')

    #d = Daemonizer(cherrypy.engine)
    #d.subscribe()
    cherrypy.engine.start()
