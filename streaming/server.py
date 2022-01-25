# This code is for the server
# Lets import the libraries
import socket, cv2, pickle, struct, imutils, time, threading, select, base64, math

BUFF_SIZE = 65536
# Socket Create
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('HOST IP:', host_ip)
port = 9090
socket_address = (host_ip, port)
off_flag = 0
print("LISTENING AT:", socket_address)
network = 0

ROOM1_FRAME_N = 0 


def receive_requests(server_socket):
    global off_flag
    global ROOM1_FRAME_N
    active_threads = []
    while off_flag == 0:
        r,_,_ = select.select([server_socket],[],[], 0)
        if r:
            rq = server_socket.recv(9)
            #sprint("THIS is the ReQuest ", rq[4:8])

            client_ip = socket.inet_ntoa(rq[4:8])
            #print (client_ip)
            room = rq[8]
            #print(room)
            streaming_thread = threading.Thread(target=stream_video, args=(server_socket,client_ip,room, ROOM1_FRAME_N+3, ))
            streaming_thread.start()
            active_threads.append(streaming_thread)
    for thread in active_threads:
            thread.join()

    server_socket.close()
def stream_video(server_socket, client_IP, room, frame_to_start):
        global network
        global ROOM1_FRAME_N
        global port
        vid = cv2.VideoCapture('video.mp4')
        vid.set(cv2.CAP_PROP_FPS, 60)
        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_to_start)
        #fourcc = cv2.VideoWriter_fourcc(*'X264')
        #out = cv2.VideoWriter('output.mkv', fourcc, 24.0, (1024, 768))
        while (vid.isOpened()):
            _,frame = vid.read()
            #print("Frame n: ", vid.get(cv2.CAP_PROP_POS_FRAMES))
            ROOM1_FRAME_N = vid.get(cv2.CAP_PROP_POS_FRAMES)

            try:
                frame = imutils.resize(frame, width=460)
            except:
                #print("Is empty")
                ROOM1_FRAME_N = 0
                break
            encoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = b''
            message = socket.inet_aton(client_IP) + base64.b64encode(buffer) + str(time.time_ns()).encode() # pack the serialized data
            #print("BUFFER SIZE: ",len(buffer))
            #out.write(frame)

            try:
                if network == "o":
                    port = 9000 
                    sending_ip = host_ip
                else:
                    sending_ip = client_IP
                server_socket.sendto(message,(sending_ip, port)) #send message or data frames to client
            except Exception as e:
                print(e)
                raise Exception(e)

            #frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            #cv2.imshow('TRANSMITTING VIDEO', frame) # will show video frame on server side.
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        vid.release()
        cv2.destroyAllWindows()






if __name__ == '__main__':


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    server_socket.bind(socket_address)
    network = input("Use overlay(o) or underlay(u) network?\n: ")
    
    receiver_thread = threading.Thread(target = receive_requests, args = (server_socket,))
    receiver_thread.start()
    leave = input("If you intend to leave type 'x'\n")
    if leave == "x":
        off_flag = 1

    receiver_thread.join()