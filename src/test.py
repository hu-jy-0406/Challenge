import rospy
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from mavros_msgs.msg import State

from enum import Enum

MAX_LINEAR = 1000
MAX_ANG_VEL = 0.5
LINEAR_STEP_SIZE = 0.1
ANG_VEL_STEP_SIZE = 0.01

#任务状态
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
        self.thunderstorm_sub = rospy.Subscriber('/zhihang/thunderstorm', Pose, self.callback_thunderstorm)
        #无人机位置（相对于仿真环境中的地面坐标系）
        self.local_position_sub = rospy.Subscriber('/gazebo/zhihang/standard_vtol/local_position', Pose, self.callback_local_position)
        #带时间戳的位置信息
        self.local_position_pose_sub = rospy.Subscriber('/standard_vtol_0/mavros/local_position/pose', PoseStamped, self.callback_pose)
        
        self.state_sub = rospy.Subscriber('/standard_vtol_0/mavros/state', State, self.callback_state)
        #无人机偏航角（无人机位置向量与目标位置向量的夹角）
        self.angle_sub = rospy.Subscriber('/zhihang/standard_vtol/angel', Pose, self.callback_angle)
        #flu坐标系：Foward（前进方向）, Left（左侧方向）, Up（上方）
        #flu坐标系下的无人机速度（Twist用于描述物体的运动状态，包括线速度和角速度）
        self.cmd_vel_flu_sub = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd_vel_flu', Twist, self.callback_cmd_vel_flu)
        #enu坐标系：East（东方）, North（北方）, Up（上方）
        #enu坐标系下的无人机位置（Pose用于描述物体在空间中的位置和方向）
        self.cmd_pose_enu_sub = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd_pose_enu', Pose, self.callback_cmd_pose_enu)
        #飞机状态，是否上锁，旋翼模式or固定翼模式等
        self.cmd_sub = rospy.Subscriber('/xtdrone/standard_vtol_0/cmd', String, self.callback_cmd)
        
        #无人机相机话题
        #--TODO--#
        
        #-----------------------------------------------------------------------------------#
        
        #------------------------------------相关话题信息------------------------------------#
        self.thunderstorm = Pose()
        self.local_position = Pose()
        self.local_position_pose = PoseStamped()
        self.state = State()
        self.angle = Pose()
        
        self.pose = Pose()
        self.twist = Twist()
        
        self.transition_state = 'multirotor'
        
        self.m_data = {
        "cmd_vel_flu": None,
        "cmd_pose_enu": None,
        "cmd": None,
        }
        
        
        
        
        
        #当前任务状态
        self.m_task = TASK.INIT
        
        #------------------------------------setpoints------------------------------------#
        self.cmd = String()
        self.set_pose = Pose()
        self.set_twist = Twist()        
        
    #------------------------------------callback_functions------------------------------------#
    def callback_thunderstorm(self, msg):
        self.thunderstorm = msg

    def callback_local_position(self, msg):
        self.local_position = msg
        
    def callback_pose(self, msg):
        self.local_position_pose = msg
        
    def callback_state(self, msg):
        self.state = msg
        
    def callback_angle(self, msg):
        self.angle = msg
        
    def callback_cmd_vel_flu(self, msg):
        self.m_data['cmd_vel_flu'] = msg
        
    def callback_cmd_pose_enu(self, msg):
        self.m_data['cmd_pose_enu'] = msg
    
    def callback_cmd(self, msg):
        self.m_data['cmd'] = msg
    
    def ARM(self):
        self.cmd = "ARM"
        # print(self.cmd)
        #self.cmd_pub.publish(self.cmd)
    def OFFBOARD(self):
        self.cmd = "OFFBOARD"
        #self.cmd_pub.publish(self.cmd)

    def Takeoff(self):
        self.upward = 0.4
        self.cmd = "OFFBOARD"
        #self.cmd_pub.publish(self.cmd)
    
    def Send(self):
        # print(self.m_data['cmd'])
        print(self.m_state)
        self.cmd_pose_enu_pub.publish(self.pose)
        self.cmd_vel_flu_pub.publish(self.twist)
        self.cmd_pub.publish(self.cmd)
    

if __name__ == '__main__':
    i = 0
    
    drone = Drone()
    
    rate = rospy.Rate(1)
    
    while not rospy.is_shutdown():
        
        print(i)

        if i == 1:
            print("test0")
            drone.OFFBOARD()
            drone.set_twist.linear.x = 0.0
            drone.set_twist.linear.y = 0.0
            drone.set_twist.linear.z = 1.6
            drone.set_twist.angular.x = 0.0
            drone.set_twist.angular.y = 0.0
            drone.set_twist.angular.z = 0.0  
        elif i == 2:
            print("test1")
            drone.ARM()
        else:
            if drone.local_position.position.z >= 25:
                drone.set_twist.linear.x = 0.0
                drone.set_twist.linear.y = 0.0
                drone.set_twist.linear.z = 0.0
                drone.set_twist.angular.z = 0.0
                drone.cmd = 'HOVER'
                print("HOVER")
            

            
        print("send")
        #drone.cmd_pose_enu_pub.publish(drone.set_pose)
        print(drone.local_position)
        drone.cmd_vel_flu_pub.publish(drone.set_twist)
        
        drone.cmd_pub.publish(drone.cmd)
        #drone.cmd = ''
        i += 1
        print(i)
        
        rospy.sleep(1)
        
    
    
    

    
    