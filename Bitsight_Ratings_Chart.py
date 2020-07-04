import requests
import json
import datetime

YYYYMMDD = datetime.datetime.now()

api_key = '#api_key'
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

rating_date_current = folder_rating_date
#
# Or, fill out a date of your choosing
#
#rating_date_current = 'YYYY-MM-DD'
rating_date_current_obj = datetime.datetime.strptime(rating_date_current, "%Y-%m-%d")
#print(rating_date_current_obj) # Check the returned value
rating_date_previous_month = rating_date_current_obj + datetime.timedelta(days=-28)
#print(rating_date_previous_month) # Check the returned value
rating_date_previous = rating_date_previous_month.date()
#
# Or, fill out a date of your choosing
#
#rating_date_previous = 'YYYY-MM-DD'

#print(rating_date_previous) # Check the returned value

params = (
    ('rating_date', rating_date_previous),
)
response_prev = requests.get('https://api.bitsighttech.com/ratings/v1/companies', params=params, auth=(api_key, ''))
params = (
    ('rating_date', rating_date_current),
)
response_cur = requests.get('https://api.bitsighttech.com/ratings/v1/companies', params=params, auth=(api_key, ''))

#print(response_cur.status_code) # Check the returned value
#print(response_prev.text) # Check the returned value
#print(response_cur.text) # Check the returned value

json_resp_prev = response_prev.json()
json_resp_cur = response_cur.json()

#
# Test the returned value for a random company from the dictionary
#
#print(json_resp_prev["companies"][18]["name"] + ',' + str(json_resp_prev["companies"][18]["rating"]))
#print(json_resp_cur)

#
# Running through the knwon numbers of company in the portfolio, adding the listvalue in front
#
#company_list = []
#for x in range (0, 23): # Should be changed into a dynamic value, reading the numbers of companies in the portfolio
#    company_list.append(str(x) + ' ' + json_resp_cur["companies"][x]["name"]);
#print(*company_list, sep = "\n")

#
# Adjusted grouped list, any order can do but, use previous block to figure out the listvalues
# Now in alfabetical order, taking the entire portfolio, except:
# PSA Marine (6)
#
order_list = [19,8,10,9,7,5,20,12,13,11,18,16,22,3,4,2,1,0,14,15,17,21]
company_list = []
for i in order_list:
    company_list.append(json_resp_cur["companies"][i]["name"])

#
# Check the order of the adjusted list
#
#print(*company_list, sep = "\n")

previous_values = []
for i in order_list:
    previous_values.append(json_resp_prev["companies"][i]["rating"])

current_values = []
for i in order_list:
    current_values.append(json_resp_cur["companies"][i]["rating"])

rating = {}
rating[rating_date_previous] = previous_values
rating[rating_date_current] = current_values

#
# Check the returned rating values
#
#print(previous_values)
#print(current_values)
#print(rating)

#
# Panda based chart
#
#import pandas as pd

#import matplotlib.pyplot as plot

#dataFrame = pd.DataFrame(data=rating, index=company_list);
 
#dataFrame.plot.bar(rot=85, title="Bitsight Ratings", figsize=(30,5), ylim=(400,820));
#plot.show(block=True);

import matplotlib
matplotlib.use('Agg') # When deployed in a terminal
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

plt.hlines(y=740, xmin=-0.5, xmax=22.5, color='g', alpha=0.7, linestyle='dotted', linewidth=3)
plt.hlines(y=folder_rating_value, xmin=-0.5, xmax=22.5, color='b', alpha=0.7, linestyle='--', linewidth=2)
plt.grid(True, alpha=0.2)

filename = (YYYYMMDD.strftime("%Y%m%d") + '_Bitsight_Ratings_' + str(rating_date_previous) + '_and_' + str(rating_date_current) + '.png')

plt.savefig(filename, bbox_inches='tight')
plt.show() # Only when not running on a terminal

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject = "Weekly Bitsight Rating Chart - " + str(YYYYMMDD.date())
body = "#blahblah"
sender_email = "#fromemail"
receiver_email = "#toemail"
password = "#password"

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
