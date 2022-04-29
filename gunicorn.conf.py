# server socket


bind = '127.0.0.1:5000'
# worker
workers = 2
worker_class = 'sync'
timeout = 30
keepalive = 10
# log
errorlog = '/home/wb/Code/lot/LOT_linux_1/log/gunicorn_error'
accesslog = '/home/wb/Code/lot/LOT_linux_1/log/gunicorn_access'
