# Scripts for various tasks

### alarm.py
Set alarms from the terminal with natural syntax  

    $ alarm at 5 pm  
    $ alarm at 5 pm tomorrow  
    $ alarm after 10 minutes  

Uses `toilet` for some wicked cool fonts  

    $ alarm at 5 pm -f <font>  

Set messages to be displayed on timer end  

    $ alarm at 5 pm -m "do the thing"  

Set silent messages which pop up message box

    $ alarm at 5 pm --silent

Set different colours

    $ alarm at 5 pm -fg red -bg cyan

  

**colorfind.py**  
open a Tk gui to showcase colors for various rgb values  
  
**distinct\_colours.py**  
for the simple steg ctf challenges  
changes pixel colours to random, distinct values  

## network

### router\_cfg.py
get settings from and set ip on a dlink router.  
amazingly, the router doesn't check a session cookie for verifying user sessions. (atleast for my firmware version)  
instead, it just checks the referer. go figure.  
so, this script **doesn't** need the password to change *any* settings on the router  

    $ router_cfg get ip_address  
    $ router_cfg get subnet_mask  
    $ router_cfg get all  
    $ router_cfg set 10.9.11.5  


### find\_hosts.py
find free IPs on the local network through a ping scan  

### auto\_ip\_config.py
poor man's DHCP :)  
change IP to a free one automatically in case of IP conflicts (for static IP configurations)  
this script uses router\_cfg.py to change the IP on the router (so, only works for Dlink routers)  

**firewall.sh**  
sets up your firewall to use redsocks with http-connect  
currently doesn't support irc - help appreciated :)  

**change-proxy**  
change proxy manually (using redsocks)  

### proxy\_handler.py
changes between free proxies automatically (using redsocks)  
switches proxy on encountering proxy errors  

**human\_red\_out.py**  
formats redsocks logs for human consumption  
Usage: `$ tail -f <redsocks log file> | human_red_out.py`

### keepalive.py
automates the keepalive process for IIT-BHU's internet  
