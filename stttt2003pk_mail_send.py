#!/usr/bin/env python
# -*- coding: utf8 -*-

import smtplib
from email.mime.text import MIMEText

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

    def write_mail(self, sender, to_list, sub, content)
        msg = MIMEText(content, _subtype='html', _charset='utf-8')
        msg['Subject'] = sub
        msg['From'] = sender
        msg['To'] = ';'.join(to_list)
        
        return msg

    def sendmail(self, content):
        msg = self.write_mail(self.me, self.tolist, self.subject, content) 
        try:
            s = smtplib.SMTP()
            s.connect(self.mailhost)
            s.sendmail(self.me, self.tolist, msg.as_string())
            s.close()
            
            print 'mail sended'
            return True
        except Exception, e:
            print 'mail failed'
            return False
            





















