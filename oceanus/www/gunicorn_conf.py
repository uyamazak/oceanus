import multiprocessing
proxy_protocol = True
x_forwarded_for_header = "X-Real-IP"
bind = ":80"
reload = True
loglevel = "debug"
#workers = multiprocessing.cpu_count() * 2 + 1
workers = 1
