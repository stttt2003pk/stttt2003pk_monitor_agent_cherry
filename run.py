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
