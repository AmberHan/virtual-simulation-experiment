# -*- coding:utf8 -*-
import paho.mqtt.client as mqtt
from multiprocessing import Process, Queue
import serial  # 导入模块
import serial.tools.list_ports

MQTTHOST = "10.191.0.63"
MQTTPORT = 1883
mqttClient = mqtt.Client()
q = Queue()


# 连接MQTT服务器
def on_mqtt_connect():
    mqttClient.connect(MQTTHOST, MQTTPORT, 60)
    mqttClient.loop_start()


# 消息处理函数
def on_message_come(lient, userdata, msg):
    # print(msg.topic + ":" + str(msg.payload.decode("utf-8")))
    q.put(msg.payload.decode("utf-8"))  # 代码放入队列
    print("代码:", msg.payload.decode("utf-8"))
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
    mqttClient.subscribe("D01", 1)  # 主题为"D01"
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
    while True:
        if ser.in_waiting:
            # print(ser.read())
            str = ser.read()
            #  print(str);
            if (str == b'*'):
                receivedMachineNum = ord(ser.read(1))
                receivedN = ord(ser.read(1))
                receivedP = ord(ser.read(1))
                receivedK = ord(ser.read(1))
                list = [receivedMachineNum, receivedN, receivedP, receivedK]
                print(list)
                Data = "{},{},{},{}".format(receivedMachineNum, receivedN, receivedP, receivedK)
                on_publish("C01", Data, 2)
    ser.close()  # 关闭串口
except Exception as e:
    print("---异常---：", e)
