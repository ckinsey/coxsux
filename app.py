import socket
import time

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


CYELLOW = '\x1b[0;33m'
CGREEN = '\x1b[0;32m'
CRED = '\x1b[0;31m'
CEND = '\x1b[0m'

def color_latency(latency):
    
    if latency < 60:
        color = CGREEN
    elif latency < 120:
        color = CYELLOW
    else:
        color = CRED

    
    return f"{color}{latency:.0f}ms{CEND}"

def test_network():
    REMOTE_SERVER = 'fast.com'
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except:
        pass

    return False

if __name__ == '__main__':

    bucket = "netmon"
    org = "lofty"
    token = "drG6_43doCj2MgQG2PbZ62f0QO7nBgmMO9C4_ILfbJeshOmxhNBR5NSkFxf4US6hrt8GSxn8hhMJjB1wvOVgpw=="
    # Store the URL of your InfluxDB instance
    url = "http://influx:8086"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)



    while True:
        start = time.perf_counter()
        result = test_network()
        stop = time.perf_counter()

        latency = (stop - start) * 1000


        if test_network():
            print(f"[{color_latency(latency)} ] [{time.ctime()}]\tNetwork up...")
            p = influxdb_client.Point("connection_stat").field("latency", latency)
        else:
            print(f"[{CRED}ERR {CEND}] [{time.ctime()}]Network down, timeout out after {latency:.0f}ms...")
            p = influxdb_client.Point("connection_stat").field("latency", -1)

        write_api.write(bucket=bucket, org=org, record=p)
        
        time.sleep(60)