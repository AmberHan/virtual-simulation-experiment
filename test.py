# 数据库端
# -*- coding:utf8 -*-
import paho.mqtt.client as mqtt
from multiprocessing import Process, Queue
import pymssql
import time

MQTTHOST = "10.191.17.10"
MQTTPORT = 1883
mqttClient = mqtt.Client()
q = Queue()

serverName = '10.191.17.10'
userName = 'xnfz'
passWord = 'yzu2019@ydh'

# 建立连接并获取cursor
conn = pymssql.connect(serverName, userName, passWord, "AgriculturalData")
cursor = conn.cursor()
if not cursor:
    raise (NameError, "连接数据库失败")


# 连接MQTT服务器
def on_mqtt_connect():
    mqttClient.connect(MQTTHOST, MQTTPORT, 60)
    mqttClient.loop_start()


# 消息处理函数,  机器号,N,P,K
def on_message_come(lient, userdata, msg):
    # print(msg.topic + ":" + str(msg.payload.decode("utf-8")))
    str = msg.payload.decode("utf-8")
    list = str.split(',', 3)
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    listData = [list[0], now_time, list[1], list[2], list[3]]
    print(listData)
    cursor.executemany("INSERT INTO AgriculturalTable VALUES (%d, %d, %d,%d, %d)",
                       [(listData[0], listData[1], listData[2], listData[3], listData[4])])
    conn.commit()

    # print("数据1", str(msg.payload.decode("utf-8")))
    # q.put(msg.payload.decode("utf-8"))  # 代码放入队列
    # print("数据2", msg.payload.decode("utf-8"))
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
        talk("/camera/person/num/result", msg, pid)

    # subscribe 消息订阅


def on_subscribe():
    mqttClient.subscribe("C1", 1)  # 订阅主题为"C1"
    mqttClient.on_message = on_message_come  # 消息到来处理函数

    # 执行订阅信息


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


def main():
    on_mqtt_connect()  # 开启MQTT
    on_subscribe()  # 订阅MQTT数据
    while True:
        pass


if __name__ == '__main__':
    main()
