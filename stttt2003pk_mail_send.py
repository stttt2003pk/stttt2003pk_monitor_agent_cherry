#!/usr/bin/env python
# -*- coding: utf8 -*-

import smtplib
from email.mime.text import MIMEText
import yaml

class mysendmail():
    def __init__(self, mailhost, me, tolist, subject):
        '''
        mailhost = 'x.x.x.x'
        me = 'stttt2003pk@gmail.com'
        tolist = ['a@gzsunrun.cn','b@tencent.com']
        subject = 'mail title'
        '''
        self.mailhost = mailhost
        self.me = me
        self.tolist = tolist
        self.subject = subject
        try:
            self.person_info = yaml.load(open('/home/info/person_info.yaml', 'r'))
        except Exception,e:
            print 'could not get personnal_infomation cause by %s' %e


    def write_mail(self, sender, to_list, sub, content):
        msg = MIMEText(content, _subtype='html', _charset='utf-8')
        msg['Subject'] = sub
        msg['From'] = sender
        msg['To'] = ';'.join(to_list)
        
        return msg

    def send_mail(self, content):
        msg = self.write_mail(self.me, self.tolist, self.subject, content) 
        try:
            s = smtplib.SMTP()
            s.connect(self.mailhost)
            s.login(self.person_info['username'], self.person_info['passwd'])
            s.sendmail(self.me, self.tolist, msg.as_string())
            s.close()
            
            print 'mail sended'
            return True
        except Exception, e:
            print 'mail failed %s' % e
            return False
            





















