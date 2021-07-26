"""
Run this file to run:
net\__main__.py
web\index.py
detect\anomaly_service.py
"""
from server.detect import anomaly_service
from server.net import __main__
from server.web import index
from multiprocessing import Process
import os
import server.constants as const

if __name__ == '__main__':
    a_service = Process(target=anomaly_service.main)
    a_service.start()
    net_cont = Process(target=__main__.main)
    net_cont.start()
    if const.WEB_DEBUG:
        web = Process(target=index.main)
        web.start()
    else:
        os.system(f'gunicorn server.web.index:server --bind={const.WEB_BIND}')
    a_service.join()
