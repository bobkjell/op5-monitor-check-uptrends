#!/usr/bin/env python

# "THE BEER-WARE LICENSE" - - - - - - - - - - - - - - - - - -
# This file was initially written by Robert Claesson.
# As long as you retain this notice you can do whatever you
# want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.
# - - - - - - - - - - - - - - - robert.claesson@gmail.com - -

# Modules
import requests, base64, argparse, json, urllib3, datetime, os
urllib3.disable_warnings()

# ENV
os.environ['LC_ALL'] = 'en_US.UTF-8'

# Arguments
parser = argparse.ArgumentParser(description="Get monitoring statistics from Uptrends https(s) checks for ITRS OP5 Monitor.")
parser.add_argument("-m", "--monitor", help="Name of monitor.", type=str, required=True)
parser.add_argument("-u", "--username", help="API Username.", type=str, required=True)
parser.add_argument("-p", "--password", help="API Password.", type=str, required=True)
args = parser.parse_args()

# Authentication
userpass = args.username + ":" + args.password
b64val = base64.b64encode(userpass)

# Make requests
def make_request(url, userpass):
  try:
    r = requests.get(url, verify=False, headers={"Authorization": "Basic %s" % userpass})
    r.raise_for_status()
  except requests.exceptions.HTTPError as error:
    print ("UNKNOWN: " + str(error))
    exit(3)
  return r

# Format json
def format_json(response_json):
  json_formatted = response_json.json()
  json_formatted = json.dumps(json_formatted)
  json_formatted = json.loads(json_formatted)
  return json_formatted

# Get monitor name & format json response
request = make_request("https://api.uptrends.com/v4/Monitor", b64val)
response_json = format_json(request)

# Parse monitor info
for item in response_json:
  if item['Name'].encode('utf-8').strip() == args.monitor:
    monitor_name = args.monitor
    monitor_guid = item['MonitorGuid']
    monitor_checkinterval = item['CheckInterval']
    monitor_isactive = item['IsActive']
    monitor_loadtimelimit1 = item['LoadTimeLimit1']
    monitor_loadtimelimit2 = item['LoadTimeLimit2']

# Check if monitor exists
if 'monitor_name' not in vars():
  print ("UNKNOWN: Monitor " + args.monitor + " not found.")
  exit(3)

# Check if monitor is active
if monitor_isactive == False:
  print ("UNKNOWN: Monitor " + monitor_name + " is not actived. Exiting.")
  exit(3)

# Get latest check status
request = make_request("https://api.uptrends.com/v4/MonitorCheck/Monitor/" + monitor_guid + "?ErrorLevel=NoError&ShowPartialMeasurements=true&Sorting=Descending&Take=1&PresetPeriod=CurrentDay", b64val)
response_json = format_json(request)

# Parse check info
for item in response_json['Data']:
  status_message = item['Attributes']['ErrorDescription']
  status_code = item['Attributes']['ErrorCode']
  status_timestamp = item['Attributes']['Timestamp']
  status_total_time = item['Attributes']['TotalTime']
  status_resolve_time = item['Attributes']['ResolveTime']
  status_connection_time = item['Attributes']['ConnectionTime']
  status_download_time = item['Attributes']['DownloadTime']
  checkpoint_serverid = item['Relationships'][0]['Id']

# Get CheckpointServer
request = make_request("https://api.uptrends.com/v4/Checkpoint/Server/" + str(checkpoint_serverid), b64val)
response_json = format_json(request)

# Parse checkpoint info
for item in response_json['Relationships']:
  checkpoint_server_name = item['Attributes']['CheckpointName']

# Performance string
perfdata = (" | TotalTime=" + str(status_total_time) + "ms" + ";" + str(monitor_loadtimelimit1) + ";" + str(monitor_loadtimelimit2) +
" ResolveTime=" + str(status_resolve_time) +
"ms ConnectionTime=" + str(status_connection_time) +
"ms DownloadTime=" + str(status_download_time)
)

# Beautify timestamp & message
try:
  status_timestamp = datetime.datetime.strptime(status_timestamp, '%Y-%m-%dT%H:%M:%S.%f').strftime("%H:%M:%S")
  status_message = status_message.encode('utf-8').strip()
except:
  status_timestamp = datetime.datetime.strptime(status_timestamp, '%Y-%m-%dT%H:%M:%S').strftime("%H:%M:%S")
  status_message = status_message.encode('utf-8').strip()

# Check for error results
if status_message != "OK":
  if status_code == 6001:
    print ("CRITICAL: " + status_message + "(crit) at: " + status_timestamp + " from: " + checkpoint_server_name.encode('utf-8')  + perfdata)
    exit(2)
  elif status_code == 6000:
    print ("WARNING: " + status_message + "(warn) at: " + status_timestamp + " from: " + checkpoint_server_name.encode('utf-8') + perfdata)
    exit(1)
  else:
    print ("CRITICAL: " + status_message + " from: " + checkpoint_server_name.encode('utf-8') + perfdata)
    exit(2)

# If we made it this far, check is OK
print ("OK: " + monitor_name.encode('utf-8') + " responds with OK status at: " + status_timestamp + " from: " + checkpoint_server_name.encode('utf-8') + perfdata)
exit(0)
