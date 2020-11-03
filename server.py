# 服务器端
# !/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import paho.mqtt.client as mqtt
import socket  # socket模块
import pymssql
import time
from multiprocessing import Process
import base64, hashlib

serverName = '10.191.17.10'
userName = 'xnfz'
passWord = 'yzu2019@ydh'
Flag = False
Return_Data = ""
MQTTHOST = "10.191.17.10"
MQTTPORT = 1883
mqttClient = mqtt.Client()

BUF_SIZE = 1024  # 设置缓冲区大小
server_addr = ('10.191.17.10', 8889)  # IP和端口构成表示地址


# 连接MQTT服务器
def on_mqtt_connect():
    mqttClient.connect(MQTTHOST, MQTTPORT, 60)
    mqttClient.loop_start()


# 消息处理函数
def on_message_come(lient, userdata, msg):
    # print(msg.topic + ":" + str(msg.payload.decode("utf-8")))
    global Flag
    str = msg.payload.decode("utf-8")
    print("编译返回情况:")
    print(str)
    global Return_Data
    Return_Data = "{}".format(str)
    # client.sendall(Return_Data)  # 返回WebSocket内容
    Flag = True


# 消息订阅
def on_subscribe(TopicMess):
    on_mqtt_connect()  # 开启MQTT
    mqttClient.subscribe(TopicMess, 1)  # 订阅主题
    mqttClient.on_message = on_message_come  # 消息到来处理函数


# 消息取消订阅
def on_unsubscribe(TopicMess):
    mqttClient.unsubscribe(TopicMess)  # 订阅主题


# publish 消息发布
def on_publish(topic, msg, qos):
    mqttClient.publish(topic, msg, qos)


# 检验数据是否符合要求
def checkData(data1, data2):
    matching_word_count = 0
    for index in range(0, len(data2)):
        if data2[index] == data1:
            matching_word_count = matching_word_count + 1
    if (matching_word_count == 2):
        return True
    else:
        return False


# 进行数据处理
def talk(client, client_addr):  # 子进程与客户端的交互内容
    while True:
        try:
            Data = client.recv(BUF_SIZE)  # 从客户端接收请求信息（此时的请求是websocket格式）
            Data = get_data(Data)  # 解析请求信息，下面对解析结果进行判断
            if (Data == ''):
                continue
            print("receive：" + Data)
            check = '*'
            if ('Send,' in Data):
                print("Send Begin!")
                send_msg(client, bytes("Success", encoding="utf-8"))
                MachineCodeIDlist = Data.split(',', 1)  # Data=（Send,主机号）
                MachineCodeID = MachineCodeIDlist[1]
                FileName = "D:/xnfz/daima/%s.txt" % MachineCodeID
                TopicName = "D%s" % MachineCodeID
                TopicReName = "R%s" % MachineCodeID
                with open(FileName, 'wb') as f:
                    f.truncate()  # 清空文件
                while True:
                    with open(FileName, 'a') as f:
                        # 接收代码
                        CodeData = client.recv(1024)
                        CodeData = get_data(CodeData)
                        if (CodeData == ''):
                            continue
                        print("receive codeText:" + CodeData)
                        if CodeData == "quit":  # 代码发送完毕
                            on_subscribe(TopicReName)  # 订阅R主题的编译情况返回信息
                            print(TopicReName + TopicName)
                            on_publish(TopicName, TopicName, 2)  # 发布D主题，内容为D，主机号，对应主机端订阅的内容，进入D判断下
                            # while (Flag is False):
                            #     pass
                            global Flag
                            for i in range(0, 10):  # 最多等待10s
                                if (Flag is False):
                                    time.sleep(1)
                                else:
                                    break
                            global Return_Data
                            Data = Return_Data
                            if (Flag is False):
                                Data = "下载失败，请检查设备连接状况"
                            send_msg(client, bytes(Data, encoding="utf-8"))
                            on_unsubscribe(TopicReName)
                            Flag = False
                            client.close()
                            break
                        # 写入文件
                        f.write(CodeData)
                        # 接受完成标志
                        send_msg(client, bytes("SaveOk", encoding="utf-8"))
            if (Data == "close"):
                client.close()
                break
            if ("Reset," in Data):  # 重置学生代码为正确代码
                print("Begin reset!")
                listR = Data.split(',', 1)  # Data=（Reset,主机号）
                ResID = listR[1]  # 请求的主机号
                TopicResName = "D%s" % ResID
                TopicRetName = "R%s" % ResID
                on_publish(TopicResName, Data, 2)  # 发布D主题，内容为reset，主机号，对应主机端订阅的内容，进入reset判断下
                on_subscribe(TopicRetName)  # 订阅R主题的编译情况返回信息
                for i in range(0, 10):  # 最多等待10s
                    if (Flag is False):
                        time.sleep(1)
                    else:
                        break
                if (Flag is False):
                    # send_msg(client, bytes("下载失败，请检查设备连接状况", encoding="utf-8"))
                    Return_Data = "下载失败，请检查设备连接状况"
                send_msg(client, bytes(Return_Data, encoding="utf-8"))
                on_unsubscribe(TopicRetName)
                Flag = False
                continue
            if (checkData(',', Data) and check in Data):
                # print("cool,you can get my data now")
                # 建立连接并获取cursor
                conn = pymssql.connect(serverName, userName, passWord, "AgriculturalData")
                cursor = conn.cursor()
                if not cursor:
                    raise (NameError, "连接数据库失败")
                print(Data)
                list1 = Data.split(',', 2)
                # 查询记录
                now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 30))
                print(now_time)
                cursor.executemany("SELECT * FROM AgriculturalTable WHERE Machine_Num=%d and Data_Time<%s",
                                   [(list1[1], now_time)])
                # 获取前30s的数据中的最上面的一条记录（如果select本身取的时候有多条数据时，cursor.fetchone将只取最上面的第一条结果）
                row = cursor.fetchone()
                print(row)
                # 循环打印记录(这里只有一条，所以只打印出一条)
                # while row:
                #     print(row)
                #     row = cursor.fetchone()
                conn.close()  # 连接用完后记得关闭以释放资源,关闭数据库
                # if():
                #     client.sendall("NoData")
                if (row == None):
                    send_msg(client, bytes("NoData", encoding="utf-8"))
                if (list1[2] == 'N_Data' and row != None):
                    N_Data = "{}".format(row[3])
                    print(N_Data)
                send_msg(client, bytes(N_Data, encoding="utf-8"))
            if (list1[2] == 'P_Data' and row != None):
                P_Data = "{}".format(row[4])
                print(P_Data)
                send_msg(client, bytes(P_Data, encoding="utf-8"))
            if (list1[2] == 'K_Data' and row != None):
                K_Data = "{}".format(row[5])
                print(K_Data)
                send_msg(client, bytes(K_Data, encoding="utf-8"))
            if (list1[2] == 'All_Data' and row != None):
                All_Data = "{},{},{}".format(row[3], row[4], row[5])
                print(All_Data)
            send_msg(client, bytes(All_Data, encoding="utf-8"))
        continue
    else:
        send_msg(client, bytes(Data, encoding="utf-8"))
        continue

except socket.error as msg:
break


# 修改
def get_headers(data):
    # 将请求头转换为字典
    header_dict = {}
    data = str(data, encoding="utf-8")
    header, body = data.split("\r\n\r\n", 1)
    header_list = header.split("\r\n")
    for i in range(0, len(header_list)):
        if i == 0:
            if len(header_list[0].split(" ")) == 3:
                header_dict['method'], header_dict['url'], header_dict['protocol'] = header_list[0].split(" ")
        else:
            k, v = header_list[i].split(":", 1)
            header_dict[k] = v.strip()
    return header_dict


# WebSocket服务端向客户端发送消息
def send_msg(conn, msg_bytes):
    """
    :param conn: 客户端连接到服务器端的socket对象,即： conn,address = socket.accept()
    :param msg_bytes: 向客户端发送的字节
    :return:
    """
    import struct

    token = b"\x81"  # 接收的第一字节，一般都是x81不变
    length = len(msg_bytes)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)

    msg = token + msg_bytes
    conn.send(msg)
    return True


# 解析websocket格式
def get_data(info):
    payload_len = info[1] & 127
    if payload_len == 126:
        extend_payload_len = info[2:4]
        mask = info[4:8]
        decoded = info[8:]
    elif payload_len == 127:
        extend_payload_len = info[2:10]
        mask = info[10:14]
        decoded = info[14:]
    else:
        extend_payload_len = None
        mask = info[2:6]
        decoded = info[6:]
    bytes_list = bytearray()  # 这里我们使用字节将数据全部收集，再去字符串编码，这样不会导致中文乱码
    for i in range(len(decoded)):
        chunk = decoded[i] ^ mask[i % 4]  # 解码方式
        bytes_list.append(chunk)
    print(bytes_list)  # 错
    if (b'\x03\xe9' in bytes_list):
        body = "close";
    else:
        body = str(bytes_list, encoding='utf-8')
    return body


# 多进程（实现多个客户端同时访问同一服务器）
if __name__ == '__main__':  # 父进程（父进程完成与客户端的连接工作，随后创建子进程）
    on_mqtt_connect()  # 开启MQTT
    try:
        # 生成一个新的socket对象
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Creating Socket Failure. Error Code : " + str(msg[0]) + " Message : " + msg[1])
        sys.exit()
    print("Socket Created!")
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置地址复用
    try:
        server.bind(server_addr)  # 绑定地址
    except socket.error as msg:
        print("Binding Failure. Error Code : " + str(msg[0]) + " Message : " + msg[1])
        sys.exit()
    print("Socket Bind!")
    server.listen(5)  # 监听, 最大监听数为5
    print("Socket listening")
    while True:
        client, client_addr = server.accept()  # 接收TCP连接, 并返回新的套接字和地址, 阻塞函数
        print('Connected by', client_addr)

        # 获取握手消息，magic string ,sha1加密
        # 发送给客户端
        # 握手消息
        dataidx = client.recv(8096)
        headers = get_headers(dataidx)
        # 对请求头中的sec-websocket-key进行加密
        response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
                       "Upgrade:websocket\r\n" \
                       "Connection: Upgrade\r\n" \
                       "Sec-WebSocket-Accept: %s\r\n" \
                       "WebSocket-Location: ws://%s%s\r\n\r\n"
        magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        value = headers['Sec-WebSocket-Key'] + magic_string
        ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())
        response_str = response_tpl % (ac.decode('utf-8'), headers['Host'], headers['url'])
        # 响应【握手】信息
        client.send(bytes(response_str, encoding='utf-8'))
        p = Process(target=talk, args=(client, client_addr))  # 子进程（子进程与客户端具体交互）
        p.start()
    server.close()
