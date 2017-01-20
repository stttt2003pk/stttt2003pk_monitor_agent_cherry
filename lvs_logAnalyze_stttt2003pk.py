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
        self.file = open(self.filename,'r')
        self.file_stat = os.stat(self.filename)
        self.file_size = self.file_stat[6]
        self.file.seek(self.file_size)


#
