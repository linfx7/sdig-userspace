import socket
import threading
import struct
import os
import psutil
import sched
import time
from flags import *

class notification_client:

    def __init__(self, server, unknown_packet_callback):
        self._running = True
        self._interval = 2
        self._unknown_packet_callback = unknown_packet_callback

        # status notification tcp socket client
        self._sb_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sb_sock.connect(server)

        # status notification thread
        self._sn_trd = threading.Thread(target=self._status_notification)
        self._sn_trd.setDaemon(True)

        # netlink socket client
        self._nl_sock = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, 31)

        # unknown packet processing thread
        self._up_trd = threading.Thread(target=self._unknown_packet)
        self._up_trd.setDaemon(True)


    def _unknown_packet(self):
        # send hello message to kernel
        self._nl_sock.send(struct.pack('IHHIIc', 17, 1, 0, 0, os.getpid(), 'H'))

        # listening message from kernel
        while self._running:
            try:
                # receive packet digest from kernel
                addrs = struct.unpack('IHHII4B4B', self._nl_sock.recv(1024))[5:24]
                # addrs = (10,1,0,10,10,2,0,20)
                self._unknown_packet_callback(addrs)
                # send to controller
                self._sb_sock.sendall(bytearray((NOTIFICATION,0, 0, 0, 0, 1, EVENT, EVENT_PACKET)) + bytearray(addrs))
                self._sb_sock.recv(1024)
            except BaseException, e:
                print e
                break


    def _status_notification(self):
        current = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
        while (self._running):
            try:
                # get status
                # ip address
                ip = psutil.net_if_addrs().get('eth0')[0].address.split('.')
                # ip = psutil.net_if_addrs().get('\xd2\xd4\xcc\xab\xcd\xf8')[1].address.split('.')
                # net speed
                last = current
                current = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
                net_usage = (current - last) / self._interval / (1024 * 1024 / 8)
                # cpu usage
                cpu_usage = psutil.cpu_percent()
                # mem usage
                mem_usage = psutil.virtual_memory().percent
                # construct message
                status_msg = bytearray((NOTIFICATION,0, 0, 0, 0, 1, STATUS, 
                    int(ip[0]), int(ip[1]), int(ip[2]), int(ip[3]),
                    int(net_usage), int(cpu_usage), int(mem_usage)))
                # print status_msg[7], status_msg[8], status_msg[9], status_msg[10], status_msg[11], status_msg[12], status_msg[13]

                # send
                self._sb_sock.sendall(status_msg)
                self._sb_sock.recv(1024)
                
                # wait interval seconds
                time.sleep(self._interval)
            except BaseException, e:
                print e
                break


    def start(self):
        self._running = True
        # send status to controller
        self._sn_trd.start()
        time.sleep(1)
        self._up_trd.start()


    def stop(self):
        self._running = False

        # close netlink socket
        self._nl_sock.close()
        time.sleep(1)
        # say goodbye to controller
        self._sb_sock.sendall(bytearray((NOTIFICATION,0, 0, 0, 0, 1, STATUS)))
        self._sb_sock.recv(1024)
        self._sb_sock.close()
        


