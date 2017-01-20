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

job_queue = Queue.Queue(0)

class keepalived_log_analyze():
    def __init__(self, filename, logfile):
        self.file = open(self.filename,'r')
        self.file_stat = os.stat(self.filename)
        self.file_size = self.file_stat[6]
        self.file.seek(self.file_size)
        try:
            loggin.basicConfig)(
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
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\w*):\s*Executing\s*\[ip\s*addr\s*del.*\]\s*\for\s*VS\s*\[(\S*)\]:\d+$')
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
                ,"alert_time":alert_time,
            }

            job_queue.put(job)

    #service enable logging
    def service_is_up(self, log):
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\w*):\s*Executing\s*\[ip\s*addr\s*add.*\]\s*for\s*VS\s*\[(\S*)\]:\d+$')
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
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\w*):\s*(Enabling|Adding)\s*service\s*\[(\d+\.\d+\.\d+\.\d+)\]:(\d+)\s*to\s*VS \[(\S*)\]:\d+$')
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
        compile_log = re.compile(r'^(\w*)\s*(\d+)\s*(\d+:\d+:\d+)\s*(\S*)\s*(\w*):\s*(Removing|Disabling)\s*service\s*\[(\d+\.\d+\.\d+\.\d+)\]:(\d+)\s*from\s*VS\s*\[(\S*)\]:\d+$')
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














































