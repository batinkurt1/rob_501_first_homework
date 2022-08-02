#!/usr/bin/env python

import rospy

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from ros_hw.srv import *

from math import atan2,sqrt,pow,isclose
from time import time

home=None
position=None
origin=Pose()
origin.x,origin.y=0,0

paramset={"distance":None,"delta":None,"max_linear_velocity":None,"max_angular_velocity":None}

params=["/distance","/delta","/max_linear_velocity","/max_angular_velocity"]
default_params=[0.1,0.001,2.0,1.0]
rotation=Twist()
translation=Twist()
check=True
def callback(data):
    global position
    global home
    global check
    if check:
        home=data
        check=False
    position=data

#def

#get the waypoints, check if you reached it, get it again, when finished (when the navigation output is [0,0,0]) go home. create the launch file. you're done
def waypoint_client():
    rospy.wait_for_service("navigation")
    try:
        waypoint_serv=rospy.ServiceProxy("navigation",nextgoal)
        waypoint=waypoint_serv()
        return waypoint
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)


    
def controller():
    global position
    global rotation
    global translation
    global home
    pub = rospy.Publisher('/turtlesim1/turtle1/cmd_vel', Twist, queue_size=10,)
    rospy.Subscriber("/turtlesim1/turtle1/pose",Pose,callback)
    rospy.init_node("controller",anonymous=True)
    rate = rospy.Rate(10)

    for i in range(len(params)):
        if not rospy.has_param(params[i]): 
            rospy.set_param(params[i],default_params[i])

    for key in paramset.keys():
        paramset[key]=rospy.get_param(f"/{key}")
    
    #rotation.angular.z=paramset["max_angular_velocity"] #proportionality constants
    #translation.linear.x=paramset["max_linear_velocity"] #proportionality constants
    #get the first waypoint
    waypoint=waypoint_client()
    waypoint=waypoint.nextwaypoint
    while waypoint!=(0.0,0.0,0.0,0.0):
        rospy.loginfo(waypoint)
        waypoint_pose=Pose()
        waypoint_pose.x, waypoint_pose.y=waypoint[0],waypoint[1]
        #takılma sorunu bundan olabilir
        #while not position:
            #pass
        heading=heading_angle_calc(position,waypoint_pose)
        #control max
        #stime=time()
        while not isclose(position.theta,heading,rel_tol=paramset["delta"]):
            rotation.angular.z=min(angular_vel(position,waypoint_pose),paramset["max_angular_velocity"])
            #rotation.angular.z=angular_vel(position,waypoint_pose)
            #if rotation.angular.z>paramset["max_angular_velocity"]:
                #rotation.angular.z=paramset["max_angular_velocity"]
            #rospy.loginfo(rotation.angular.z)
            pub.publish(rotation)
            #if (time()-stime)>10:
                #break
            
        dist=distance_calc(position,waypoint_pose)
        while dist>=paramset["distance"]:
            translation.linear.x=min(linear_vel(position,waypoint_pose),paramset["max_linear_velocity"])
            #translation.linear.x=linear_vel(position,waypoint_pose)
            #if translation.linear.x>paramset["max_linear_velocity"]:
                #translation.linear.x=paramset["max_linear_velocity"]
            pub.publish(translation)
            dist=distance_calc(position,waypoint_pose)
        waypoint=waypoint_client()
        waypoint=waypoint.nextwaypoint
    

    heading=heading_angle_calc(position,home)
    #cw_ccw_adjustor(heading,position)

    while not isclose(position.theta,heading,rel_tol=paramset["delta"]):
        #rotation.angular.z=angular_vel(position,waypoint_pose)
        #if rotation.angular.z>paramset["max_angular_velocity"]:
            #rotation.angular.z=paramset["max_angular_velocity"]
        rotation.angular.z=min(angular_vel(position,home),paramset["max_angular_velocity"])
        pub.publish(rotation)
    dist=distance_calc(position,home)
    while dist>=paramset["distance"]:
        #translation.linear.x=linear_vel(position,waypoint_pose)
        #if translation.linear.x>paramset["max_linear_velocity"]:
            #translation.linear.x=paramset["max_linear_velocity"]
        translation.linear.x=min(linear_vel(position,home),paramset["max_linear_velocity"])
        pub.publish(translation)
        dist=distance_calc(position,home)


    #while not rospy.is_shutdown():
        #rate.sleep()
        


    
    

    #rospy.spin()

def distance_calc(position,goal):
    return sqrt(pow((position.x-goal.x),2)+pow((position.y-goal.y),2))

def heading_angle_calc(position,goal):
    return atan2(goal.y-position.y,goal.x-position.x)

"""def cw_ccw_adjustor(heading,position):
    global rotation
    if heading>0 and position.theta>=0 and (heading-position.theta)<0:
        rotation.angular.z*=-1
    if heading<0 and position.theta<=0 and (heading-position.theta)<0:
        rotation.angular.z*=-1
    if heading<0 and position.theta>=0 and abs(heading-position.theta)<3:
        rotation.angular.z*=-1
    if heading>0 and position.theta<=0 and (heading-position.theta)>3:
        rotation.angular.z*=-1"""

def angular_vel(position,goal, p=3):
    return p * (heading_angle_calc(position,goal) - position.theta)

def linear_vel( position,goal, p=1.5):
    return p * distance_calc(position,goal)


if __name__ == '__main__':
    try:
        controller()
    except rospy.ROSInterruptException:
        pass




#max ayarla, cw ccw düzelt, home düzelt, bazen p controller aşıyo, çok hızlı dönüyor düzelt

#rospy.loginfo sor