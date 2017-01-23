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

import shelve


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
            print 'RS:%s from %s is enable' %(rs,vip_instance)
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
            print 'RS:%s from %s is disable' %(rs,vip_instance)

            job = {
                "job_type":"run_rs_is_disable_action",
                "lb_id":lb_id,
                "vip_instance":vip_instance,
                "rs":rs,
                "alert_time":alert_time,
            }
            job_queue.put(job)


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



class log_job_thread(threading.Thread):
    def __init__(self, job_input):
        self.jobq = job_input
        self.lvs_alert_api_url = config['lvs_cluster_alert_api']
        self.date = self.gettoday()
        threading.Thread.__init__(self)

    def timestampnow(self):
        return time.time()

    def gettoday(self):
        dt = datetime.date.today()
        return dt.strftime('%Y-%m-%d')

    def get_info_yaml(self):
        infoyaml = yaml.load(open(config['info_yaml_file']))
        return infoyaml

    def post_alert_message_to_api(self, cluster_id, lb_id, area, descript, owners, rs, status, message, alert_type, time_now, vip_instance, vip, alert_time):
        url = self.lvs_alert_api_url
        data = {
            "cluster_id":cluster_id,
            "lb_id":lb_id,
            "area":area,
            "descript":descript,
            "owners":owners,
            "rs":rs,
            "status":status,
            "message":message,
            "alert_type":alert_type,
            "time":time_now,
            "vip_instance":vip_instance,
            "vip_group":vip,
            "alert_time":alert_time,
        }
        _data = json.dumps(data)
        try:
            r = requests.post(url, data=_data, timeout=1)
            logging.info('Post Alert Message Successed !')
            return True

        except Exception,e:
            logging.warn('Post Alert Message Failed! case by: %s' % e)
            return False

    def add_rs_or_service_status(self, key, value):
        db = shelve.open(alert_rs_status_file, 'c')
        db[str(key)] = value
        db.close()

    def search_rs_or_service_status(self, key):
        db = shelve.open(alert_rs_status_file, 'c')
        if key in db:
            return db[key]
        else:
            return 'pending'

        db.close()
        
    def write_mail_content(self,cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time):
        html_template = u'''
        <html>
            <h2 style="color:#FFFFFF; background: #008040;">LVS Alert Mail</h2>
            <div> <b>Alert_Time：</b>%s
            </div>
            <div> <b>Cluster_Id: </b>%s
            </div>
            <div> <b>Load_Balancer: </b>%s
            </div>

            <div> <b>Area: </b>%s
            </div>

            <div>
                <b>Descript：</b>%s
            </div>

            <div>
                <b>VIP：</b>%s
            </div>


            <div>
                <b>Owners: </b>%s
            </div>

            <div>
                <b>Real Server: </b>%s
            </div>

            <div>
                <b>Status：</b>%s
            </div>

            <h2 style="color:#FFFFFF; background: #4682B4;">Alert_Message</h2> 
            <font size="4" color="#BF6000"><xmp>%s</xmp></font>
            <h2 style="color:#FFFFFF; background: #5353B9;">Monitoring Status</h2>
            <a href="http://lvs.stttt2003pk.com/lvsalert/?vip_instance=%s&date=%s">Go To The CMDB To View The Alert Message</a>
        '''
        content = html_template % (alert_time,cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,self.date)
        return content

    def search_vip_from_infoyaml(self, vip_instance):
        infoyaml = self.get_info_yaml()
        for vip in infoyaml['server']:
            if vip['vip_instance'] == vip_instance:
                return vip
        return False
            

    #the rs enable job
    def run_rs_is_enable_action(self, job):
        lb_id = job['lb_id']
        vip_instance = job['vip_instance']
        alert_time = job['alert_time']
        rs = job['rs']

        #get the configuration from /etc/keepalived/info.yaml
        alert_type = "rs_is_up"
        infoyaml = self.get_info_yaml()
        cluster_id = infoyaml['cluster_id']
        area = infoyaml['area']
        vip_dict = self.search_vip_from_infoyaml(vip_instance)

        if vip_dict:
            descript = vip_dict['descript']
            owners = vip_dict['owners']
            vip = [ '%s:%s' %(i['vip'], i['port']) for i in vip_dict['vip_group'] ]
            mailto = vip_dict['mailto']
        else:
            descript = 'UnKown'
            owners = 'UnKown'
            vip = 'UnKown'
            mailto = None

        status = 'enable'
        message = u'Real Server %s,monitoring up,back to the vip_instance' % rs
        logging.info(u'RS Recovery (Description:%s,Vip:%s,RealServer:%s)' %(descript,vip,rs))

        rs_key = '%s_%s' % (vip_instance,rs)
        rs_status = self.search_rs_or_service_status(rs_key)

        self.add_rs_or_service_status(rs_key, 'enable')

        if rs_status == 'disable':
            time_now = self.timestampnow()
            self.post_alert_message_to_api(cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time)
            admin_mail_group = infoyaml['admin_mail_group']
            if mailto:
                mailtolist = admin_mail_group + mailto
            else:
                mailtolist = admin_mail_group
            mailhost = config['mail_host']
            mail_me = config['mail_me']

            mail_subject = u'Rs Recovery Alert (Description:%s,Vip:%s,RealServer:%s)' %(descript,vip,rs)
            content = self.write_mail_content(cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time)
            handler_mail = mysendmail(mailhost, mail_me,mailtolist, mail_subject)
            print 'rs:%s is enable, start sendmail' % rs
            handler_mail.send_mail(content)

    def run_rs_is_disable_action(self, job):
        lb_id = job['lb_id']
        vip_instance = job['vip_instance']
        alert_time = job['alert_time']
        rs = job['rs']

        alert_type = "rs_is_down"
        infoyaml = self.get_info_yaml()
        cluster_id = infoyaml['cluster_id']
        area = infoyaml['area']

        vip_dict = self.search_vip_from_infoyaml(vip_instance)
        if vip_dict:
            descript = vip_dict['descript']
            owners = vip_dict['owners']
            vip = [ '%s:%s' %(i['vip'], i['port']) for i in vip_dict['vip_group']]
            mailto = vip_dict['mailto']
        else:
            descript = 'UnKown'
            owners = 'UnKown'
            vip = 'UnKown'
            mailto = None

        status = 'disable'
        message = u'Real Server %s,monitoring down,remove from to the vip_instance' % rs
        logging.info(u'RS Down (Description:%s,Vip:%s,RealServer:%s)' %(descript,vip,rs))

        rs_key = '%s_%s' % (vip_instance,rs)
        rs_status = self.search_rs_or_service_status(rs_key)

        self.add_rs_or_service_status(rs_key,'disable')

        if rs_status == 'enable' or rs_status == 'pending':
            time_now = self.timestampnow()
            self.post_alert_message_to_api(cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time)
            
            admin_mail_group = infoyaml['admin_mail_group']
            if mailto:
                mailtolist = admin_mail_group + mailto
            else:
                mailtolist = admin_mail_group

            mailhost = config['mail_host']
            mail_me = config['mail_me']
            
            mail_subject = u'LVS Rs Down Alert (Description:%s,Vip:%s,RealServer:%s)' %(descript,vip,rs)
            content = self.write_mail_content(cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time)
            handler_mail = mysendmail(mailhost,mail_me,mailtolist,mail_subject)
            print 'rs:%s is down, start sendmail' % rs
            handler_mail.send_mail(content)

    def run_service_is_disable_action(self, job):
        lb_id = job['lb_id']
        vip_instance = job['vip_instance']
        alert_time = job['alert_time']

        alert_type = "service_is_down"
        infoyaml = self.get_info_yaml()
        cluster_id = infoyaml['cluster_id']
        area = infoyaml['area']
        vip_dict = self.search_vip_from_infoyaml(vip_instance)
        rs = 'ALL'

        if vip_dict:
            descript = vip_dict['descript']
            owners = vip_dict['owners']
            vip = [ '%s:%s' %(i['vip'], i['port']) for i in  vip_dict['vip_group'] ]
            mailto = vip_dict['mailto']
        else:
            descript = 'UnKown'
            owners = 'UnKown'
            vip = 'UnKown'
            mailto = None

        status = 'disable'
        message = u'Critical Service %s,No real server can be used,Service VIP:%s Down' %(descript,vip) 
        logging.info(u'Critical Service %s,No real server can be used,Service VIP:%s Down' %(descript,vip))

        service_key = '%s_service' %vip_instance
        service_status = self.search_rs_or_service_status(service_key)

        self.add_rs_or_service_status(service_key,'disable')
        if service_status == 'enable' or service_status == 'pending':
            time_now = self.timestampnow()
            #print 'postdata'
            self.post_alert_message_to_api(cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time)

            admin_mail_group = infoyaml['admin_mail_group']
            if mailto:
                mailtolist = admin_mail_group + mailto
            else:
                mailtolist = admin_mail_group
            mailhost = config['mail_host']
            mail_me = config['mail_me']
            mail_subject = u'Critical! LVS Service Down Alert (Description:%s,Vip:%s)' %(descript,vip)
            content = self.write_mail_content(cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time)
            handler_mail = mysendmail(mailhost,mail_me,mailtolist,mail_subject)
            print 'service:%s is down, start sendmail' % vip_instance
            handler_mail.send_mail(content)
            
    def run_service_is_enable_action(self, job):
        lb_id = job['lb_id']
        vip_instance = job['vip_instance']
        alert_time = job['alert_time']

        alert_type = "service_is_up"
        infoyaml = self.get_info_yaml()
        cluster_id = infoyaml['cluster_id']
        area = infoyaml['area']
        vip_dict = self.search_vip_from_infoyaml(vip_instance)
        rs = 'ALL'

        if vip_dict:
            descript = vip_dict['descript']
            owners = vip_dict['owners']
            vip = [ '%s:%s' %(i['vip'], i['port']) for i in vip_dict['vip_group'] ]
            mailto = vip_dict['mailto']
        else:
            descript = 'UnKown'
            owners = 'UnKown'
            vip = 'UnKown'
            mailto = None

        status = 'enable'
        
        message = u'Success Service %s,service can be used,Service VIP:%s up' %(descript,vip) 
        logging.info(u'Success Service %s,service can be used,Service VIP:%s up' %(descript,vip))

        service_key = '%s_service' % (vip_instance)
        service_status = self.search_rs_or_service_status(service_key)

        self.add_rs_or_service_status(service_key,'enable')
        if service_status == 'disable':
            time_now = self.timestampnow()
            self.post_alert_message_to_api(cluster_id,lb_id,area,descript,owners,rs,status,message,alert_type,time_now,vip_instance,vip,alert_time)

            admin_mail_group = infoyaml['admin_mail_group']
            if mailto:
                mailtolist = admin_mail_group + mailto
            else:
                mailtolist = admin_mail_group
            mailhost = config['mail_host']
            mail_me = config['mail_me']
            mail_subject = u'Success! LVS Service Up Alert (Description:%s,Vip:%s)' %(descript,vip)
            content = self.write_mail_content(cluster_id,lb_id,area,descript,vip,owners,rs,status,message,vip_instance,alert_time)
            handler_mail = mysendmail(mailhost,mail_me,mailtolist,mail_subject)
            print 'service:%s is up, start sendmail' % vip_instance
            handler_mail.send_mail(content)
            
    def _process_job(self, job):
        job_type = job['job_type']
        if job_type == 'run_rs_is_enable_action':
            print 1
            self.run_rs_is_enable_action(job)
        elif job_type == 'run_rs_is_disable_action':
            print 2
            self.run_rs_is_disable_action(job)
        elif job_type == 'run_service_is_enable_action':
            self.run_service_is_enable_action(job)
        elif job_type == 'run_service_is_disable_action':
            self.run_service_is_disable_action(job)
    
    def run(self):
        while True:
            time.sleep(1)
            if self.jobq.qsize() > 0:
                job = self.jobq.get()
                print job
                self._process_job(job) 
















      
            
            
            






































job_queue = Queue.Queue(0)
cur_dir = os.path.dirname(os.path.abspath(__file__))
config = yaml.load(open(os.path.join(cur_dir, 'config.yaml')))
data_dir = os.path.join(cur_dir, 'data/')
#
alert_rs_status_file = os.path.join(data_dir,'alert_rs_status.dbm')

if __name__ == '__main__':
    filename = config['keepalived_log_file']
    logfile = config['logfile']
    
    thread = log_job_thread(job_queue)
    thread.start()
    work = keepalived_log_analyze(filename,logfile)
    work.run()
    thread.join()










































