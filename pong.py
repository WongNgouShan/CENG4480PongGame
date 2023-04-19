from sense_hat import SenseHat
from time import sleep
from multiprocessing.sharedctypes import Value, Array
import copy
import random
import multiprocessing

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
		
		if host:
			sense.set_pixel(ball[0]-8,ball[1],B)
			sense.set_pixel(7,paddle1_y.value,W)
			sense.set_pixel(7,paddle1_y.value+1,W)
			sense.set_pixel(7,paddle1_y.value-1,W)
		else:
			sense.set_pixel(ball[0],7-ball[1],B)
			sense.set_pixel(7,7-paddle2_y.value,W)
			sense.set_pixel(7,7-paddle2_y.value+1,W)
			sense.set_pixel(7,7-paddle2_y.value-1,W)
		
		if game_running.value == 0: 
			break
			
		sleep(0.25)
	return
	
def joystick(sense,paddle1_y,paddle2_y):
	while True:
		event = sense.stick.wait_for_event()
		if event.action=='pressed':
			print("[{:.2f}] {}".format(event.timestamp, event.direction))
			if event.direction == 'middle':
				pass
			elif event.direction == 'up':
				if paddle1_y.value > 1:
					paddle1_y.value-=1
			elif event.direction == 'down':
				if paddle1_y.value < 6:
					paddle1_y.value+=1
			elif event.direction == 'left':
				pass
			elif event.direction == 'right':
				pass
            
def control(sense,paddle1_y,paddle2_y,ball,ball_velo,host,game_running,p1_score,p2_score):
    while True:
            
        if ball[0] == 15:
            game_running.value = 0
            p1_score.value -= 1
            break
			
        if ball[0] == 0:
            game_running.value = 0
            p2_score.value -= 1
            break
			
        if ball[0] == 14 and ball_velo[0] > 0:
            if ball[1] >= paddle1_y.value-1 and ball[1] <= paddle1_y.value+1:
                ball_velo[0] = -ball_velo[0]
		
		#to be remove later
        if ball[0] == 8 and ball_velo[0] < 0:
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
    
if __name__ == "__main__": 
    
	sense = SenseHat()

	#pipe1 = multiprocessing.Pipe() 
	host = Value('i',1)
	game_running = Value('i',0)

	paddle1_y = Value('i',4)
	paddle2_y = Value('i',3)
	ball = Array('i',[8,4]) #x[0-15],y[0-7]
	ball_velo = Array('i',[1,-1])

	p1_score = Value('i',5)
	p2_score = Value('i',5)
	
	while p1_score.value != 0 and p2_score.value != 0:
		
		sense.set_rotation(0)
	
		display(sense,paddle1_y,paddle2_y,ball,host,game_running)

		while True:
			event = sense.stick.wait_for_event()
			if event.action=='pressed':
				if event.direction == 'middle':
					game_running.value = 1
					break

		p1 = multiprocessing.Process(target=display, args=(sense,paddle1_y,paddle2_y,ball,host,game_running))
		p2 = multiprocessing.Process(target=control, args=(sense,paddle1_y,paddle2_y,ball,ball_velo,host,game_running,p1_score,p2_score))
		p3 = multiprocessing.Process(target=joystick, args=(sense,paddle1_y,paddle2_y))
		p1.start()
		p2.start()
		p3.start()

		p1.join()
		p2.join()
		p3.terminate()

		sense.set_rotation(270)
		
		if host.value == 1:
			sense.show_letter(digit_to_char(p1_score.value),W,BK)
		else:
			sense.show_letter(digit_to_char(p2_score.value),W,BK)
			
		sleep(1)
		
		if ball[0] == 15:
			ball[0] = 14
			ball[1] = paddle1_y.value
			ball_velo = [-1,ball_velo[1]]		
			
		elif ball[0] == 0:
			ball[0] = 1
			ball[1] = paddle2_y.value
			ball_velo = [-1,ball_velo[1]]
		
	sense.set_rotation(270)
	
	if p1_score.value == 0 and host.value == 1 or p2_score.value == 0 and host.value == 0:
		sense.set_pixels(lose)
	else:
		sense.set_pixels(win)
	
	sleep(2)

