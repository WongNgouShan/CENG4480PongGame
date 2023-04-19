R = (180, 0, 0)
G = (0, 200, 0)
B = (0, 0, 180)
BK = (0,0,0)
W = (180,180,180)

WG = (100,100,100) #White Gray
BG = (0, 0, 100) #Blue Gray

win = [R,BK,R,BK,R,BK,W,BK,
R,BK,R,BK,R,BK,W,BK,
BK,R,BK,R,BK,BK,W,BK,
BK,BK,BK,BK,BK,BK,W,BK,
R,BK,R,R,BK,BK,W,BK,
R,BK,R,BK,R,BK,BK,BK,
R,BK,R,BK,R,BK,W,BK,
BK,BK,BK,BK,BK,BK,BK,BK]

lose = [WG,BK,BK,BK,BG,BG,BG,BK,
WG,BK,BK,BK,BG,BK,BG,BK,
WG,WG,WG,BK,BG,BG,BG,BK,
BG,BG,BG,BK,WG,WG,WG,BK,
BG,BK,BK,BK,WG,BK,BK,BK,
BG,BG,BG,BK,WG,WG,WG,BK,
BK,BK,BG,BK,WG,BK,BK,BK,
BG,BG,BG,BK,WG,WG,WG,BK]

join_p2 = [BK,B,B,BK,BK,B,B,BK,
BK,B,BK,B,BK,BK,BK,B,
BK,B,B,BK,BK,B,B,BK,
BK,B,BK,BK,BK,B,B,B,
BK,BK,BK,BK,BK,BK,BK,BK,
BK,BK,BK,BK,BK,BK,BK,BK,
BK,BK,B,BK,B,BK,B,BK,
BK,BK,BK,BK,BK,BK,BK,BK]

joy = [1,1,2,2,2,1,BK,1,
BK,1,2,BK,2,BK,1,BK,
1,BK,2,2,2,BK,1,BK]

tilt = [1,1,1,2,1,2,2,2,
BK,1,BK,2,1,BK,2,BK,
BK,1,BK,2,1,1,2,BK]

BK_row = [BK,BK,BK,BK,BK,BK,BK,BK]

p1 = [BK,1,1,BK,BK,1,1,BK,
BK,1,BK,1,BK,BK,1,BK,
BK,1,1,BK,BK,BK,1,BK,
BK,1,BK,BK,BK,1,1,1]

p2 = [BK,1,1,BK,BK,1,1,BK,
BK,1,BK,1,BK,BK,BK,1,
BK,1,1,BK,BK,1,1,BK,
BK,1,BK,BK,BK,1,1,1]

def get_screen(control, player, select):
    return [(R if select == "up" else BG) if x == 1 \
    else (W if select == "up" else WG) if x == 2 \
    else BK \
    for x in (joy if control == "joy" \
    else tilt if control == "tilt" \
    else BK_row*3)] + \
    BK_row + \
    [(R if select == "down" else BG) if x == 1 \
    else (W if select == "down" else WG) if x == 2 \
    else BK \
    for x in (p1 if player == "p1" \
    else p2 if player == "p2" \
    else BK_row*4)]