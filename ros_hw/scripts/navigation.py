#!/usr/bin/env python


import rospy

from ros_hw.srv import nextgoal,nextgoalResponse
i=-1
list_of_points=None
def handle_waypoint(a):
    global i
    i+=1
    if i>=len(list_of_points):
        return nextgoalResponse([0,0,0,0])
    else:
        return nextgoalResponse(list_of_points[i])


def navigation():
    global list_of_points
    while not rospy.has_param("/waypoints"):
        pass
    list_of_points=rospy.get_param("/waypoints")
    rospy.init_node('navigation', anonymous=True)
    s = rospy.Service('navigation', nextgoal, handle_waypoint)
    print("Ready to submit the next waypoint")
    rospy.spin()




if __name__ == '__main__':
    try:
        navigation()
    except rospy.ROSInterruptException:
        pass
