import os


worker_class = "gevent"
proxy_protocol = True
x_forwarded_for_header = "X-Real-IP"
bind = ":80"
reload = True
timeout = 5
loglevel = "debug"


def worker_exit(server, worker):
    print("worker_exit server:{}, worker:{}".format(server, worker))
    print("os._exit(4) with worker's exit")
    os._exit(4)
