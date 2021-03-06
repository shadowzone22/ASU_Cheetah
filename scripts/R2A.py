#!/usr/bin/env python3
import rospy
import time
import GP2_Vrep_V3 as v
import numpy as np
import threading
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import String
testing=False
params=0
inits=0
pub=0
sub=0
if __name__ == "__main__":
	if not testing :
		#v.vrepInterface(19999)
		print('NOT TEST')
	ros_init()
	set_angle('cd1',0.0)
	# print('should be set')
	#v.set_angle('cd1',0)


def callback(data):
	#loginfo(rospy.get_caller_id() + "I heard %s", data.data)
	#print('info is'+data.data)
	global params
	params=data.data
	


def ros_init(node=0):
	
	global pub
	global pub2
	global sub
	rospy.Subscriber('getter',Float32MultiArray,callback)
	rospy.Subscriber("init",Float32MultiArray,get_inits_toR2A)
	pub = rospy.Publisher('setter', String, queue_size=10)
	pub2 = rospy.Publisher('ik_setter', Float32MultiArray, queue_size=10)
	time.sleep(2)
	if node==0:
		rospy.init_node('algorithm', anonymous=True)
	time.sleep(2)
	print('Started')
def get_inits_toR2A(data):
	inits=data.data
def get_inits():
	return inits
def get_angles(pos):
	global params
	if pos=='ab3' or pos==0 :
		ang=params[0]
	if pos=='bc3' or pos==1 :
		ang=params[1]
	if pos=='cd3' or pos==2 :
		ang=params[2]
	if pos=='ab4' or pos==3 :
		ang=params[3]
	if pos=='bc4' or pos==4 :
		ang=params[4]
	if pos=='cd4' or pos==5 :
		ang=params[5]
	if pos=='ab1' or pos==6 :
		ang=params[6]
	if pos=='bc1' or pos==7 :
		ang=params[7]
	if pos=='cd1' or pos==8 :
		ang=params[8]
	if pos=='ab2' or pos==9 :
		ang=params[9]
	if pos=='bc2' or pos==10 :
		ang=params[10]
	if pos=='cd2' or pos==11 :
		ang=params[11]
	return ang


def get_torques(pos):
	global params
	if pos=='ab3' or pos==0 :
		trq=params[12]
	if pos=='bc3' or pos==1 :
		trq=params[13]
	if pos=='cd3' or pos==2 :
		trq=params[14]
	if pos=='ab4' or pos==3 :
		trq=params[15]
	if pos=='bc4' or pos==4 :
		trq=params[16]
	if pos=='cd4' or pos==5 :
		trq=params[17]
	if pos=='ab1' or pos==6 :
		trq=params[18]
	if pos=='bc1' or pos==7 :
		trq=params[19]
	if pos=='cd1' or pos==8 :
		trq=params[20]
	if pos=='ab2' or pos==9 :
		trq=params[21]
	if pos=='bc2' or pos==10 :
		trq=params[22]
	if pos=='cd2' or pos==11 :
		trq=params[23]
	return trq
def send_ik_point(x,y,z,leg):
	total = Float32MultiArray()
	total.data = []
	arr=[x,y,z,leg]
	total.data=arr
	pub2.publish(total)


def set_angle(joint,angle):
	#msg=str(joint)+' '+str(angle)
	sendangle=float(angle)#cause sometimes it came in shape of a single list 
	msg=str(joint)+' '+str(sendangle)
	pub.publish(msg)

def desired_xy(transverse,hip,knee,legno):
	from Main_Functions import GP2_Function_V7 as gait1
	msg = Float32MultiArray()
	x,y,z = gait1.forward_kinematics_V3(transverse,hip,knee)
	msg.data=[float(x),float(z),legno]
	pub2 = rospy.Publisher('desired',Float32MultiArray)
	pub2.publish(msg)