import requests
from datetime import datetime
import time
from threading import Thread
from src.user import User
import requests
import subprocess
from parse import compile
import json

def req(url: str, data: dict, description: str):
    res = requests.post(url, headers={'Content-Type': "application/json; charset=utf-8"}, data=json.dumps(data))
    if res.status_code == 200:
        print(datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + ' [INFO] : Send json to server - ', description)
        return res
    elif res.status_code == 503:
        print(datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + ' [ERROR] : HTTP/' + str(res.status_code) + " There are not collector server now.")
    elif res.status_code == 500:
        print(datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + ' [ERROR] : HTTP/' + str(res.status_code) + " There are no databases in server now.")
    else:
        print(datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + ' [ERROR] : HTTP/' + str(res.status_code))
    return res

class YarnWorker(Thread):
    __name: str # Thread name
    __user: User
    __url: str

    def __init__(self, name: str, user: User, url: str, metric, metric_name, metric_arg=None):
        super().__init__()
        self.__name = name
        self.__user = user
        self.__url = url
        self.__metric = metric
        self.__metric_name = metric_name
        self.__metric_arg = metric_arg

    def run(self):
        while True:
            # Get data from API
            try:
                data = self.__metric()[self.__metric_name]
            except:
                print(datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + " [ERROR] : "+ self.__name +" - Cannot receive data from hadoop")
                return

            if data != None:
                # Append email and datetime
                data['email'] = self.__user.email
                data['datetime'] = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

                # Send data
                data_res = req(self.__url, data, self.__metric_name)
            else:
                print(datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + " [ERROR] : "+ self.__name +" - Cannot receive data from hadoop")
            time.sleep(5)

class HdfsWorker(Thread):
    __name: str # Thread name
    __user: User
    __url: str

    def __init__(self, name: str, user: User, url: str):
        super().__init__()
        self.__name = name
        self.__user = user
        self.__url = url

    def run(self):
        while True:
            # Get data
            try:
                data = get_hdfs_usage()
            except:
                print(datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + " [ERROR] : "+ self.__name +" - Cannot receive data from hadoop")
                return

            if data != None:
                data['email'] = self.__user.email
                data['datetime'] = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

                # Send data
                data_res = req(self.__url, data, "Hdfs information")
            else:
                print(datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + " [ERROR] : "+ self.__name +" - Cannot receive data from hadoop")
            time.sleep(5)

def get_hdfs_usage():
    log = subprocess.check_output(["hdfs", "dfs", "-df"], universal_newlines=True)
    data = log.splitlines()[1].split()[1:]

    return {
        "size": int(data[0]),
        "used": int(data[1]),
        "available": int(data[2]),
        "usePercentage": int(data[3][:-1]),
    }