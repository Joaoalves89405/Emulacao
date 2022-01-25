import socket, pickle, struct, threading, select, base64, time
import numpy as np
import cv2

BUFF_SIZE = 65536

hostname = socket.gethostname()
localIP = socket.gethostbyname(hostname)

host_ip = '10.0.15.21'  # paste your server ip address here
port = 9090
off_flag = 0


def send_join_request(socket1, server_IP, room):
    message = b''
    serverip_in_bytes = socket.inet_aton(host_ip)
    localIP_in_bytes = socket.inet_aton(localIP)
    message = serverip_in_bytes+localIP_in_bytes+int(room).to_bytes(1, byteorder="big")
    print(serverip_in_bytes)
    print (room)
    print(message)
    #print("SERVER ADDRESS: ", (str(host_ip), port))
    res = socket1.sendto(message, (str(server_IP), port))

def receive_video(client_socket):
    global off_flag
    fps,st,frames_to_count,cnt = (0,0,20,0)
    latency = 0
    latency_total = 0
    tns = 0
    n_frames = 0
    
    while True:
        r,_,_ = select.select([client_socket],[],[], 0)
        if r:
            packet,_ = client_socket.recvfrom(BUFF_SIZE)  # 4K, range(1024 byte to 64KB)
            if not packet: 
                #print("ENDED")
                break
            latency_total += time.time_ns()- int(packet[-19:].decode())
            data = base64.b64decode(packet[4:-19], ' /')
            n_frames+=1
            if n_frames == 50:
                latency = latency_total/n_frames
                latency_total = 0
                #print(latency)
                n_frames = 0
                pass
            #print(data)
            npdata = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(npdata, 1)
            frame = cv2.putText(frame,'Latency: '+str(round((latency*0.000001), 2))+' ms FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
            cv2.imshow("RECEIVING VIDEO", frame) # show video frame at client side
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): # press q to exit video
                break
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count/(time.time()-st))
                    # latency = time.time_ns()-tns
                    # tns = time.time_ns()
                    st=time.time()
                    cnt=0
                except Exception as e:
                    print(e)
                    pass
            cnt+=1

    cv2.destroyAllWindows()
    client_socket.close()



if __name__ == '__main__':


    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    client_socket.bind((localIP, port))
    
    network = input("Use overlay(o) or underlay(u) network?\n: ")
    if network == "o":
        server_ip = localIP
        port = 9000
    elif network == "u":
        server_ip = host_ip
    else:
        print("Wrong input!")
    while True:
        res = input("\nEnter room: \n1) Nature \n2) Action \n3) Horror \n4) Animation \n : ")
        send_join_request(client_socket, server_ip, res)
        receiver_thread = threading.Thread(target = receive_video, args = (client_socket,))
        receiver_thread.start()
        leave = input("If you intend to leave type 'x'\n")
        if leave == "x":
            off_flag = 1
            break

    receiver_thread.join()