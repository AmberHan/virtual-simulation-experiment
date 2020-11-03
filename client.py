#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import socket

BUF_SIZE = 1024  # 设置缓冲区的大小
server_addr = ('10.191.17.10', 8889)  # IP和端口构成表示地址
while True:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 返回新的socket对象
    except socket.error as msg:
        print("Creating Socket Failure. Error Code : " + str(msg[0]) + " Message : " + msg[1])
        sys.exit()
    client.connect(server_addr)  # 要连接的服务器地址
    dataget = input("请选择你的输入模式(1或2)，1代表请求数据以及重置试验箱，2代表发送代码>")
    if (dataget == '2'):
        client.sendall("Send,1".encode())  # 发送数据到服务器
        data2 = client.recv(BUF_SIZE)  # 从服务器端接收数据
        print(data2.decode("utf-8"))
    if (dataget != '1' and dataget != '2'):
        continue
    while True:
        data = input("Please input some string > ")
        if not data:
            print("input can't empty, Please input again..")
            continue
        if (data == 'n'):
            data = "*,1,N_Data"
        if (data == 'p'):
            data = "*,1,P_Data"
        if (data == 'k'):
            data = "*,1,K_Data"
        if (data == 'all'):
            data = "*,1,All_Data"
        if (data == 're'):
            data = "Reset,1"
        data1 = data.encode()
        client.sendall(data1)  # 发送数据到服务器
        data2 = client.recv(BUF_SIZE)  # 从服务器端接收数据
        print(data2.decode("utf-8"))
        if (dataget == '1' or data == 'quit'):
            break
client.close()
