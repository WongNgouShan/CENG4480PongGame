from sense_hat import SenseHat
from time import sleep
import time
from multiprocessing.sharedctypes import Value, Array
import copy
import random
import multiprocessing

from paho.mqtt import client as mqtt_client
import paho.mqtt.publish
import paho.mqtt.subscribe

R = (255, 0, 0)
G = (0, 200, 0)
B = (0, 0, 255)
BK = (0,0,0)
W = (255,255,255)

win = [R,BK,R,BK,R,BK,W,BK,
R,BK,R,BK,R,BK,W,BK,
BK,R,BK,R,BK,BK,W,BK,
BK,BK,BK,BK,BK,BK,W,BK,
W,BK,R,R,BK,BK,W,BK,
W,BK,R,BK,R,BK,BK,BK,
W,BK,R,BK,R,BK,W,BK,
BK,BK,BK,BK,BK,BK,BK,BK]

lose = [W,BK,BK,BK,R,R,R,BK,
W,BK,BK,BK,R,BK,R,BK,
W,W,W,BK,R,R,R,BK,
R,R,R,BK,W,W,W,BK,
R,BK,BK,BK,W,BK,BK,BK,
R,R,R,BK,W,W,W,BK,
BK,BK,R,BK,W,BK,BK,BK,
R,R,R,BK,W,W,W,BK]

def display(sense,paddle1_y,paddle2_y,ball,host,game_running):
	while True:
		sense.clear()
		
		if host.value == 1:
			if ball[0] >= 8:
				sense.set_pixel(ball[0]-8,ball[1],B)
			sense.set_pixel(7,paddle1_y.value,W)
			sense.set_pixel(7,paddle1_y.value+1,W)
			sense.set_pixel(7,paddle1_y.value-1,W)
		else:
			if ball[0] < 8:
				sense.set_pixel(7-ball[0],7-ball[1],B)
			sense.set_pixel(7,7-paddle2_y.value,W)
			sense.set_pixel(7,7-paddle2_y.value+1,W)
			sense.set_pixel(7,7-paddle2_y.value-1,W)
		
		if game_running.value == 0: 
			break
			
		sleep(0.25)
	return
	
def joystick(sense,host,paddle1_y,paddle2_y):
	
	if host.value == 1:
		paddle_y = paddle1_y
	else:
		paddle_y = paddle2_y
		
	while True:
		event = sense.stick.wait_for_event()
		if event.action=='pressed':
			print("[{:.2f}] {}".format(event.timestamp, event.direction))
			if event.direction == 'middle':
				pass
			elif event.direction == 'up':
				if host.value == 1:
					if paddle_y.value > 1:
						paddle_y.value-=1
				else:
					if paddle_y.value < 6:
						paddle_y.value+=1
						
			elif event.direction == 'down':
				if host.value == 1:
					if paddle_y.value < 6:
						paddle_y.value+=1
				else:
					if paddle_y.value > 1:
						paddle_y.value-=1
			elif event.direction == 'left':
				pass
			elif event.direction == 'right':
				pass

def IMU(sense,host,paddle1_y,paddle2_y):
	if host.value == 1:
		paddle_y = paddle1_y
	else:
		paddle_y = paddle2_y
	while True:
		roll = sense.get_orientation()["roll"]
		if 0 < roll <= 15:
			paddle_y.value = 4
		elif 15 < roll <= 30:
			paddle_y.value = 5
		elif 30 < roll <= 177:
			paddle_y.value = 6
		elif 360 > roll >= 345:
			paddle_y.value = 3
		elif 345 > roll >= 330:
			paddle_y.value = 2
		elif 330 > roll >= 183:
			paddle_y.value = 1
		sleep(0.05)

def control(sense,paddle1_y,paddle2_y,ball,ball_velo,host,game_running,p1_score,p2_score,pipe_receive,pipe_send):
	while True:

		if ball[0] < 8 and host.value == 1 or ball[0] >= 8 and host.value != 1:
			msg = str(ball[0]) + " " + str(ball[1]) + " " + str(ball_velo[0])+ " " + str(ball_velo[1])
			while pipe_receive.poll():
				pipe_receive.recv()
			pipe_send.send(msg)
			msg = pipe_receive.recv().split()
			ball[0] = int(msg[0])
			ball[1] = int(msg[1])
			ball_velo[0] = int(msg[2])
			ball_velo[1] = int(msg[3])
			print(ball[0], ball[1])

		if ball[0] == 15:
			msg = str(ball[0]) + " " + str(ball[1]) + " " + str(ball_velo[0])+ " " + str(ball_velo[1])
			pipe_send.send(msg)

			game_running.value = 0
			p1_score.value -= 1
			break
			
		if ball[0] == 0:
			msg = str(ball[0]) + " " + str(ball[1]) + " " + str(ball_velo[0])+ " " + str(ball_velo[1])
			pipe_send.send(msg)

			game_running.value = 0
			p2_score.value -= 1
			break

		if ball[0] == 14 and ball_velo[0] > 0:
			if ball[1] >= paddle1_y.value-1 and ball[1] <= paddle1_y.value+1:
				ball_velo[0] = -ball_velo[0]
			
		if ball[0] == 1 and ball_velo[0] < 0:
			if ball[1] >= paddle2_y.value-1 and ball[1] <= paddle2_y.value+1:
				ball_velo[0] = -ball_velo[0]
				
		if ball[1] == 0 and ball_velo[1] < 0:
			ball_velo[1] = -ball_velo[1]
		
		if ball[1] == 7 and ball_velo[1] > 0:
			ball_velo[1] = -ball_velo[1]
				
		ball[0] = ball[0]+ball_velo[0]
		ball[1] = ball[1]+ball_velo[1]
		
		sleep(0.5)
	
	return

def digit_to_char(digit):
	if type(digit) is not int:
		return ' ' 
		
	if digit == 0:
		return '0'
		
	if digit == 1:
		return '1'
		
	if digit == 2:
		return '2'
		
	if digit == 3:
		return '3'
		
	if digit == 4:
		return '4'
		
	if digit == 5:
		return '5'
		
	if digit == 6:
		return '6'
		
	if digit == 7:
		return '7'
		
	if digit == 8:
		return '8'
		
	if digit == 9:
		return '9'
	
	return ' '    
	
def connection_ball(ball, host, pipe_send, pipe_receive):
	broker = 'broker.emqx.io'
	port = 1883
	if host.value == 1:
		topic_ball1 = "pong/ball/1"
		topic_ball2 = "pong/ball/2"
	else:
		topic_ball1 = "pong/ball/2"
		topic_ball2 = "pong/ball/1"
	# generate client ID with pub prefix randomly
	client_id = f'python-mqtt-{random.randint(0, 1000)}'
	username = 'emqx'
	password = '**********'

	def on_connect(client, userdata, flags, rc):
		if rc == 0:
			print("(ball)Connected to MQTT Broker!")
		else:
			print("Failed to connect, return code %d\n", rc)

	client = mqtt_client.Client(client_id)
	client.username_pw_set(username, password)
	client.on_connect = on_connect
	client.connect(broker, port)

	def on_message(client, userdata, msg):
		print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
		pipe_send.send(msg.payload.decode())
	client.subscribe(topic_ball2)
	client.on_message = on_message
	client.loop_start()

	while True:
		msg = pipe_receive.recv()
		result = client.publish(topic_ball1, msg)
		status = result[0]
		if status == 0:
			print(f"Send `{msg}` to topic `{topic_ball1}`")
		else:
			print(f"Failed to send message to topic {topic_ball1}")
			
	return
	
# def connection_paddle(paddle, pipe):
# 	broker = 'broker.emqx.io'
# 	port = 1883
# 	topic_paddle = "pong/paddle"
# 	# generate client ID with pub prefix randomly
# 	client_id = f'python-mqtt-{random.randint(0, 1000)}'
# 	username = 'emqx'
# 	password = '**********'

# 	def on_connect(client, userdata, flags, rc):
# 		if rc == 0:
# 			print("(paddle)Connected to MQTT Broker!")
# 		else:
# 			print("Failed to connect, return code %d\n", rc)

# 	client = mqtt_client.Client(client_id)
# 	client.username_pw_set(username, password)
# 	client.on_connect = on_connect
# 	client.connect(broker, port)
	
# 	if host.value == 1:
# 		def on_message(client, userdata, msg):
# 			print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
# 			paddle2_y.value = int(msg.payload.decode())
# 		client.subscribe(topic_paddle)
# 		client.on_message = on_message
# 		client.loop_forever()
		
# 	else:
# 		client.loop_start()
# 		while True:
# 			msg = pipe.recv()
# 			result = client.publish(topic_paddle, msg)
# 			status = result[0]
# 			if status == 0:
# 				print(f"Send `{msg}` to topic `{topic_paddle}`")
# 			else:
# 				print(f"Failed to send message to topic {topic_paddle}")
# 	return

#host_win(bool): host is the winning one? host(bool): is the player host?
def decide_start_ball(host_win, host):
	if host == True:
		return (not host_win)
	else:
		return host_win
	
    
if __name__ == "__main__": 
	
	auth_info = {"username":'emqx', "password":'**********'}
    
	sense = SenseHat()
	
	#pipe connect_ball to control
	pipe1 = multiprocessing.Pipe() 
	
	#pipe joy to connect_paddle
	pipe2 = multiprocessing.Pipe() 
	
	host = Value('i',1)
	game_running = Value('i',0)

	paddle1_y = Value('i',4)
	paddle2_y = Value('i',3)
	ball = Array('i',[8,4]) #x[0-15],y[0-7]
	ball_velo = Array('i',[1,-1])

	p1_score = Value('i',5)
	p2_score = Value('i',5)
	
	start_ball = decide_start_ball(False, host.value == 1)
	
	
	while p1_score.value != 0 and p2_score.value != 0:
		
		sense.set_rotation(0)
	
		display(sense,paddle1_y,paddle2_y,ball,host,game_running)

		if start_ball:
			while True:
				event = sense.stick.wait_for_event()
				if event.action=='pressed':
					if event.direction == 'middle':
						paho.mqtt.publish.single(topic="pong/start", payload="start", hostname="broker.emqx.io", port=1883, client_id="", auth = auth_info)
						break
		else:
			paho.mqtt.subscribe.simple(topics="pong/start", hostname="broker.emqx.io", port=1883, client_id="", auth=auth_info)
		
		game_running.value = 1

		p1 = multiprocessing.Process(target=display, args=(sense,paddle1_y,paddle2_y,ball,host,game_running))
		p2 = multiprocessing.Process(target=control, args=(sense,paddle1_y,paddle2_y,ball,ball_velo,host,game_running,p1_score,p2_score,pipe1[1],pipe2[0]))
		p3 = multiprocessing.Process(target=IMU, args=(sense,host,paddle1_y,paddle2_y))
		p4 = multiprocessing.Process(target=connection_ball, args=(ball,host,pipe1[0],pipe2[1]))
		# p5 = multiprocessing.Process(target=connection_paddle, args=(paddle2_y,pipe2[1]))
		p1.start()
		p2.start()
		p3.start()
		p4.start()
		# p5.start()

		p1.join()
		p2.join()
		p3.terminate()
		p4.terminate()
		# p5.terminate()

		sense.set_rotation(270)
		
		if host.value == 1:
			sense.show_letter(digit_to_char(p1_score.value),W,BK)
		else:
			sense.show_letter(digit_to_char(p2_score.value),W,BK)
			
		sleep(1)
		
		if ball[0] == 15: #host lose
			start_ball = decide_start_ball(False, host.value == 1)
			ball[0] = 14
			ball[1] = paddle1_y.value
			ball_velo = [-1,ball_velo[1]]		
			
		elif ball[0] == 0: #host win
			start_ball = decide_start_ball(True, host.value == 1)
			ball[0] = 1
			ball[1] = paddle2_y.value
			ball_velo = [1,ball_velo[1]]
		
	p4.terminate()
	
	sense.set_rotation(270)
	
	if p1_score.value == 0 and host.value == 1 or p2_score.value == 0 and host.value == 0:
		sense.set_pixels(lose)
	else:
		sense.set_pixels(win)
	
	sleep(2)

