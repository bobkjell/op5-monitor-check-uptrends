# op5-monitor-check-uptrends
Monitor Uptrends http(s) checks from OP5 Monitor. <br/>
Requires login and API access to Uptrends: <br/>
https://www.uptrends.com/ <br/>
https://www.uptrends.com/support/kb/api/authentication-v4 <br/>

Currently only supports http(s) type of checks in Uptrends. <br/>

![alt text](https://github.com/bobkjell/op5-monitor-check-uptrends/blob/main/uptrends-checks.png "Uptrends service-checks")

## Requires
* python-requests
* Uptrends API credentials

## Usage
Upload script to: `/opt/plugins/custom/` <br/>

Create a check_command for the plugin: <br/>
`command_name = check_uptrends` <br/>
`command_line = $USER1$/custom/check_uptrends.py -u $ARG1$ -p $ARG2$ -m $ARG3$` <br/>



Create service-objects for each monitor: (Example for example.com) <br/>
`service_description = Uptrends: example.com` <br/>
`check_command = check_uptrends` <br/>
`check_command_args = <username>!<password>!example.com` <br/>

It's recommended to mask your API-key in: `/opt/monitor/etc/resource.cfg`

## Notes
