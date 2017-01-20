#!/usr/bin/python
# -*- coding: utf8 -*-

import datetime
import json

import logging

import os
import sys

import re

import time

import yaml

from stttt2003pk_mail_send import mysendmail

import requests
import Queue
import threading


class keepalived_log_analyze():
    def __init__(self, filename, logfile):
        self.filename = filename
        self.file = open(self.filename,'r')
        self.file_stat = os.stat(self.filename)
        self.file_size = self.file_stat[6]
        self.file.seek(self.file_size)
        try:
            logging.basicConfig(
                level=logging.NOTSET,
                format='%(asctime)s %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename=logfile,
                filemode='a' 
            )
            self.logging = logging.getLogger()
        except AttributeError as err:
            print("Error: %s %s" %(err, logfile))
            sys.exit(2)


    #service disabled logging
    def service_is_disable(self, log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\S*)\[.*\]:\s*Executing\s*\[ip\s*addr\s*del.*\]\s*for\s*VS\s*\[(\S*)\]:\d+$')
        match = compile_log.match(log)

        if match:
            log_group = match.groups()
            alert_time = '%s %s %s' %(log_group[0],log_group[1],log_group[2])
            lb_id = log_group[3]
            vip_instance = log_group[5]
            print 'Service:%s is down' %vip_instance

            job = {
                "job_type":"run_service_is_disable_action",
                "lb_id":lb_id,
                "vip_instance":vip_instance,
                "alert_time":alert_time,
            }

            job_queue.put(job)

    #service enable logging
    def service_is_up(self, log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\S*)\[.*\]:\s*Executing\s*\[ip\s*addr\s*add.*\]\s*for\s*VS\s*\[(\S*)\]:\d+$')
        match = compile_log.match(log)

        if match:
            log_group = match.groups()
            alert_time = '%s %s %s'%(log_group[0],log_group[1],log_group[2])
            lb_id = log_group[3]
            vip_instance = log_group[5]
            print 'Service:%s is up' %vip_instance
            job = {
                "job_type":"run_service_is_enable_action",
                "lb_id":lb_id,
                "vip_instance":vip_instance,
                "alert_time":alert_time,
            }
            
            job_queue.put(job)
            
    #real server enable logging
    def rs_is_enable(self, log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\S*)\[.*\]:\s*(Enabling|Adding)\s*service\s*\[(\d+\.\d+\.\d+\.\d+)\]:(\d+)\s*to\s*VS \[(\S*)\]:\d+$')
        match = compile_log.match(log)

        if match:
            log_group =  match.groups()
            alert_time = '%s %s %s'%(log_group[0],log_group[1],log_group[2])
            lb_id = log_group[3]
            rs = "%s:%d" %(log_group[6],int(log_group[7]))
            vip_instance = log_group[8]
            print 'RS:%s form %s is enable' %(rs,vip_instance)
            job = {
                "job_type":"run_rs_is_enable_action",
                    "lb_id":lb_id,
                    "vip_instance":vip_instance,
                    "rs":rs,
                    "alert_time":alert_time,
            }

            job_queue.put(job)

    #real server disable logging
    def rs_is_disable(self, log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\S*)\[.*\]:\s*(Removing|Disabling)\s*service\s*\[(\d+\.\d+\.\d+\.\d+)\]:(\d+)\s*from\s*VS\s*\[(\S*)\]:\d+$')
        match = compile_log.match(log)

        if match:
            log_group = match.groups()
            alert_time = '%s %s %s'%(log_group[0],log_group[1],log_group[2])
            lb_id = log_group[3]
            rs = "%s:%d" %(log_group[6],int(log_group[7]))
            vip_instance = log_group[8]
            print 'RS:%s form %s is disable' %(rs,vip_instance)

            job = {
                "job_type":"run_rs_is_disable_action",
                "lb_id":lb_id,
                "vip_instance":vip_instance,
                "rs":rs,
                "alert_time":alert_time,
            }


    #handler
    def handler(self, line):
        self.rs_is_disable(line)
        self.rs_is_enable(line)
        self.service_is_disable(line)
        self.service_is_up(line)

    #run the worker in
    def run(self):
        while True:
            time.sleep(1)
            lines = self.file.readlines()
            if not lines:
                continue
            for line in lines:
                self.handler(line)















































job_queue = Queue.Queue(0)
cur_dir = os.path.dirname(os.path.abspath(__file__))
config = yaml.load(open(os.path.join(cur_dir,'config.yaml')))

if __name__ == '__main__':
    filename = config['keepalived_log_file']
    logfile = config['logfile']
    
    work = keepalived_log_analyze(filename,logfile)
    work.run()










































