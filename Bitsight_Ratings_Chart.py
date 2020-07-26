#!/usr/bin/env python
# coding: utf-8

import requests
import json
import datetime

YYYYMMDD = datetime.datetime.now()

api_key = ''
folder_rating = requests.get('https://api.bitsighttech.com/ratings/v1/folders/#folder_guid/graph_data', auth=(api_key, ''))

json_folder_rating = folder_rating.text
folder_rating_dict = json.loads(json_folder_rating)
#
# Fetching the latest rating performed in Bitsight and take this as the current rating
#

folder_rating_value = folder_rating_dict['ratings'][-1]['y']
#print(folder_rating_value) # Check the returned value

folder_rating_date = folder_rating_dict['ratings'][-1]['x']
#print(folder_rating_date) # Check the returned value

#
# Determine Porfolio length
#

portfolio_date_current = folder_rating_date
params = (
    ('rating_date', portfolio_date_current),
)
response_cur = requests.get('https://api.bitsighttech.com/ratings/v1/companies', params=params, auth=(api_key, ''))
json_resp_cur = response_cur.json()
portfolio_count=len(json_resp_cur['companies'])

#
# Running through the portfolio, adding the guid in front
#

#company_list = []
#for x in range (0, portfolio_count):
#    company_list.append(json_resp_cur["companies"][x]["guid"] + "\t" + json_resp_cur["companies"][x]["name"]);
#print(*company_list, sep = "\n")

#
# Build the Portfolio Dictionary
#

company_guid = []
for i in range (0, portfolio_count):
    company_guid.append(json_resp_cur["companies"][i]["guid"])

company_name = []
for j in range (0, portfolio_count):
    company_name.append(json_resp_cur["companies"][j]["name"])

company_dict = {}
company_dict['company_guid'] = company_guid
company_dict['company_name'] = company_name

ordered_portfolio_list = [""]
order_list = []

#
# Generate list of the indices to query the Portfolio Dictionary
#

for k in ordered_portfolio_list:
    loc = company_dict['company_guid'].index(k)
    order_list.append(loc)

#
# Generate list of company names according the ordered portfolio list
#

company_list = []
for i in order_list:
    company_list.append(json_resp_cur["companies"][i]["name"])

previous_values = []
current_values = []

for i in ordered_portfolio_list:
    #
    # Check the GUID used
    #
    #print(i)
    response_company = requests.get('https://api.bitsighttech.com/ratings/v1/companies/' + i, auth=(api_key, ''))
    json_response_company = response_company.json()
    #
    # Check the build-up of the list
    #
    #print(json_response_company['name'])
    #
    # index 28 represents 28 days prior to the latest available rating
    # index 0 represents the latest available resut of the rating, which usually is the day before
    # index 365 would then present a year ago
    #
    previous_values.append(json_response_company['ratings'][28]['rating'])
    rating_date_previous = json_response_company['ratings'][28]['rating_date']
    current_values.append(json_response_company['ratings'][0]['rating'])
    rating_date_current = json_response_company['ratings'][0]['rating_date']
#
# Check if the ordered list is correct
#

#print(*company_list, sep = "\n")

rating = {}
rating[rating_date_previous] = previous_values
rating[rating_date_current] = current_values

#print(previous_values)
#print(current_values)
#print(rating)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

x = np.arange(len(company_list))  # the label locations
width = 0.30  # the width of the bars

fig, ax = plt.subplots(figsize=(30.0, 5.0))

rects1 = ax.bar(x - width/2, previous_values, width, label=rating_date_previous, color='#ffa500', alpha=0.5)
rects2 = ax.bar(x + width/2, current_values, width, label=rating_date_current, color='#ffa500', alpha=0.9)

ax.set_ylabel('Bitsight Rating')
ax.set_ylim(450,850)
#ax.set_title(' ') # Should a standalone graph be needed with a title
ax.set_xticks(x)
ax.set_xticklabels(company_list, rotation=60, ha='right')
ax.legend()


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)

#fig.tight_layout() # Condenses the height

plt.hlines(y=740, xmin=-0.5, xmax=23.5, color='g', alpha=0.7, linestyle='dotted', linewidth=3)
plt.hlines(y=folder_rating_value, xmin=-0.5, xmax=23.5, color='b', alpha=0.7, linestyle='--', linewidth=2)
plt.grid(True, alpha=0.2)

filename = (YYYYMMDD.strftime("%Y%m%d") + '_Bitsight_Ratings_' + str(rating_date_previous) + '_and_' + str(rating_date_current) + '.png')

plt.savefig(filename, bbox_inches='tight')
#plt.show()

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject = "Weekly Bitsight Rating Chart - " + str(YYYYMMDD.date())
body = "Please find the lateste rating chart in attachment."
sender_email = ""
receiver_email = ""
password = ""

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject

# Add body to email
message.attach(MIMEText(body, "plain"))

# Open PDF file in binary mode
with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filename}",
)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()

# Log in to server using secure context and send email
context = ssl.create_default_context()
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)
