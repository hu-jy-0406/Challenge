#启动仿真程序
gnome-terminal -- bash -c "roslaunch px4 zhihang2024.launch; exec bash"
sleep 1
#启动地面站
gnome-terminal -- bash -c "chmod +x ./QGroundControl.AppImage; ./QGroundControl.AppImage; exec bash"
#运行通信脚本
gnome-terminal -- bash -c "cd ~/XTDrone/communication; python3 vtol_communication.py standard_vtol 0; exec bash"
#sleep 1
#启动发布位置代码
gnome-terminal -- bash -c "cd ~/XTDrone/zhihang2024; python3 standard_vtol_position.py; exec bash"
#sleep 1
#启动需要救援的船只发布角度代码
gnome-terminal -- bash -c "cd ~/XTDrone/zhihang2024; python3 Pub_yaw.py; exec bash"
#sleep 1
#启动发布雷暴中心点的代码
gnome-terminal -- bash -c "cd ~/XTDrone/zhihang2024; python3 Pub_thunderstorm.py; exec bash"
#sleep 1
#启动控制脚本
#gnome-terminal -- bash -c "cd ~/catkin_ws/src; python3 test.py; exec bash"