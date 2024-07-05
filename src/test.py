import rospy
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from mavros_msgs.msg import State

from enum import Enum

class TASK(Enum):
    INIT    = 0    #初始状态
    TAKEOFF = 1    #起飞并切换至固定翼模式
    TRACK   = 2    #以固定翼模式飞至引导点，中途躲避雷暴区域
    SEARCH  = 3    #在引导点附近搜寻目标
    LAND    = 4    #切换至旋翼模式并降落到目标上

#部分Subscriber参见XTDrone/communication/vtol_communication.py
#无人机控制方法参见XTDrone/keyboard/vtol_keyboard_control.py
class Drone:
    def __init__(self) -> None:
        rospy.init_node('drone', anonymous=True)
        
        #------------------------------------Publishers------------------------------------#
        self.cmd_pose_enu_pub = rospy.Publisher('/xtdrone/standard_vtol_0/cmd_pose_enu', Pose, queue_size=1)
        self.cmd_vel_flu_pub = rospy.Publisher('/xtdrone/standard_vtol_0/cmd_vel_flu', Twist, queue_size=1)
        self.cmd_pub = rospy.Publisher('/xtdrone/standard_vtol_0/cmd', String, queue_size=1)
        
        '''
        self.arrive_pub
        self.ship_pub
        '''
        #----------------------------------------------------------------------------------#
        
        
        #------------------------------------Subscribers------------------------------------#
        #雷暴中心点位置（随机，z的值是零，只能绕过，半径1000米）
        self.sub_thunderstorm = rospy.Subscriber('/zhihang/thunderstorm', Pose, self.callback_thunderstorm)
        #无人机位置（相对于仿真环境中的地面坐标系）
        self.sub_local_position = rospy.Subscriber('/gazebo/zhihang/standard_vtol/local_position', Pose, self.callback_local_position)
        #带时间戳的位置信息
        self.sub_pose = rospy.Subscriber('/standard_vtol_0/mavros/local_position/pose', PoseStamped, self.callback_pose)
        
        self.sub_state = rospy.Subscriber('/standard_vtol_0/mavros/state', State, self.callback_state)
        #无人机偏航角（无人机位置向量与目标位置向量的夹角）
        self.sub_angle = rospy.Subscriber('/zhihang/standard_vtol/angel', Pose, self.callback_angle)
        #flu坐标系：Foward（前进方向）, Left（左侧方向）, Up（上方）
        #flu坐标系下的无人机速度（Twist用于描述物体的运动状态，包括线速度和角速度）
        self.sub_cmd_vel_flu = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd_vel_flu', Twist, self.callback_cmd_vel_flu)
        #enu坐标系：East（东方）, North（北方）, Up（上方）
        #enu坐标系下的无人机位置（Pose用于描述物体在空间中的位置和方向）
        self.sub_cmd_pose_enu = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd_pose_enu', Pose, self.callback_cmd_pose_enu)
        #飞机状态，是否上锁，旋翼模式or固定翼模式等
        self.sub_cmd = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd', String, self.callback_cmd)
        
        #无人机相机话题
        #--TODO--#
        
        #-----------------------------------------------------------------------------------#
        
        #相关话题信息
        self.m_data = {
        "thunderstorm": None,
        "local_position": None,
        "pose": None,
        "state": None,
        "angel": None,
        "cmd_vel_flu": None,
        "cmd_pose_enu": None,
        "cmd": None,
        }
        
        self.m_state = State()
        
        #当前任务状态
        self.m_task = TASK.INIT
        
        self.cmd = String()
        self.pose = Pose()
        self.twist = Twist()
        
        
    
    def callback_thunderstorm(self, data):
        self.m_data['thunderstorm'] = data

    def callback_local_position(self, data):
        self.m_data['local_position'] = data
        
    def callback_pose(self, data):
        self.m_data['pose'] = data
        
    def callback_state(self, msg):
        self.m_state = msg
        
    def callback_angle(self, data):
        self.m_data['angel'] = data
        
    def callback_cmd_vel_flu(self, data):
        self.m_data['cmd_vel_flu'] = data
        
    def callback_cmd_pose_enu(self, data):
        self.m_data['cmd_pose_enu'] = data
    
    def callback_cmd(self, data):
        self.m_data['cmd'] = data
    
    def ARM(self):
        self.cmd = "ARM"
        # print(self.cmd)
        #self.cmd_pub.publish(self.cmd)

    def Takeoff(self):
        self.cmd = "AUTO.TAKEOFF"
        #self.cmd_pub.publish(self.cmd)
    
    def Test(self):
        # print(self.m_data['cmd'])
        # self.cmd_pose_enu_pub.publish(self.pose)
        # self.cmd_vel_flu_pub.publish(self.twist)
        self.cmd_pub.publish(self.cmd)
    

if __name__ == '__main__':
    drone = Drone()
    
    rate = rospy.Rate(1000)
    # drone.ARM()
    # drone.ARM()
    # drone.Test()
    # drone.Takeoff()
    drone.Test()
    while not rospy.is_shutdown():
        current_state = drone.m_state
        print(current_state.armed)
        if current_state is not None and current_state.armed:
            drone.Takeoff() 
        else:
            drone.ARM()
        drone.Test()
        rate.sleep()
    
    
    

    
    