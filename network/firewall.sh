#!/bin/bash

iptables -t nat --flush
iptables -t nat -F REDSOCKS
iptables -t nat -X REDSOCKS
iptables -t nat -N REDSOCKS
# ignore local addr
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN
# everything else through proxy
## 12345: http-relay; 12346: http-connect

# iptables -t nat -A REDSOCKS -p tcp --dport 80 -j REDIRECT --to-ports 12345
# iptables -t nat -A REDSOCKS -p tcp --dport 443 -j REDIRECT --to-ports 12346
# iptables -t nat -A REDSOCKS -p tcp --dport 11371 -j REDIRECT --to-ports 12345
# iptables -t nat -A REDSOCKS -p tcp --dport 6667 -j REDIRECT --to-ports 12346
# iptables -t nat -A REDSOCKS -p tcp --dport 21 -j REDIRECT --to-ports 12346
# iptables -t nat -A REDSOCKS -p tcp --dport 20 -j REDIRECT --to-ports 12346
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12346

iptables -t nat -A OUTPUT -p tcp -j REDSOCKS

# iptables -t nat -A PREROUTING -p tcp --dport 11371 -j REDSOCKS
# iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDSOCKS
# iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDSOCKS
# iptables -t nat -A PREROUTING -p tcp --dport 6667 -j REDSOCKS
# iptables -t nat -A PREROUTING -p tcp --dport 21 -j REDSOCKS
# iptables -t nat -A PREROUTING -p tcp --dport 20 -j REDSOCKS
iptables -t nat -A PREROUTING -p tcp -j REDSOCKS
