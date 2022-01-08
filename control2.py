import easytello 
import time

# 設置command line呈現的字串
def command_line():
    print('t: 起飛, l: 降落, ud:先上後下, ba: 查電量')

# 自定義command
def call_command(t,cmd):
   
        if cmd=='t':
            t.takeoff()
        elif cmd=='l':
            t.land()
        elif cmd=='ud':
            t.up(20)
            t.down(20)
        elif cmd=='ba':
            status=t.send_command('battery?')
            print('battery=%s' % status)
        elif cmd=='so':
            t.streamon()
        elif cmd=='sf':
            t.streamoff()
        

def main():
    
    t=easytello.Tello()
    while True:
        # 異常處理
        try:
            command_line()
            # 顯示電池電量
            message=("電池電量剩下%s%%>>" % t.get_battery())
            cmd = input(message)

            if cmd.lower() in ('end', 'exit', 'quit'):
                print ('Exit')
                break
            else:
                call_command(t,cmd)

            if(t.get_battery()<10):
                print("電池電量剩下%s%%低於10" % t.get_battery())
                break
        except Exception as e:
            print('Err:',e)
        except KeyboardInterrupt:
            print ('\n KeyboardInterrupt\n')
            break


if __name__ == '__main__':
    main()
                



