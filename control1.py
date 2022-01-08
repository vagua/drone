# 此範例為如何用Python將SDK命令透過鍵盤程控Tello
import socket
import threading
import time
import sys

# IP and port of Tello
tello_address = ('192.168.10.1', 8889)

# IP and port of local computer
local_address = ('', 9000)

# 建立一個UDP連結以發送指令
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to the local address and port
sock.bind(local_address)


# 定義發送訊息給Tello的函數
def send(message,delay):
  # 嘗試發送消息，否則顯示異常
  try:
    sock.sendto(message.encode(), tello_address)
    print("Sending message: " + message)
  except Exception as e:
    print("Error sending: " + str(e))
  #等待接收訊息 若takeoff 8sec. flip 5sec. land 5sec.
  if message=='takeoff':  
    delay=8
  elif message.find('flip')>=0:  
    delay=5
  elif message=='land':  
    delay=5
  time.sleep(delay)
  
# 定義從Tello接收訊息的函數
def receive():
  # 循環迴圈接收訊息
  while True:
    # 嘗試接收消息，否則顯示異常
    try:
      response, ip_address = sock.recvfrom(128)
      print("Received message: " + response.decode(encoding='utf-8'))
    except Exception as e:
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

# 操作指示
print("請輸入Tello SDK指令，並按下'Enter'鍵.或輸入'quit'離開程式.")

# 一直循環等待指令的輸入或是使用'quit'或ctrl-c退出
while True:
  try:
    # 讀取鍵盤輸入 
    message = input('')
    # 當收到'quit'指令，則結束程式並關閉連結
    if 'quit' in message:
      print("Program exited sucessfully")
      sock.close()
      break
    
    # 送出指令
    send(message,3)
    
  # 處理當使用ctrl-c時之例外處理
  except KeyboardInterrupt as e:
    sock.close()
    break
#左#000r000000r000000r000000rrrrrrrrrrrrrrrr0r00000000r00000000r0000
#右#0000r00000000r00000000r0rrrrrrrrrrrrrrrr000000r000000r000000r000
#上#000rr00000rrrr000r0rr0r0r00rr00r000rr000000rr000000rr000000rr000
#下#000rr000000rr000000rr000000rr000r00rr00r0r0rr0r000rrrr00000rr000
#叉叉#p000000p0p0000p000p00p00000pp000000pp00000p00p000p000p0p000000p




