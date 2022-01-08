from djitellopy import tello
import cv2
import time 
import socket
import threading
from PIL import Image
import pytesseract

me = tello.Tello()
me.connect()

def reg():
    img = cv2.imread('1.jpg', 1)

    cv2.imshow('img', img)
    img_shape = img.shape

    h = img_shape[0]
    w = img_shape[1]
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dst = 255 - gray
    text = pytesseract.image_to_string(dst, lang='eng')
    text = text.replace(" ","")
    text = text.replace("\n","")
    print(text)
    return text

#region  有用到receive的response 其他是我加的路徑函式
#python Email內容
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
content = MIMEMultipart()  #建立MIMEMultipart物件
content["subject"] = "到貨"  #郵件標題
content["from"] = "410721203@gms.ndhu.edu.tw"  #寄件者
content["to"] = "410721227@gms.ndhu.edu.tw" #收件者
content.attach(MIMEText("來領囉"))  #郵件內容

#報錯時修改信件內容
def fix_mail(note = None,road = None):
    if(note == "error"):
        content["subject"] = "故障"  #郵件標題
        content["from"] = "410721203@gms.ndhu.edu.tw"  #寄件者
        content["to"] = "410721203@gms.ndhu.edu.tw" #收件者
        content.attach(MIMEText("請求支援，在{}".format(road)))  #郵件內容

#設定SMTP伺服器
import smtplib
def send_mail():
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("410721203@gms.ndhu.edu.tw", "rmaxxuiiiljizvbt")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)

# IP and port of Tello
tello_address = ('192.168.10.1', 8889)

# IP and port of local computer
local_address = ('', 9000)

# 建立一個UDP連結以發送指令
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to the local address and port
sock.bind(local_address)

#接收callback訊息 例如:DIY Close
DIY = ""
  
# 定義從Tello接收訊息的函數
def receive():
    global DIY
  # 循環迴圈接收訊息
    while True:
        # 嘗試接收消息，否則顯示異常
        try:
            response, ip_address = sock.recvfrom(1024)
            print("Received message: " + response.decode(encoding='utf-8'))
            DIY = response.decode(encoding = "utf-8")
            
        except Exception as e:
            #有error就發信
            error_mail()
            # If there's an error close the socket and break out of the loop
            sock.close()
            print("socket closed ==>Error receiving: " + str(e))
            break
      
# 建立並在背景執行監聽緒
# 此執行緒使用上述之接收訊息的函數
#持續不斷的運行
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

road_curr = 0

#判斷ERROR放在每個路徑上執行移動指令的後面
def error_mail():
    global DIY
    DIY = me.get_own_udp_object()["responses"]
    print(DIY)

    global road_curr
    if(len(DIY)>0):
        for i in DIY:
            if('error' in str(i)):
                if(road_curr > 0):
                    fix_mail("error", road_curr)
                    send_mail()
                    break

def All_Road(t):
    t.takeoff()
    FirstRoad(t,100)#11*50)
    higher(t)
    FirstCorner(t)
    higher(t)
    SecondRoad(t,50)#6*50)
    higher(t)
    SecondCorner(t)
    higher(t)
    ThirdRoad(t,200) #7*200 +100)
    higher(t)
    Find_target(t)

def FirstRoad(t, x): # 11*50
    total_len = x
    t.move_up(80)
    while total_len > 20:
        close_stop(t)
        t.move_forward(50)
        error_mail()
        total_len -= 50
    road_curr = 1

def FirstCorner(t):
    t.rotate_counter_clockwise(90) #逆時鐘
    if(close_stop(t) == "change"):
        t.move_right(50)
    road_curr = 2

def SecondRoad(t,x): #6*50
    total_len = x
    while total_len > 20:
        close_stop(t)
        t.move_forward(50)
        error_mail()
        total_len -= 50
    road_curr = 3

def SecondCorner(t):
    t.rotate_clockwise(90) #順時鐘
    if(close_stop(t) == "change"):
        t.move_left(50)
    road_curr = 4

def ThirdRoad(t,x):
    total_len = x #7*200 + 50-100
    while total_len > 100:
        close_stop(t)
        t.move_forward(200)
        error_mail()
        total_len-=200
    if  20<= total_len <= 100:
        close_stop(t)
        t.move_forward(total_len)
        error_mail()
        total_len-=total_len #歸零
    road_curr = 5

def Find_target(t):
    t.rotate_counter_clockwise(90)
    
    while True:
        higher(t) #防止高度過低看不到數字
        #拍照
        take_pic(t)
        curr = reg()
        if(curr == "A161"):
            #房號確認成功 開啟挑戰卡探測
            mission_complete(t)
            break
        #以前後號碼做誤差判斷
        elif(curr == "A162"):
            print(curr)
            fix_target_position(t,"back")
        elif(curr == "A160"):
            print(curr)
            fix_target_position(t,"forward")
        else:
            fix_target_position(t,"back")
        

def fix_corner_way(t, right, left):
    if(right > 0): #如果右邊遮擋 要往左偏航 #right >left
        t.move_left(right) #50 或是 遮擋比例
    if(left > 0):  #left > right
        t.move_right(left)

def fix_target_position(t,direction):
    if direction == "back":
        t.rotate_counter_clockwise(90) #轉到原路徑反方向
        close_stop(t)
        t.move_forward(50)
        error_mail()
        t.rotate_clockwise(90)
    if direction == "forward":
        t.rotate_clockwise(90)
        close_stop(t)
        t.move_forward(50)
        error_mail()
        t.rotate_counter_clockwise(90)

#完成並降落
def mission_complete(t):
    t.mission_pad_on() 
    t.go_xyz_speed_mid(0,0,100,30,6) #以速度30cm/s飛到6號挑戰卡上方100cm
    time.sleep(2) #防止太早降落
    t.land() 
    send_mail() #寄信

#前方有障礙物就停住
def close_stop(t):
    if("DIY Close" in DIY):
        t.send_control_command("stop")
        time.sleep(1) #停1秒
        return "change"
    else:
        return
        
#利用tof判斷高度是否足夠 以利拍照
def higher(t):
    dis = t.query_distance_tof()
    if(dis <= 160):
        t.move_up(20)
#endregion

def take_pic(t):
    t.streamon()
    for i in range(20):
        img = t.get_frame_read().frame
        if(i == 10):
            cv2.imwrite("1.jpg",img)
    t.streamoff()

def call_command(me,cmd):
        if ' ' in cmd:
            cmd,x=cmd.split(' ')
            x=int(x)
        #跑全程
        if cmd == "all":
            All_Road(me)
        
            
def main():
    while True:
        try:
            #socket
            sock.sendto("command".encode(), tello_address)
            cmd = input()
            call_command(me,cmd)
        except Exception as e:
            print('Err:',e)
        except KeyboardInterrupt:
            print ('\n KeyboardInterrupt\n')
            break


if __name__ == '__main__':
    main()

