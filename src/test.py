import rospy
from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from mavros_msgs.msg import State
from mavros_msgs.msg import CameraImageCaptured

from enum import Enum

# MAX_LINEAR = 1000
# MAX_ANG_VEL = 0.5
# LINEAR_STEP_SIZE = 0.1
# ANG_VEL_STEP_SIZE = 0.01

#GPS引导点（mavros坐标）
GPS = {"x": -3500, "y": -3500}

#任务状态（状态机）
class TASK(Enum):
    TAKEOFF = 0    #起飞并切换至固定翼模式
    TRACK   = 1    #以固定翼模式飞至引导点，中途躲避雷暴区域
    SEARCH  = 2    #在引导点附近搜寻目标
    LAND    = 3    #切换至旋翼模式并降落到目标上


#脚本通过XTDrone/communication/vtol_communication.py与无人机通信
#无人机控制方法参见XTDrone/keyboard/vtol_keyboard_control.py
class Drone:
    def __init__(self) -> None:
        rospy.init_node('drone', anonymous=True)
        
        #------------------------------------Publishers------------------------------------#
        #enu坐标系：East（东方）, North（北方）, Up（上方）
        #enu坐标系下的无人机位置（Pose用于描述物体在空间中的位置和方向）
        #mavros用的是enu坐标系
        self.cmd_pose_enu_pub = rospy.Publisher('/xtdrone/standard_vtol_0/cmd_pose_enu', Pose, queue_size=1)
        
        #self.local_pose_pub = rospy.Publisher('/xtdrone/standard_vtol_0/mavros/local_position/pose', PoseStamped, queue_size=1)
        
        #flu坐标系：Foward（前进方向）, Left（左侧方向）, Up（上方）
        #flu坐标系下的无人机速度（Twist用于描述物体的运动状态，包括线速度和角速度）
        self.cmd_vel_flu_pub = rospy.Publisher('/xtdrone/standard_vtol_0/cmd_vel_flu', Twist, queue_size=1)
        
        #飞机状态，是否上锁，旋翼模式or固定翼模式等
        self.cmd_pub = rospy.Publisher('/xtdrone/standard_vtol_0/cmd', String, queue_size=1)
        
        #--TODO--#
        '''
        self.arrive_pub
        self.ship_pub
        '''
        #----------------------------------------------------------------------------------#
        
        
        #------------------------------------Subscribers-----------------------------------#
        #雷暴中心点位置（随机，z的值是零，只能绕过，半径1000米，基于gazebo坐标系）
        self.thunderstorm_sub = rospy.Subscriber('/zhihang/thunderstorm', Pose, self.callback_thunderstorm)
        #无人机位置（基于gazebo坐标系，主办方给的信息都是基于gazebo坐标系）
        self.gazebo_position_sub = rospy.Subscriber('/gazebo/zhihang/standard_vtol/local_position', Pose, self.callback_gazebo_position)
        #带时间戳的位置信息（基于marvros的enu坐标系，两个坐标系不一样）
        self.mavros_pose_sub = rospy.Subscriber('/standard_vtol_0/mavros/local_position/pose', PoseStamped, self.callback_pose)
        #当前飞机状态#
        self.state_sub = rospy.Subscriber('/standard_vtol_0/mavros/state', State, self.callback_state)
        #无人机偏航角（无人机位置向量与目标位置向量的夹角）
        self.angle_sub = rospy.Subscriber('/zhihang/standard_vtol/angel', Pose, self.callback_angle)

        #无人机相机话题
        self.img = rospy.Subscriber('/standard_vtol_0/mavros/camera/image_captured', CameraImageCaptured, self.callback_img)
        
        #----------------------------------------------------------------------------------#
        
        #------------------------------------相关话题信息------------------------------------#
        self.thunderstorm = Pose()
        self.gazebo_position = Pose()
        self.mavros_pose = PoseStamped()
        self.state = State()
        self.angle = Pose()
        self.img = CameraImageCaptured()
        #-----------------------------------------------------------------------------------#
        
        
        #当前任务状态
        self.m_task = TASK.TAKEOFF
        
        #当前飞机模态
        self.transition_state = 'multirotor'
        
        #------------------------------------setpoints------------------------------------#
        self.cmd_pose_enu = Pose()#基于gazebo坐标系
        self.cmd_vel_flu = Twist()  
        self.cmd = String()   
        #---------------------------------------------------------------------------------#   
        
    #------------------------------------callback_functions------------------------------------#
    def callback_thunderstorm(self, msg):
        self.thunderstorm = msg

    def callback_gazebo_position(self, msg):
        self.gazebo_position = msg
        
    def callback_pose(self, msg):
        self.mavros_pose = msg
        
    def callback_state(self, msg):
        self.state = msg
        
    def callback_angle(self, msg):
        self.angle = msg
        
    def callback_img(self, msg):
        self.img = msg
        print("----img----")
        print(self.img)
        print("----img----")
    #-----------------------------------------------------------------------------------------#
    
    

    #------------------------------------任务函数------------------------------------#
    def Takeoff(self):

        # 设置起飞速度->OFFBOARD->ARM
        # 到达目标高度后悬停
        
        #--TODO--#
        #起飞时旋转机身使得机头方向朝南
        
        if self.state.mode == "OFFBOARD":
            self.cmd = "ARM"
        else:
            self.cmd_vel_flu.linear.x = 0.0
            self.cmd_vel_flu.linear.y = 0.0
            self.cmd_vel_flu.linear.z = 3.0
            self.cmd_vel_flu.angular.x = 0.0
            self.cmd_vel_flu.angular.y = 0.0
            self.cmd_vel_flu.angular.z = 0.0
            self.cmd = "OFFBOARD"
        '''
        if self.local_position.position.z >= 24:
            self.set_twist.linear.x = 0.0
            self.set_twist.linear.y = 0.0
            self.set_twist.linear.z = 0.0
            self.set_twist.angular.z = 0.0
            self.cmd = "HOVER"
            self.m_task = TASK.TRACK 
        '''
        #起飞高度大于30m时，切换至固定翼模式
        #参数是测试用的
        if self.gazebo_position.position.z >= 30:
            self.cmd_pose_enu.position.x = -100
            self.cmd_pose_enu.position.y = -100
            self.cmd_pose_enu.position.z = 25
            self.transition_state = 'plane'
            self.cmd = self.transition_state
            self.m_task = TASK.TRACK
          
            
    #--TODO--#
    
    def Track(self):
        # 飞至引导点
        # 中途躲避雷暴区域
        # 到达引导点后悬停
        print("Begin to track")
        if self.transition_state == 'plane':
            self.cmd = 'loiter'
        #--TODO--#
        
    
    # def Search(self):
    #     # 在引导点附近搜寻目标
    #     pass
    # def Land(self):
    #     # 切换至旋翼模式并降落到目标上
    #     pass
    
    #----------------------------------------------------------------------------#
    
    #发布控制信息
    def PubMsg(self):
        if self.transition_state == 'plane':
            self.cmd_pose_enu_pub.publish(self.cmd_pose_enu)
        else:
            self.cmd_vel_flu_pub.publish(self.cmd_vel_flu)
        self.cmd_pub.publish(self.cmd)
        self.cmd = ''
    
def Transform(g_x, g_y, g_z):
    #将gazebo坐标转换为mavros enu坐标
    m_x = g_x - 2300.0
    m_y = g_y - 2300.0
    m_z = g_z - 4.50
    return m_x, m_y, m_z

if __name__ == '__main__':
    
    drone = Drone()
    
    rate = rospy.Rate(1)
    
    while not rospy.is_shutdown():

        # print("----thunderstrom----")
        # print(drone.thunderstorm)
        # print('\n')

        print("----gazebo_position----")
        print(drone.gazebo_position.position)
        print("----mavros_position----")
        print(drone.mavros_pose.pose.position)
        print('\n')

        if drone.m_task == TASK.TAKEOFF:
            drone.Takeoff()

        elif drone.m_task == TASK.TRACK:
            drone.Track()

        else:
            #--TODO--#
            pass
        
        drone.PubMsg()
        rospy.sleep(1)
        
    
    
    

    
    