
#found pause simulation:
#sim.simxPauseCommunication(clientID,True)
#import matplotlib.pyplot as plt
import math 
import numpy as np
import GP2_Vrep_V8 as v
from numpy import sin , cos
#from sympy import symbols, Eq, solve
import sim
#import matplotlib.pyplot as plt
import time
#import sympy as sp

import math
#Parameters:
clientID=0
l1 =245
l2 =208.4
a = 112.75
initalheight=390
stride=80
plus2pi=False
stability=True
movement=True
stp = 100

#Functions:

def getjointanglesfromvrep():#transverse,hips,knees

    hipangles = np.zeros((4, 1))
    kneeangles = np.zeros((4, 1))
    transverseangles = np.zeros((4, 1))

    for i in range(hipangles.shape[0]):
        transverseangles[i] = v.get_angles(0 + 3 * i)
        hipangles[i] = v.get_angles(1 + 3 * i)
        kneeangles[i] = v.get_angles(2 + 3 * i)

    return transverseangles, hipangles, kneeangles

def GetEndEffectorPos(transverseangles, hipangles, kneeangles):  # Gets End effectors Positions
    leg_pos_x = [300.78, 300.78, -300.78, -300.78]  # the endeffector position relative to the cg in the x-axis
    leg_pos_y = [123.5, -123.5, -123.5, 123.5]  # the endeffector position relative to the cg in the y-axis
    # This array will have the pos. of the 4 endeffector
    pos2cg = np.zeros((4, 3))
    pos2joint = np.zeros((4, 3))

    for i in range(4):

        x,y,z = forward_kinematics_V3(transverseangles[i,0], hipangles[i,0], kneeangles[i,0])
        pos2cg[i, 0] = (leg_pos_x[i] + x)  # forward/backward (x-axis)
        pos2cg[i, 1] = leg_pos_y[i] - y  # tilting (y-axis)
        pos2cg[i, 2] = z  # Height  (z-axis)
        pos2joint[i, 0] = x  # forward/backward (x-axis)
        pos2joint[i, 1] = y  # tilting (y-axis)
        pos2joint[i, 2] = z  # Height  (z-axis)

    return pos2cg, pos2joint
    
def Move_side(direction):
    if direction == 'r':
        x = [2,3,1,4]
    if direction == 'l':
        x = [1,4,2,3]

    time.sleep(0.5)
    delay = Move_Leg(x[0],direction,stride)
    time.sleep(0.5)
    delay = Move_Leg(x[1],direction,stride)
    time.sleep(0.5)
    Body_mover(direction, 250*delay,stride)
    time.sleep(0.5)
    delay = Move_Leg(x[2],direction,stride)
    time.sleep(0.5)
    delay = Move_Leg(x[3],direction,stride)

    #print("finish")

def Rotate(leg):
    Move_Leg_V2(1,50,-50,initalheight)

def Move_Leg(leg,direction,distance):

    transverses , hips, knees = getjointanglesfromvrep()
    legspos2cg,legspos2joint=GetEndEffectorPos(transverses,hips,knees)#effector pos with respect to cg got correct angles
    trans, hippp, kneeee, delay = Leg_Ellipse_Trajectory(initalheight, distance,direction, transverses[leg-1], hips[leg-1], knees[leg-1]
                                         ,legspos2joint[leg-1,0],legspos2joint[leg-1,1])
    for i in range(hippp.shape[0]):
        v.set_angle(0 + 3 * (leg - 1), trans[i])
        v.set_angle(1 + 3 * (leg - 1), hippp[i])
        v.set_angle(2 + 3 * (leg - 1), kneeee[i])
        time.sleep(delay)

    return delay

def Move_Leg_V2(leg,x_target,y_target,z_target):

    transverses , hips, knees = getjointanglesfromvrep()
    legspos2cg,legspos2joint=GetEndEffectorPos(transverses,hips,knees)#effector pos with respect to cg got correct angles
    trans, hippp, kneeee, delay = Leg_Ellipse_Trajectory_V2(x_target,y_target,z_target, transverses[leg-1], hips[leg-1], knees[leg-1]
                                         ,legspos2joint[leg-1,0],legspos2joint[leg-1,1])
    for i in range(hippp.shape[0]):
        v.set_angle(0 + 3 * (leg - 1), trans[i])
        v.set_angle(1 + 3 * (leg - 1), hippp[i])
        v.set_angle(2 + 3 * (leg - 1), kneeee[i])
        time.sleep(delay)

    return delay



def Leg_Ellipse_Trajectory_V2(x_target,y_target,z_target, Transverse_Angle, hipangle, kneeangle, xt,yt):

    # H = 100 #height
    T = 0.001  # total time for each cycle
    h = 100  # 100 #hsmall
    # intial_leg_height = 300 #from ground to joint
    stp = x_target  # 100 #number of steps even number for some reason
    St = T / stp  # sample time
    xnew = np.zeros([stp, 1], dtype=float)
    t = 0;
    i = 0;


    for t in np.arange(0, T, St):
        xnew[i] =  (s * ((t / T) - ((1 / (2 * np.pi)) * np.sin(2 * np.pi * (t / T)))) - (
                    s / 2) + s / 2) + initial_distance
        i = i + 1;

    tnew = np.zeros([stp, 1], dtype=float)
    i = 0;

    # malhash lazma,ba2a leha lazma
    for t in np.arange(0, stp, 1):
        tnew[i] = St * t
        i = i + 1

    i = 0
    ynew = np.zeros([stp, 1], dtype=float)
    # First part of Ynew in peicewise

    for t in np.arange(0, T / 2, St):
        ynew[i] = (-(h / (2 * np.pi)) * np.sin(((4 * np.pi) / T) * t) + ((2 * h * t) / T) - (h / 2)) + (
                    h / 2) - intial_leg_height
        i = i + 1;

    n = (T / 2)
    for t in np.arange(n, T, St):
        ynew[i] = (-(h / (2 * np.pi)) * np.sin(4 * np.pi - (((4 * np.pi) / T) * t)) - ((2 * h * t) / T) + (
                    (3 * h) / 2)) + (h / 2) - intial_leg_height
        i = i + 1

    theta1 = np.zeros([stp, 1], dtype=float)
    theta2 = np.zeros([stp, 1], dtype=float)
    theta3 = np.zeros([stp, 1], dtype=float)

    i = 0;
    Current_Transverse = Transverse_Angle
    Current_Hip = hipangle
    Current_Knee = kneeangle
    if direction == 'r' or direction == 'l':
        x_pos = [xt]
        y_pos = xnew
        z_pos = ynew
    if direction == 'f' or direction == 'b':
        x_pos = xnew
        y_pos = [yt]
        z_pos = ynew
    for t in np.arange(0, T, St):
        theta1[i], theta2[i], theta3[i] = inverse_kinematics_3d_v6(x_pos[i * x], y_pos[i * y], z_pos[i],
                                                                   Current_Transverse, Current_Hip, Current_Knee)
        Current_Transverse = theta1[i]
        Current_Hip = theta2[i]
        Current_Knee = theta3[i]
        i = i + 1

    return theta1, theta2, theta3, St


def Leg_Ellipse_Trajectory(intial_leg_height,s,direction,Transverse_Angle,hipangle,kneeangle,xt,yt):#Gets angles for leg trajectory  xc stands for current x

    #H = 100 #height
    T = 0.001 #total time for each cycle
    h = 100#100 #hsmall
    #intial_leg_height = 300 #from ground to joint
    stp=100#100 #number of steps even number for some reason
    St=T/stp #sample time
    xnew = np.zeros([stp,1], dtype=float)
    t=0
    i=0

    if direction == 'r':
        initial_distance = yt
        sign = -1
        y = 1
        x = 0
    if direction == 'l':
        initial_distance = yt
        sign = 1
        y = 1
        x = 0
    if direction == 'f':
        initial_distance = xt
        sign = 1
        y = 0
        x = 1
    if direction == 'b':
        initial_distance = xt
        sign = -1
        y = 0
        x = 1

    for t in np.arange(0,T,St):
         xnew[i]=sign*(s*((t/T)-((1/(2*np.pi))*np.sin(2*np.pi*(t/T))))-(s/2)+s/2)+initial_distance
         i=i+1;
    
    
    tnew = np.zeros([stp,1], dtype=float)
    i=0;
    
    # malhash lazma,ba2a leha lazma
    for t in np.arange(0,stp,1):
         tnew[i]=St*t
         i=i+1

    
    i=0
    ynew=np.zeros([stp,1], dtype=float)
     #First part of Ynew in peicewise
     
    for t in np.arange(0,T/2, St):
         ynew[i]=(-(h/(2*np.pi))*np.sin(((4*np.pi)/T)*t)+((2*h*t)/T)-(h/2))+(h/2)-intial_leg_height
         i=i+1;
    
    n=(T/2)
    for t in np.arange(n,T, St):
        ynew[i]= (-(h/(2*np.pi))*np.sin(4*np.pi-(((4*np.pi)/T)*t))-((2*h*t)/T)+((3*h)/2))+(h/2)-intial_leg_height
        i=i+1

    theta1=np.zeros([stp,1], dtype=float)
    theta2=np.zeros([stp,1], dtype=float)
    theta3 = np.zeros([stp, 1], dtype=float)
 
    i=0
    Current_Transverse = Transverse_Angle
    Current_Hip = hipangle
    Current_Knee = kneeangle
    if direction == 'r'or direction == 'l':
        x_pos = [xt]
        y_pos = xnew
        z_pos = ynew
    if direction == 'f' or direction == 'b':
        x_pos = xnew
        y_pos = [yt]
        z_pos = ynew
    for t in np.arange(0,T, St):
        theta1[i] , theta2[i] ,theta3[i]= inverse_kinematics_3d_v6(x_pos[i*x] ,y_pos[i*y] ,z_pos[i] ,Current_Transverse ,Current_Hip ,Current_Knee)
        Current_Transverse= theta1[i]
        Current_Hip = theta2[i]
        Current_Knee = theta3[i]
        i=i+1
    
    return theta1,theta2,theta3,St



#Getting Desired Cg Pos for stability
def getnewcg(pos , SwingLegNo):    # pos is array 4*3
    pos  = np.delete(pos , SwingLegNo-1 ,0  )  # deleting the moving leg co-ordinates
    cg = np.zeros(2)
    cg[0] =  (pos[0,0] + pos[1,0] + pos[2,0])/3
    cg[1] =  (pos[0,1] + pos[1,1] + pos[2,1])/3

    return cg    # cg = [x,y]

def generalbasemover(direction,stride): #moves base with same length as stride

    if direction == 'f':
        sign = 1
    if direction == 'b':
        sign = -1

            
    iteration = []
    transverses , hips, knees = getjointanglesfromvrep()
    legspos2cg,legspos2joint=GetEndEffectorPos(transverses,hips,knees)#effector pos with respect to cg got correct angles 
    transverse = np.zeros((4, 1))
    hip=np.zeros((4,1))
    knee=np.zeros((4,1))
    numofsteps=60
    initial_hip = hips
    initial_knee= knees
#    torquehip=np.zeros(numofsteps)
#    torqueknee=np.zeros(numofsteps)
    for i in range(numofsteps):  #moves the base
        iteration.append(i)
        for ii in range(4):#gets required angles for this step-size    
            transverse[ii],hip[ii],knee[ii]=inverse_kinematics_3d_v6((legspos2joint[ii,0]-sign*(i+1)*((stride)/numofsteps)) ,-a,legspos2joint[ii,2] ,transverses[ii,0] ,initial_hip[ii] ,initial_knee[ii])

        initial_hip = hip
        initial_knee = knee

        for iii in range(4):#moves the stepsize determined
            v.set_angle((0+3*iii),transverse[iii])
            v.set_angle((1+3*iii),hip[iii])
            v.set_angle((2+3*iii),knee[iii])
#            torquehip[i]=vrep.simxGetJointForce (clientID,int(angles_handler[1+3*iii)]),hip[iii])
#            torqueknee[i]=vrep.simxGetJointForce (clientID,int(angles_handler[2+3*iii)]),knee[iii])

        time.sleep(0.005)


def Straightline_Trajectory(leg,plane,num_of_steps,distance):  # moves base with same length as stride
    if plane=='x':
        x = 1
        y = 0
    if plane=='y':
        x = 0
        y = 1

    transverses, hips, knees = getjointanglesfromvrep()
    legspos2cg, legspos2joint = GetEndEffectorPos(transverses, hips, knees)  # effector pos with respect to cg got correct angles
    transverse = np.zeros((num_of_steps, 1))
    hip = np.zeros((num_of_steps, 1))
    knee = np.zeros((num_of_steps, 1))
    initial_transverse = transverses[leg-1]
    initial_hip = hips[leg-1]
    initial_knee = knees[leg-1]

    for i in range(num_of_steps):
        transverse[i], hip[i], knee[i] = inverse_kinematics_3d_v6(
                legspos2joint[leg-1,0] +( x*(i + 1) * (distance / num_of_steps) ), (legspos2joint[leg-1, 1] + (y* (i + 1) * (distance / num_of_steps)) ), legspos2joint[leg-1, 2],
                initial_transverse, initial_hip, initial_knee)
        initial_transverse = transverse[i]
        initial_hip = hip[i]
        initial_knee = knee[i]

    return transverse,hip,knee

def Body_mover(direction,delay,distance):  # moves base with same length as stride

    if direction == 'r':
        sign = -1
        y = 1
        x = 0
    if direction == 'l':
        sign = 1
        y = 1
        x = 0
    if direction == 'f':
        sign = 1
        y = 0
        x = 1
    if direction == 'b':
        sign = -1
        y = 0
        x = 1

    transverses, hips, knees = getjointanglesfromvrep()
    legspos2cg, legspos2joint = GetEndEffectorPos(transverses, hips,knees)  # effector pos with respect to cg got correct angles
    transverse = np.zeros((4, 1))
    hip = np.zeros((4, 1))
    knee = np.zeros((4, 1))
    numofsteps = 100
    initial_transverse = transverses
    initial_hip = hips
    initial_knee = knees

    for i in range(numofsteps):  # moves the base
        for ii in range(4):  # gets required angles for this step-size
            transverse[ii], hip[ii], knee[ii] = inverse_kinematics_3d_v6(
                (legspos2joint[ii,0] - sign*x*(i + 1)*(distance/ numofsteps)), (legspos2joint[ii, 1] - sign*y*(i + 1)*(distance/ numofsteps)), legspos2joint[ii, 2],
                initial_transverse[ii], initial_hip[ii], initial_knee[ii])
        initial_transverse = transverse
        initial_hip = hip
        initial_knee = knee

        for iii in range(4):  # moves the stepsize determined
            v.set_angle((0 + 3 * iii), transverse[iii])
            v.set_angle((1 + 3 * iii), hip[iii])
            v.set_angle((2 + 3 * iii), knee[iii])
            #time.sleep(delay)

        time.sleep(delay)

def move_2_legs(leg1,leg2,direction,distance):
    transverses , hips, knees = getjointanglesfromvrep()
    legspos2cg,legspos2joint=GetEndEffectorPos(transverses,hips,knees)#effector pos with respect to cg got correct angles
    trans1, hip1, knee1, delay = Leg_Ellipse_Trajectory(initalheight, distance,direction, transverses[leg1], hips[leg1], knees[leg1]
                                         ,legspos2joint[leg1,0],legspos2joint[leg1,1])
    trans2, hip2, knee2, delay = Leg_Ellipse_Trajectory(initalheight, distance,direction, transverses[leg2], hips[leg2], knees[leg2]
                                         ,legspos2joint[leg2,0],legspos2joint[leg2,1])
    for i in range(stp):
        v.set_angle((0 + 3 * (leg1)), trans1[i])
        v.set_angle((1 + 3 * (leg1)), hip1[i])
        v.set_angle((2 + 3 * (leg1)), knee1[i])
        v.set_angle((0 + 3 * (leg2)), trans2[i])
        v.set_angle((1 + 3 * (leg2)), hip2[i])
        v.set_angle((2 + 3 * (leg2)), knee2[i])
        time.sleep(delay*2)

def trot2(leg,direction,distance):
    transverses, hips, knees = getjointanglesfromvrep()
    legspos2cg, legspos2joint = GetEndEffectorPos(transverses, hips,knees)

    trans1, hip1, knee1, delay = Leg_Ellipse_Trajectory(initalheight ,distance ,direction , transverses[leg-1], hips[leg-1], knees[leg-1]
                                         ,legspos2joint[leg-1,0],legspos2joint[leg-1,1])
    trans2, hip2, knee2, delay = Leg_Ellipse_Trajectory(initalheight, distance ,direction , transverses[leg+1], hips[leg+1], knees[leg+1]
                                         ,legspos2joint[leg+1,0],legspos2joint[leg+1,1])

    if (leg == 1):
        leg_for_base = [1, 3]
        trans3, hip3, knee3 = generalbasemover_modifed(leg_for_base[0] +1 , direction,distance)
        trans4, hip4, knee4 = generalbasemover_modifed(leg_for_base[1] +1 , direction,distance)
    else:
        leg_for_base = [0, 2]
        trans3, hip3, knee3 = generalbasemover_modifed(leg_for_base[0] +1 , direction,distance)
        trans4, hip4, knee4 = generalbasemover_modifed(leg_for_base[1] +1 , direction,distance)
    numofsteps = stp

    for i in range(numofsteps):
        v.set_angle((0 + 3 * (leg - 1)), trans1[i])
        v.set_angle((1 + 3 * (leg - 1)), hip1[i])
        v.set_angle((2 + 3 * (leg - 1)), knee1[i])
        v.set_angle((0 + 3 * (leg + 1)), trans2[i])
        v.set_angle((1 + 3 * (leg + 1)), hip2[i])
        v.set_angle((2 + 3 * (leg + 1)), knee2[i])
        time.sleep(delay*2)
        v.set_angle((0 + 3 * (leg_for_base[0])), trans3[i])
        v.set_angle((1 + 3 * (leg_for_base[0])), hip3[i])
        v.set_angle((2 + 3 * (leg_for_base[0])), knee3[i])
        v.set_angle((0 + 3 * (leg_for_base[1])), trans4[i])
        v.set_angle((1 + 3 * (leg_for_base[1])), hip4[i])
        v.set_angle((2 + 3 * (leg_for_base[1])), knee4[i])
        time.sleep(delay*8)


def generalbasemover_modifed(leg,direction,distance):  # moves base with same length as stride
    if direction == 'r':
        sign = -1
        y = 1
        x = 0
    if direction == 'l':
        sign = 1
        y = 1
        x = 0
    if direction == 'f':
        sign = 1
        y = 0
        x = 1
    if direction == 'b':
        sign = -1
        y = 0
        x = 1
    transverses, hips, knees = getjointanglesfromvrep()
    legspos2cg, legspos2joint = GetEndEffectorPos(transverses, hips,
                                                  knees)  # effector pos with respect to cg got correct angles 
    numofsteps = stp
    trans = np.zeros((numofsteps, 1))
    hip = np.zeros((numofsteps, 1))
    knee = np.zeros((numofsteps, 1))

    initial_transverse= transverses[leg-1]
    initial_hip = hips[leg-1]
    initial_knee = knees[leg-1]

    for i in range(numofsteps):  # moves the base    
        trans[i], hip[i], knee[i] = inverse_kinematics_3d_v6(
                (legspos2joint[leg-1,0] - sign*x*(i + 1)*(distance/ numofsteps)), (legspos2joint[leg-1, 1] - sign*y*(i + 1)*(distance/ numofsteps)), legspos2joint[leg-1, 2],
                initial_transverse, initial_hip, initial_knee)
        initial_transverse = trans[i]
        initial_hip = hip[i]
        initial_knee = knee[i]

    return trans,hip,knee

def onestepcreeping(direction,distance):
    time.sleep(0.4)
    delay = Move_Leg(1,direction,distance)
    #torquehip, torqueknee, iteration = move_leg(1, 'f')
    time.sleep(0.4)
    delay = Move_Leg(2, direction, distance)
    #torquehip, torqueknee, iteration = move_leg(2, 'f')
    #  gait.plot_torque(torquehip, torqueknee, iteration)
    time.sleep(0.4)
    Body_mover(direction,delay*250,distance)
    time.sleep(0.4)
    delay = Move_Leg(3 ,direction, distance)
    #torquehip, torqueknee, iteration = move_leg(3, 'f')
    #   gait.plot_torque(torquehip, torqueknee, iteration)
    time.sleep(0.4)
    delay = Move_Leg(4, direction, distance)
    #torquehip, torqueknee, iteration = move_leg(4, 'f')

def One_Trot(direction,distance):
    time.sleep(0.5)
    trot2(1,direction,distance)
    time.sleep(0.5)
    trot2(2,direction,distance)


hipinit=-2.01842
kneeinit=0.980479
trinit=0       
   
def asin2(x):
    angle = np.arcsin(x)
    angles=np.zeros((2,1))
    if x >= 0:
        angles[0]=angle
        angles[1]=(np.pi-angle)
        return angles 
    else:
        angles[0]=angle
        angles[1]=-(np.pi) - angle
        return angles
    
def acos2(x):
    angle = np.arccos(x)
    
    if x >= 0:
        return angle , - angle
    else:
        return angle , - angle

def trueangle(two_angles,current_angle):
    diff = np.array((2,1),dtype=np.float)
    diff[0] = abs(current_angle - two_angles[0])
    diff[1] = abs(current_angle - two_angles[1])
    if diff[0] < diff[1]:
        return two_angles[0]
    else:
        return two_angles[1]
    
def plot_torque(hip , knee , iteration):
    
    plt.figure()    
    plt.plot(iteration , hip[0,:],'r')
    plt.plot(iteration , hip[1,:],'b')
    plt.plot(iteration , hip[2,:],'r--')
    plt.plot(iteration , hip[3,:],'b--')

    plt.legend(['leg1 hip' , 'leg2 hip ', 'leg3 hip ', 'leg4 hip '])
    plt.xlabel('trajectory(step)')
    plt.ylabel('Torque(N.m)')
    plt.show()
    
    plt.figure()    
    plt.plot(iteration , knee[0,:],'r')
    plt.plot(iteration , knee[1,:],'b')
    plt.plot(iteration , knee[2,:],'r--')
    plt.plot(iteration , knee[3,:],'b--')

    plt.legend(['leg1 knee' , 'leg2 knee ', 'leg3 knee ', 'leg4 knee '])
    plt.xlabel('trajectory(step)')
    plt.ylabel('Torque(N.m)')
    plt.show()

def inverse_kinematics_3d_v6(px,py,pz,ptran,phip,pknee):
    two_angles = np.array((2, 1))
    u = np.sqrt((- a**2 + py**2 + pz**2))
    x = 2*np.arctan((pz - u)/(a + py))
    y = 2*np.arctan((pz + u)/(a + py))

    if np.abs(x-ptran) < np.abs(y-ptran):
        theta1 = x
    else:
        theta1 = y

    r = px**2 + py**2 + pz**2
    ratio = ((r - a**2 - l1**2 - l2**2) / (2*l1*l2))
    two_angles = acos2(ratio)
    theta3 = trueangle(two_angles, pknee)

    N = l2*cos(theta3) + l1
    num = px*N - l2*sin(theta1)*sin(theta3)*py + l2*sin(theta3)*cos(theta1)*pz
    den = l2*N*cos(theta3) + l1*N + (l2**2 * (sin(theta3))**2)
    ratio = num/den
    two_angles = acos2(ratio)
    theta2 = trueangle(two_angles, phip)
    return theta1,theta2,theta3


def forward_kinematics_V2( theta1 , theta2 , theta3):
    t = theta2 + theta3
    px = np.cos(theta1)*(l2*np.cos(t) + l1*np.cos(theta2)) + a*np.sin(theta1)
    py = np.sin(theta1)*(l2*np.cos(t) + l1*np.cos(theta2)) - a*np.cos(theta1)
    pz = l2*np.sin(t) + l1*np.sin(theta2)
    return px,py,pz


def forward_kinematics_V3( theta1 , theta2 , theta3):
    t = theta2 + theta3
    pz = cos(theta1)*(l2*sin(t) + l1*sin(theta2)) + a*sin(theta1)
    py = -sin(theta1)*(l2*sin(t) + l1*sin(theta2)) + a*cos(theta1)
    px = l2*np.cos(t) + l1*np.cos(theta2)
    return px,py,pz


l1 =244.59
l2 =208.4
mis = 0
hip = np.zeros((33**3 ,2))
tran = np.zeros((33**3 ,2))
knee = np.zeros((33**3 ,2))
iteration = 0
# for i in range(31):
#     for j in range(31):
#         for k in range(31):
#             x, y, z = forward_kinematics_V3(i/10, j/10, k/10)
#             l, m, n = inverse_kinematics_3d_v6(x, y, z, i/10 -0.001, j/10 -0.001, k/10 -0.001)
#             if (np.abs(l-(i/10)) > 0.01) or (np.abs(m-(j/10)) > 0.01) or (np.abs(n-(k/10)) > 0.01):
#
#                 tran[iteration, 0] = i / 10
#                 hip[iteration, 0] = j / 10
#                 knee[iteration, 0] = k / 10
#                 tran[iteration, 1] = l
#                 hip[iteration, 1] = m
#                 knee[iteration, 1] = n
#                 iteration = iteration + 1
#

# x,y,z = forward_kinematics_V2(0,1,1.3)
q,w,r= inverse_kinematics_3d_v6(0,a,-initalheight,0,-0.99,1.29)
# x = 120
# y = 50
# z = 100


#y = inverse_kinematics(5,200,0.1,0.1)
print("finish")