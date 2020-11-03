# 主机端（1号主机）
# -*- coding:utf8 -*-
import paho.mqtt.client as mqtt
from multiprocessing import Process, Queue
import serial  # 导入模块
import serial.tools.list_ports
import os
import time

MQTTHOST = "10.191.17.10"
MQTTPORT = 1883
mqttClient = mqtt.Client()
q = Queue()


# 连接MQTT服务器
def on_mqtt_connect():
    mqttClient.connect(MQTTHOST, MQTTPORT, 60)
    mqttClient.loop_start()


# execute command, and return the output
def execCmd(cmd):
    r1 = os.popen(cmd)
    result1 = r1.readlines()
    ReturnData = " ".join(result1)
    r1.close()
    return ReturnData


# 消息处理函数
def on_message_come(client, userdata, msg):
    # print(msg.topic + ":" + str(msg.payload.decode("utf-8")))
    # q.put(msg.payload.decode("utf-8"))  # 代码放入队列
    print("主机代码:", msg.payload.decode("utf-8"))
    if ("D" in msg.payload.decode("utf-8")):
        cmd1 = "F:\\bat\\1.bat"  # 编译学生代码
        cmd2 = "F:\\bat\\cspy.bat  F:\\4.1-P2P模块 - 副本\\4.1-P2P不转换\\Release\\Exe\\p2p.hex"  # 下载启动
        ReturnData = execCmd(cmd1)  # 编译情况
        print(ReturnData)
        os.popen(cmd2)
    if ("Reset," in msg.payload.decode("utf-8")):
        cmd3 = "F:\\bat\\2.bat"  # 编译初始程序
        cmd4 = "F:\\bat\\cspy.bat  F:\\4.1-P2P模块\\4.1-P2P不转换\\Release\\Exe\\p2p.hex"  # 下载启动
        ReturnData = execCmd(cmd3)  # 编译情况
        os.popen(cmd4)
        print(ReturnData)
    on_publish("R1", ReturnData, 2)  # 发布主题为R1的编译情况
    # on_publish("R1", line, 2)
    # 消息处理开启多进程
    # p = Process(target=talk, args=("/camera/person/num/result", msg.payload.decode("utf-8")))
    # p.start()


def consumer(q, pid):
    print("开启消费序列进程", pid)
    while True:
        if (ser.read(3) == b'\xaa\xaa\x20'):
            print("nnda");
        msg = q.get()
        # p = Process(target=talk, args=("/camera/person/num/result", msg, pid))
        # p.start()
        # talk("/camera/person/num/result", msg, pid)


# subscribe 消息订阅
def on_subscribe():
    mqttClient.subscribe("D1", 1)  # 主题为"D1"
    mqttClient.on_message = on_message_come  # 消息到来处理函数


# publish 消息发布
def on_publish(topic, msg, qos):
    mqttClient.publish(topic, msg, qos);


# 多进程中发布消息需要重新初始化mqttClient
def talk(topic, msg, pid):
    # cameraPsersonNum = camera_person_num.CameraPsersonNum(msg)
    # t_max, t_mean, t_min = cameraPsersonNum.personNum()
    # time.sleep(20)
    print("消费消息", pid, msg)
    mqttClient2 = mqtt.Client()
    mqttClient2.connect(MQTTHOST, MQTTPORT, 1)
    mqttClient2.loop_start()
    mqttClient2.publish(topic, '{"max":' + str(t_max) + ',"mean":' + str(t_mean) + ',"min:"' + t_min + '}', 1)
    mqttClient2.disconnect()


try:
    port_list = list(serial.tools.list_ports.comports())
    print(port_list)
    if len(port_list) == 0:
        print('无可用串口,请重新连接')
    else:
        for i in range(0, len(port_list)):
            print(port_list[i])
    portx = "COM3"
    bps = 9600
    # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
    timex = 5
    # 打开串口，并得到串口对象
    ser = serial.Serial(portx, bps, timeout=timex)
    '''print("串口详情参数：", ser)
    print(ser.port)#获取到当前打开的串口名
    print(ser.baudrate)#获取波特率   
    print("写总字节数:",result)'''
    # print(ser.read())#读一个字节
    # print(ser.read(10).decode("gbk"))#读十个字节
    # print(ser.readline().decode("gbk"))#读一行
    # print(ser.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
    # print(ser.in_waiting)#获取输入缓冲区的剩余字节数
    # print(ser.out_waiting)#获取输出缓冲区的字节数

    # 循环接收数据，此为死循环，可用线程实现
    on_mqtt_connect()  # 开启MQTT
    on_subscribe()  # 订阅MQTT代码
    i = 0
    while True:
        if ser.in_waiting:
            str = ser.read()
            if (str == b'*'):
                i = i + 1
                receivedMachineNum = ord(ser.read(1))
                receivedNH = ord(ser.read(1))
                receivedNL = ord(ser.read(1))
                receivedPH = ord(ser.read(1))
                receivedPL = ord(ser.read(1))
                receivedKH = ord(ser.read(1))
                receivedKL = ord(ser.read(1))
                receivedN = receivedNH * 16 * 16 + receivedNL
                receivedP = receivedPH * 16 * 16 + receivedPL
                receivedK = receivedKH * 16 * 16 + receivedKL
                list = [receivedMachineNum, receivedN, receivedP, receivedK]
                print(list)
                Data = "{},{},{},{}".format(receivedMachineNum, receivedN, receivedP, receivedK)
                # print(i)
                if (i % 5 == 0):
                    i = 0
                    on_publish("C1", Data, 2)  # 发布主题为C1的数据
                time.sleep(5)
    ser.close()  # 关闭串口
except Exception as e:
    print("---异常---：", e)
