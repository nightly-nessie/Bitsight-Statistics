#!/usr/bin/env python
# coding: utf-8
import requests
import json
import datetime

dict_EMA = { "guid": ["#guid list"], "name": ["#name list"]}

today = datetime.datetime.now()
last_week = today + datetime.timedelta(days=-7)
query_date = last_week.date()

grade_value = 'bad'

api_key = '#api_key'
params = (
    ('last_seen_gte', query_date),
    ('grade', grade_value)
)

guid_list = dict_EMA["guid"]

x = 0
findings = ''
for company_guid in guid_list:
    response = requests.get('https://api.bitsighttech.com/ratings/v1/companies/' + company_guid + '/findings', params=params, auth=(api_key, ''))
    json_response = response.text
    response_dict=json.loads(json_response)
    number_findings = response_dict['count']
    link = 'https://service.bitsighttech.com/app/company/' + company_guid + '/findings/?affects_rating=true&grade=' + grade_value + '&last_seen=7d&sort=-last_seen'
    for i in range (0, number_findings):
        findings += str(dict_EMA["name"][x] + ' | ' + grade_value + ' | ' + response_dict['results'][i]['evidence_key'] + ' | ' + response_dict['results'][i]['risk_vector_label'] + ' | ' + link + '\n')
    x = x + 1

import smtplib

from email.message import EmailMessage

msg = EmailMessage()
msg['Subject'] = '#subject'
msg['From'] = '#fromemail'
msg['To'] = '#toemail'
msg.set_content(findings)

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login("#fromemail", "#password")
s.send_message(msg)
s.quit() 
