import rospy
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class Drone:
    def __init__(self) -> None:
        rospy.init_node('drone', anonymous=True)
        
        self.sub_thunderstorm = rospy.Subscriber('/zhihang/thunderstorm', Pose, self.callback_storm)
        self.sub_local_position = rospy.Subscriber('/gazebo/zhihang/standard_vtol/local_position', Pose, self.callback_vtol)
        self.sub_pose = rospy.Subscriber('/standard_vtol_0/mavros/local_position/pose', PoseStamped, self.callback_pose)
        self.sub_state = rospy.Subscriber('/standard_vtol_0/mavros/state', String, self.callback_state)
        self.sub_angle = rospy.Subscriber('/zhihang/standard_vtol/angel', Pose, self.callback_angle)
        self.sub_cmd_vel_flu = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd_vel_flu', Twist, self.callback_cmd_vel_flu)
        self.sub_cmd_pose_enu = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd_pose_enu', Pose, self.callback_cmd_pose_enu)
        self.sub_cmd = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd', String, self.callback_cmd)
        
        #无人机相机话题
        
        
        self.data = {
        "thunderstorm": None,
        "local_position": None,
        "pose": None,
        "state": None,
        "angel": None,
        "cmd_vel_flu": None,
        "cmd_pose_enu": None,
        "cmd": None,
    }
    
    def callback_thunderstorm(self, data):
        self.data['thunderstorm'] = data

    def callback_local_position(self, data):
        self.data['local_position'] = data
        
    def callback_pose(self, data):
        self.data['pose'] = data
        
    def callback_state(self, data):
        self.data['state'] = data
        
    def callback_angle(self, data):
        self.data['angel'] = data
        
    def callback_cmd_vel_flu(self, data):
        self.data['cmd_vel_flu'] = data
        
    def callback_cmd_pose_enu(self, data):
        self.data['cmd_pose_enu'] = data
    
    def callback_cmd(self, data):
        self.data['cmd'] = data
        
    

   
    
    def Test(self):
        print("VTOL: ", self.vtol_data)
        print("Storm: ", self.storm_data)


    

    cmd = String()
    twist = Twist()
    

if __name__ == '__main__':
    drone = Drone()
    rospy.spin()
    
    

    
    