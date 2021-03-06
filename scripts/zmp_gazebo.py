#!/usr/bin/env python

import rospy
import numpy as np
import sympy as sp
import math
from numpy import sin , cos
# import torch
import scipy.linalg
from sympy.solvers import solve
from sympy import Symbol, Eq
#from sympy.solvers.solveset import linsolve
from timeit import default_timer as time
import time
from std_msgs.msg import String
from std_msgs.msg import Float32MultiArray
from Main_Functions import GP2_Function_V7 as gait

# Constants
g = 9.81
Mx = 2
My = 3
Mz = 5
Fx = 8
Fy = 12
Fz = 9
hipOffset = 300.78
mass = 20
z = 0
var =0
var2 = 0
var3 =0
var4 = 0
delay_seq = 0.1
#inert = 

global pub
global leg_pos3_hip
global leg_pos4_hip
global leg_pos1_hip
global leg_pos2_hip
global leg_pos3_cg
global leg_pos4_cg
global leg_pos1_cg
global leg_pos2_cg
global leg3_ang
global leg4_ang        
global leg1_ang
global leg2_ang

# Parameters:
l1 =245
l2 =208.4
a=gait.a
initial_leg_height = 390 # from ground to joint   320
stride = 150
ct=0.5
h = 15    # maximum height of trajectory
cycle_time =ct  # total time for each cycle
steps = 100 # number of steps 'even'
initial_distance = 0 # along x

x_fixed = np.zeros([steps, 1], dtype=float)
y_fixed = np.zeros([steps, 1], dtype=float)



initial_leg_height_f = initial_leg_height
stride_f = 150
h_f = 100
cycle_time_f = ct
initial_distance_f = None
sample_time_f = None
pub = 0
indx_fix = 0
linear_acc_threshold = 20 
angular_acc_threshold = 20


#initial position relative to hip and cg
leg1_initial_hip=np.zeros([3, 1], dtype=float)
leg2_initial_hip=np.zeros([3, 1], dtype=float)
leg3_initial_hip=np.zeros([3, 1], dtype=float)
leg4_initial_hip=np.zeros([3, 1], dtype=float)

leg1_initial_cg=np.zeros([3, 1], dtype=float)
leg2_initial_cg=np.zeros([3, 1], dtype=float)
leg3_initial_cg=np.zeros([3, 1], dtype=float)
leg4_initial_cg=np.zeros([3, 1], dtype=float)

#Subscribed data
lin_acc=np.zeros([3, 1], dtype=float)
Ang_acc=np.zeros([3, 1], dtype=float)
lin_acc_prev=np.zeros([3, 1], dtype=float)
Ang_acc_prev=np.zeros([3, 1], dtype=float)


leg_pos3_hip=np.zeros([3, 1], dtype=float) 
leg_pos4_hip=np.zeros([3, 1], dtype=float)
leg_pos1_hip=np.zeros([3, 1], dtype=float)
leg_pos2_hip=np.zeros([3, 1], dtype=float) 

leg_pos3_cg=np.zeros([3, 1], dtype=float) 
leg_pos4_cg=np.zeros([3, 1], dtype=float)
leg_pos1_cg=np.zeros([3, 1], dtype=float)
leg_pos2_cg=np.zeros([3, 1], dtype=float)

leg3_ang=np.zeros([3, 1], dtype=float)                  #trans hip knee
leg4_ang=np.zeros([3, 1], dtype=float)
leg1_ang=np.zeros([3, 1], dtype=float)
leg2_ang=np.zeros([3, 1], dtype=float)
legfix_Prev_angs = np.zeros([3, 1], dtype=float)
legvar_Prev_angs = np.zeros([3, 1], dtype=float)


########################################################################################################

def imudata(data):
    Array = np.array(data.data)
    global lin_acc
    global Ang_acc
    global lin_acc_prev
    global Ang_acc_prev
    global linear_acc_threshold
    global angular_acc_threshold
    global leg3_ang                   #trans hip knee
    global leg4_ang
    global leg1_ang
    global leg2_ang
    global z        

    
    linear_acc_threshold = 10
    angular_acc_threshold = 10
    
    lin_acc_prev=lin_acc    ######save previous imu readings
    Ang_acc_prev=Ang_acc
    
    lin_acc = Array[36:39]  ######get new readings
    Ang_acc = Array[39:42]

    leg3_ang = Array[0:3] 
    leg4_ang = Array[3:6]
    leg1_ang = Array[6:9]
    leg2_ang = Array[9:12]    
  
    # for i in range (3):   ###### thresholding  between previous and new readings
    #     if ((np.absolute(lin_acc[i]-lin_acc_prev[i]))>linear_acc_threshold) or ((np.absolute(Ang_acc[i]-Ang_acc_prev[i]))> angular_acc_threshold):
    #         z = 1 
    #     else:
    #         z = 0


#########################################################################################################

def leg_pos(data):
    Array2 = np.array(data.data)

    global leg_pos3_hip
    global leg_pos4_hip
    global leg_pos1_hip
    global leg_pos2_hip
    global leg_pos3_cg
    global leg_pos4_cg
    global leg_pos1_cg
    global leg_pos2_cg

    leg_pos3_hip =Array2[0:3] 
    leg_pos4_hip =Array2[3:6] 
    leg_pos1_hip =Array2[6:9] 
    leg_pos2_hip =Array2[9:12] 

    leg_pos3__cg =Array2[12:15] 
    leg_pos4__cg =Array2[15:18] 
    leg_pos1__cg =Array2[18:21] 
    leg_pos2__cg =Array2[21:24]
	


##########################################################################################################

# Functions:

def Get_ZMP():
    global mass
    Pc = [0, 0, 0]  # Position of Com relative to origin(cg)
    G = [0, 0, -g]  # Gravity
    #Fi=[Fx,Fy,Fz]                  #Inertia Force from IMU
    Fi = lin_acc * mass
    #Mi = [Mx, My, Mz]              #Inertia Moment
   # Mi = Ang_acc * inert
    Zval = 10  # this will be Z of endeffector from origin which is = Zzmp
    Xzmp, Yzmp, Zzmp = sp.symbols("Xzmp,Yzmp,Zzmp")
    Pzmp = np.array([Xzmp, Yzmp, Zzmp])  # Position of Zmp relative to origin

    A = np.cross(np.subtract(Pc, Pzmp), Fi)
    B = np.cross((np.subtract(Pc, Pzmp)), G)
    F = A + B 
    eq1 = Eq(F[0])
    eq1 = eq1.subs(Zzmp, Zval)
    eq2 = Eq(F[1])
    eq2 = eq2.subs(Zzmp, Zval)
    eq3 = Eq(F[2])
    eq3 = eq3.subs(Zzmp, Zval)
    sol = solve((eq1, eq2, eq3), (Xzmp, Yzmp, Zzmp))

    return sol[Xzmp], sol[Yzmp], Zval


def Mod_contact(leg_no, leg_pos1, leg_pos2_y):

    hipoffset = 300.78
    # leg_pos1 is Position of one leg relative to origin(cg)
    Pzmp = Get_ZMP()
    # Pzmp=[4,5]
    m = (Pzmp[1] - leg_pos1[1]) / (Pzmp[0] - leg_pos1[0])  # Slope of needed line
    # Solve eq y-y1=m(x-x1) with y=cons from the other leg(leg_pos2)
    X_leg = (leg_pos2_y[1] - leg_pos1[1] + m * leg_pos1[0]) / m
    if leg_no==3 or leg_no==4:
    	X_leg = X_leg - hipoffset
    elif leg_no==1 or leg_no==2: #check axisss
    	X_leg = hipoffset- X_leg

    print(X_leg)
    return X_leg 



def Gate_Publisher(leg_no,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,st):

    # Parameters:
    global l1
    global l2
    global initial_leg_height
    global initial_leg_height_f
    global stride
    global stride_f
    global h
    global h_f
    global cycle_time
    global cycle_time_f
    global steps
    global initial_distance
    global initial_distance_f
    global z
    global sample_time_f

    global leg_pos3_hip
    global leg_pos4_hip
    global leg_pos1_hip
    global leg_pos2_hip

    global x_fixed
    global y_fixed
    global var 
    global var2
    global var3 
    global var4    

    flag_start =0
    x_current = 0 
    y_current = 0
    x_current_f =0
    global indx_fix
    t_left = 0
    current = 0
    last_fix = 0
    sample_time = np.float(cycle_time) / steps # sample time
    sample_time_f =np.float(cycle_time_f) / steps   # sample time
    stride= st
    stride_f=st

    z=0

    if leg_no == 4 or leg_no == 3:    

        xnew = np.zeros([steps, 1], dtype=float)
        t = 0
        i = 0
        if leg_no == 4:
            initial_distance_f = leg_pos4_hip[0]
        else:
            initial_distance_f = leg_pos3_hip[0]

        for t in np.arange(0, cycle_time_f, sample_time_f):
            xnew[i] = (stride_f * ((t / cycle_time_f) - ((1 / (2 * np.pi)) * np.sin(2 * np.pi * (t / cycle_time_f)))) - (stride_f / 2) + stride_f / 2) + initial_distance_f
            i = i + 1
        xnew = xnew
 
        i = 0
        ynew = np.zeros([steps, 1], dtype=float)

        # First part of Ynew in piecewise
        for t in np.arange(0, cycle_time_f / 2, sample_time_f):
            ynew[i] = (-(h_f / (2 * np.pi)) * np.sin(((4 * np.pi) / cycle_time_f) * t) + ((2 * h_f * t) / cycle_time_f) - (h_f / 2)) + (h_f / 2) - initial_leg_height_f
            i = i + 1

        n = (cycle_time_f / 2)
        for t in np.arange(n, cycle_time_f, sample_time_f):
            ynew[i] = (-(h_f / (2 * np.pi)) * np.sin(4 * np.pi - (((4 * np.pi) / cycle_time_f) * t)) - ((2 * h_f * t) / cycle_time_f) + ((3 * h_f) / 2)) + (h_f / 2) - initial_leg_height_f
            i = i + 1
        ynew = ynew

        x_fixed = xnew
        y_fixed = ynew

    elif leg_no == 2 or leg_no == 1:
     
        xnew = np.zeros([steps, 1], dtype=float)
        ynew = np.zeros([steps, 1], dtype=float)
        t = 0
        i = 0
        if leg_no == 2:
            initial_distance = leg_pos2_hip[0]
        else:
            initial_distance = leg_pos1_hip[0]

        if leg_no == 2:
            var = 1
            var2 = 3
            var3 = 1 
            var4 = 3
        else:
            var = 0
            var2 = 2
            var3 = 2 
            var4 = 4            


        while(1):

            current = time.time()   #absolute
            if leg_no == 2:
                legfix_Prev_angs = leg4_ang
                #print(legfix_Prev_angs)
                legvar_Prev_angs = leg2_ang
                #print(legvar_Prev_angs)
            else:
                legfix_Prev_angs = leg3_ang
                legvar_Prev_angs = leg1_ang

            if ((current - last_fix) > sample_time_f ) and i < steps:        
                last_fix = current
                xnew[i] = (stride * ((t / cycle_time) - ((1 / (2 * np.pi)) * np.sin(2 * np.pi * (t / cycle_time)))) - (stride / 2) + stride / 2) + initial_distance
                
                if t < (cycle_time / 2):

                    ynew[i] = (-(h / (2 * np.pi)) * np.sin(((4 * np.pi) / cycle_time) * t) + ((2 * h * t) / cycle_time) - (h / 2)) + (h / 2) - initial_leg_height

                else:
                    ynew[i] = (-(h / (2 * np.pi)) * np.sin(4 * np.pi - (((4 * np.pi) / cycle_time) * t)) - ((2 * h * t) / cycle_time) + ((3 * h) / 2)) + (h / 2) - initial_leg_height


                trans,hip,knee = gait.inverse_kinematics_3d_v6(x_fixed[i], 112.75, y_fixed[i],0 ,legfix_Prev_angs[1], legfix_Prev_angs[2] )
                trans0,hip0,knee0 = gait.inverse_kinematics_3d_v6(xnew[i], 112.75, ynew[i],0 ,legvar_Prev_angs[1], legvar_Prev_angs[2])                 
                #Publish Fixed leg point                
                set_angle((var*3),trans)
                set_angle((var*3)+1 , hip)
                set_angle(((var*3)+2), knee)       
                #Publish Variable leg point
                set_angle((var2*3),trans0)
                set_angle((var2*3)+1 , hip0)
                set_angle((var2*3)+2, knee0)
                if flag_start == 0:
                    trans3,hip3,knee3 = gait.generalbasemover_modifed(var3, 'f',st ,steps)
                    trans1,hip1,knee1 = gait.generalbasemover_modifed(var4, 'f',st ,steps)
                    flag_start = 1
                # Move Body                                    
                set_angle(((var3-1)*3),trans3[i])
                set_angle(((var3-1)*3)+1 , hip3[i])
                set_angle((((var3-1)*3)+2), knee3[i])         
                set_angle(((var4-1)*3),trans1[i])
                set_angle(((var4-1)*3)+1 , hip1[i])
                set_angle((((var4-1)*3)+2), knee1[i])
                if(z == 1):
                    x_current = xnew[i]
                    y_current = ynew[i]
                    #x_current_f = x_fixed[i]
                    t_left = cycle_time_f - t
                    indx_fix = i+1
                    break
                i = i + 1
                t = t + sample_time_f
            if (i == steps):
                flag_start =0
                break               

        if z == 1:
            #x_moved = legfix_initial_hip[0] - x_current_f
            #t_elabsed = (x_moved/stride_f) * cycle_time_f
            cycletime_required = t_left * 2
            legfix_final_cg = np.zeros([2, 1], dtype=float)
            legvar_final_cg = np.zeros([2, 1], dtype=float)           
            legfix_final_cg[0] = legfix_initial_cg[0] + stride_f     # this is coord of the pt at end of traj for fixed leg
            legfix_final_cg[1] = legfix_initial_cg[1]                # Must be relative to cg
            legvar_final_cg[1] = legvar_initial_cg[1]
            x_target = Mod_contact(leg_no, legfix_final_cg ,legvar_final_cg)    
            trajectory_modification(x_current, y_current, x_target, cycletime_required,legfix_Prev_angs,legvar_Prev_angs)
            indx_fix = 0
            #stride = stride_mod
            #h = h_mod
            #cycle_time = cycle_time_mod
            #initial_distance = initial_distance_mod       #######################
            #xpub, ypub = trajectory_moved(x_mod, y_mod)
            #initial_distance=0                            #######################




def trajectory_modification(x_current, y_current, x_target, cycle_time,legfix_Prev_angs,legvar_Prev_angs):

    global l1
    global l2
    global steps
    global initial_leg_height
    global var
    global var2
    global var3
    global var4

    global indx_fix
    global x_fixed
    global y_fixed

    stride = (x_target - x_current) * 2
    h = y_current  # maximum height of the trajectory
    x_initial = x_target - stride
    initial_distance = x_initial
    sample_time = cycle_time / steps  # sample time, steps should be even

    xnew = np.zeros([steps/2, 1], dtype=float)
    ynew = np.zeros([steps/2, 1], dtype=float)
    t = 0
    i = 0
    #i_f= steps/2
    n = (cycle_time / 2)
    current = 0
    last_fix = 0
    last_var = 0


    while(1):

        current = time.time()   #absolute

        if ((current - last_fix) > sample_time_f ) and indx_fix < steps :        #Publish Fixed leg point
            last_fix = current
            trans,hip,knee = gait.inverse_kinematics_3d_v6(x_fixed[indx_fix], 112.75, y_fixed[indx_fix],0 ,legfix_Prev_angs[1], legfix_Prev_angs[2] )
            set_angle((var*3),trans )
            set_angle((var*3)+1 , hip)
            set_angle(((var*3)+2), knee)


            #rospy.loginfo(x_fixed[indx_fix])        
            #pub.publish(x_fixed[indx_fix])          
            #rospy.loginfo(y_fixed[indx_fix])
            #pub.publish(y_fixed[indx_fix])

            indx_fix = indx_fix + 1

        if ((current - last_var) > sample_time ) and i < steps/2 :               #Publish Variable leg point
            last_var = current
            xnew[i] = (stride * ((t / cycle_time) - ((1 / (2 * np.pi)) * np.sin(2 * np.pi * (t / cycle_time)))) - (stride / 2) + stride / 2) + initial_distance
            ynew[i] = (-(h / (2 * np.pi)) * np.sin(4 * np.pi - (((4 * np.pi) / cycle_time) * t)) - ((2 * h * t) / cycle_time) + ((3 * h) / 2)) + (h / 2) - initial_leg_height            
            trans,hip,knee = gait.inverse_kinematics_3d_v6(xnew[i], 112.75, ynew[i],0 ,legvar_Prev_angs[1], legvar_Prev_angs[2])    

            set_angle((var2*3),trans )
            set_angle((var2*3)+1 , hip)
            set_angle(((var2*3)+2), knee)



            #rospy.loginfo(xnew[i])                 
            #pub.publish(xnew[i])          
            #rospy.loginfo(ynew[i])
            #pub.publish(ynew[i])
            i = i + 1
            t = t + sample_time

        if (indx_fix == steps) and i == steps/2:
            #print("done")
            break
          
    #return xnew, ynew, stride, h, cycle_time, initial_distance

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

def set_angle(joint, angle):
    global pub
    msg=str(joint) + ' ' + str(angle)
    sendangle = float(angle)
    msg = str(joint)+ ' ' + str(sendangle)
    pub.publish(msg)

#####################################################################################################################
# Main
if __name__ == '__main__':
    rospy.init_node('talker', anonymous=True)
    pub = rospy.Publisher('setter', String, queue_size=10)
    gait.ros.ros_init(1)
    rospy.Subscriber('fwd', Float32MultiArray, leg_pos)
    rospy.Subscriber('getter', Float32MultiArray , imudata)
    time.sleep(2)
    rate = rospy.Rate(100)  # 10hz 
    first_step_flag=1
    while not rospy.is_shutdown():
        
        if first_step_flag == 1:
            legfix_initial_hip = leg_pos4_hip[0]
            legvar_initial_hip = leg_pos2_hip[0]
            legfix_initial_cg = leg_pos4_cg
            legvar_initial_cg = leg_pos2_cg


            time.sleep(delay_seq)        
            Gate_Publisher(4 ,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,150)
            Gate_Publisher(2 ,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,150)     

            legfix_initial_hip = leg_pos3_hip[0]
            legvar_initial_hip = leg_pos1_hip[0]
            legfix_initial_cg = leg_pos3_cg
            legvar_initial_cg = leg_pos1_cg

            time.sleep(delay_seq)         

            Gate_Publisher(3 ,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,300)
            Gate_Publisher(1 ,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,300)  
            first_step_flag=0    
        
        else:
            legfix_initial_hip = leg_pos4_hip[0]
            legvar_initial_hip = leg_pos2_hip[0]
            legfix_initial_cg = leg_pos4_cg
            legvar_initial_cg = leg_pos2_cg


            time.sleep(delay_seq)        
            Gate_Publisher(4 ,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,300)
            Gate_Publisher(2 ,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,300)     

            legfix_initial_hip = leg_pos3_hip[0]
            legvar_initial_hip = leg_pos1_hip[0]
            legfix_initial_cg = leg_pos3_cg
            legvar_initial_cg = leg_pos1_cg

            time.sleep(delay_seq)         

            Gate_Publisher(3 ,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,300)
            Gate_Publisher(1 ,legfix_initial_hip,legvar_initial_hip,legfix_initial_cg,legvar_initial_cg,300)   

            

        #rate.sleep()        