import rclpy
from rclpy.node import Node
import ros2pkg
from geometry_msgs.msg import Twist,PoseStamped,Pose,TransformStamped
from ssafy_msgs.msg import TurtlebotStatus, MapScan
from sensor_msgs.msg import Imu,LaserScan
from std_msgs.msg import Float32, Int8MultiArray
from squaternion import Quaternion
from nav_msgs.msg import Odometry,Path,OccupancyGrid,MapMetaData
from math import pi,cos,sin,sqrt
import tf2_ros
import os
import sub3.utils as utils
import numpy as np
import cv2
import time

# mapping node의 전체 로직 순서
# 1. publisher, subscriber, msg 생성
# 2. mapping 클래스 생성
# 3. 맵의 resolution, 중심좌표, occupancy에 대한 threshold 등의 설정 받기
# 4. laser scan 메시지 안의 ground truth pose 받기
# 5. lidar scan 결과 수신
# 6. map 업데이트 시작
# 7. pose 값을 받아서 좌표변환 행렬로 정의
# 8. laser scan 데이터 좌표 변환
# 9. pose와 laser의 grid map index 변환
# 10. laser scan 공간을 맵에 표시
# 11. 업데이트 중인 map publish
# 12. 맵 저장

params_map = {
    "MAP_RESOLUTION": 0.05,
    "OCCUPANCY_UP": 0.02,
    "OCCUPANCY_DOWN": 0.01,
    "MAP_CENTER": (-8.0, -4.0),
    "MAP_SIZE": (17.5, 17.5),
    "MAP_FILENAME": 'test.png',
    "MAPVIS_RESIZE_SCALE": 2.0
}


def createLineIterator(P1, P2, img):

    # Bresenham's line algorithm을 구현해서 이미지에 직선을 그리는 메소드입니다.
    
    # 로직 순서
    # 1. 두 점을 있는 백터의 x, y 값과 크기 계산
    # 2. 직선을 그릴 grid map의 픽셀 좌표를 넣을 numpy array 를 predifine
    # 3. 직선 방향 체크
    # 4. 수직선의 픽셀 좌표 계산
    # 5. 수평선의 픽셀 좌표 계산
    # 6. 대각선의 픽셀 좌표 계산
    # 7. 맵 바깥 픽셀 좌표 삭제

   
    imageH = img.shape[0] #height
    imageW = img.shape[1] #width
    P1Y = P1[1] #시작점 y 픽셀 좌표
    P1X = P1[0] #시작점 x 픽셀 좌표
    P2X = P2[0] #끝점 y 픽셀 좌표
    P2Y = P2[1] #끝점 x 픽셀 좌표

    """
    로직 1 : 두 점을 있는 백터의 x, y 값과 크기 계산
    
    dX = 
    dY = 
    dXa = 
    dYa = 

    """

    """
    # 로직 2 : 직선을 그릴 grid map의 픽셀 좌표를 넣을 numpy array 를 predifine

    itbuffer =  
    itbuffer.fill(np.nan)

    """

    """
    # 로직 3 : 직선 방향 체크
 
    negY = 
    negX = 
 
    """
    
    """ 
    # 로직 4 : 수직선의 픽셀 좌표 계산   
    if P1X == P2X:        
        itbuffer[:,0] = P1X
        if negY:
            itbuffer[:,1] = 
        else:
            itbuffer[:,1] = 
     
    """

    """
    # 로직 5 : 수평선의 픽셀 좌표 계산

    elif P1Y == P2Y:        
        itbuffer[:,1] = 
        if negX:
            
        else:
     
    """

    """ 
    # 로직 6 : 대각선의 픽셀 좌표 계산  

    else:        
        steepSlope = dYa > dXa 
        if steepSlope:
            slope = 
            if negY:
                itbuffer[:,1] = 
            else:
                itbuffer[:,1] = 
            itbuffer[:,0] = 
        else:
            slope = 
            if negX:
                itbuffer[:,0] = 
            else:
                itbuffer[:,0] = 
            itbuffer[:,1] = 

    """

    
    """
    로직 7 : 맵 바깥 픽셀 좌표 삭제.
    colX = 
    colY = 
    itbuffer = 
    
    """
    itbuffer = []
    # itbuffer[:,2] = img[itbuffer[:,1].astype(np.uint),itbuffer[:,0].astype(np.uint)]

    return itbuffer


class Mapping:

    # 사용자가 정의한 맵 설정을 받아서 회색의 어레이로 초기화 시키고,
    # 로봇의 pose와 2d 라이다 값들을 받은 다음,
    # 라이다가 나타내는 로봇으로부터 측정된 좌표와의 직선을
    # utils_skeleton.py에 있는 createLineIterator()로
    # 그려가면서 맵을 채워서 저장할 수 있도록 만든 스크립트입니다.

    def __init__(self, params_map):

        self.map_resolution = params_map["MAP_RESOLUTION"]
        self.map_size = np.array(params_map["MAP_SIZE"]) / self.map_resolution
        self.map_center = params_map["MAP_CENTER"]
        self.map = np.ones((self.map_size[0].astype(np.int), self.map_size[1].astype(np.int)))*0.5
        self.occu_up = params_map["OCCUPANCY_UP"]
        self.occu_down = params_map["OCCUPANCY_DOWN"]

        self.map_filename = params_map["MAP_FILENAME"]
        self.map_vis_resize_scale = params_map["MAPVIS_RESIZE_SCALE"]

        self.T_r_l = np.array([[0,-1,0],[1,0,0],[0,0,1]])


    def update(self, pose, laser):

        # 로직 7. pose 값을 받아서 좌표변환 행렬로 정의
        n_points = laser.shape[1]
        pose_mat = utils.xyh2mat2D(pose)


        # 로직 8. laser scan 데이터 좌표 변환
        pose_mat = np.matmul(pose_mat,self.T_r_l)
        laser_mat = np.ones((3, n_points))
        laser_mat[:2, :] = laser

        laser_global = np.matmul(pose_mat, laser_mat)

        """
        로직 9. pose와 laser의 grid map index 변환
        (#으로 주석처리된 것을 해제하고 쓰시고, 나머지 부분은 직접 완성시켜 실행하십시오)
        # pose_x = (pose[0] - self.map_center[0] + (self.map_size[0]*self.map_resolution)/2) / self.map_resolution
        # pose_y = (pose[1] - self.map_center[1] + (self.map_size[1]*self.map_resolution)/2) / self.map_resolution
        laser_global_x = 
        laser_global_y = 
        """

        """
        # 로직 10. laser scan 공간을 맵에 표시
        for i in range(laser_global.shape[1]):
            p1 = np.array([pose_x, pose_y]).reshape(-1).astype(np.int)
            p2 = np.array([laser_global_x[i], laser_global_y[i]]).astype(np.int)
        
            line_iter = utils.createLineIterator(p1, p2, self.map)
        
            if (line_iter.shape[0] is 0):
                continue
        
            avail_x = 
            avail_y = 
        
            ## Empty
            self.map[avail_y[:-1], avail_x[:-1]] = 
        
            ## Occupied
            self.map[avail_y[-1], avail_x[-1]] = 
        """        

        # self.show_pose_and_points(pose, laser_global)        

    def __del__(self):
        # 로직 12. 종료 시 map 저장
        ## Ros2의 노드가 종료될 때 만들어진 맵을 저장하도록 def __del__과 save_map이 정의되어 있습니다
        self.save_map(())
        
    def save_map(self):
        map_clone = self.map.copy()
        cv2.imwrite(self.map_filename, map_clone*255)



    def show_pose_and_points(self, pose, laser_global):
        tmp_map = self.map.astype(np.float32)
        map_bgr = cv2.cvtColor(tmp_map, cv2.COLOR_GRAY2BGR)

        pose_x = (pose[0] - self.map_center[0] + (self.map_size[0]*self.map_resolution)/2) / self.map_resolution
        pose_y = (pose[1] - self.map_center[1] + (self.map_size[1]*self.map_resolution)/2) / self.map_resolution

        laser_global_x = (laser_global[0, :] - self.map_center[0] + (self.map_size[0]*self.map_resolution)/2) / self.map_resolution
        laser_global_y =  (laser_global[1, :] - self.map_center[1] + (self.map_size[1]*self.map_resolution)/2) / self.map_resolution

        for i in range(laser_global.shape[1]):
            (l_x, l_y) = np.array([laser_global_x[i], laser_global_y[i]]).astype(np.int)
            center = (l_x, l_y)
            cv2.circle(map_bgr, center, 1, (0,255,0), -1)

        center = (pose_x.astype(np.int32)[0], pose_y.astype(np.int32)[0])
        
        cv2.circle(map_bgr, center, 2, (0,0,255), -1)

        map_bgr = cv2.resize(map_bgr, dsize=(0, 0), fx=self.map_vis_resize_scale, fy=self.map_vis_resize_scale)
        # cv2.imshow('Sample Map', map_bgr)
        # cv2.waitKey(1)



        
class Mapper(Node):

    def __init__(self):
        super().__init__('Mapper')
        
        # 로직 1 : publisher, subscriber, msg 생성
        self.subscription = self.create_subscription(LaserScan,
        '/scan',self.scan_callback,10)
        self.map_pub = self.create_publisher(OccupancyGrid, '/map', 1)
        
        self.map_msg=OccupancyGrid()
        self.map_msg.header.frame_id="map"
        self.map_size=int(params_map["MAP_SIZE"][0]\
            /params_map["MAP_RESOLUTION"]*params_map["MAP_SIZE"][1]/params_map["MAP_RESOLUTION"])
        

        m = MapMetaData()
        m.resolution = params_map["MAP_RESOLUTION"]
        m.width = int(params_map["MAP_SIZE"][0]/params_map["MAP_RESOLUTION"])
        m.height = int(params_map["MAP_SIZE"][1]/params_map["MAP_RESOLUTION"])
        quat = np.array([0, 0, 0, 1])
        m.origin = Pose()
        m.origin.position.x = params_map["MAP_CENTER"][0]-8.75
        m.origin.position.y = params_map["MAP_CENTER"][1]-8.75
        self.map_meta_data = m

        self.map_msg.info=self.map_meta_data

        # socket에서 받아온 맵 만들기 실행 여부 정보 받기
        self.create_map_sub = self.create_subscription(MapScan, '/map_scan', self.map_scan_callback, 100)

        # is_map_create 변수가 True면 mapping 시작, std_msg에서 받아온 값으로 확인
        self.is_map_create = False

        # 로직 2 : mapping 클래스 생성
        self.mapping = Mapping(params_map)


    def map_scan_callback(self, msg):
        self.is_map_create = msg.map_scan
        print("runmapping의 데이터 값", msg)


    def scan_callback(self, msg):
        
        """
        # 로직 4 : laser scan 메시지 안의 ground truth pose 받기
        pose_x = 
        pose_y = 
        heading = 
        """

        pose = np.array([[pose_x],[pose_y],[heading]])

        # 소켓에서 들어온 map_create 변수가 1일 경우에만 lidar 이용해 mapping시작 
        if self.is_map_create:
            self.mapping.update(pose, laser)

            np_map_data=self.mapping.map.reshape(1,self.map_size) 
            list_map_data=np_map_data.tolist()
            for i in range(self.map_size):
                list_map_data[0][i]=100-int(list_map_data[0][i]*100)
                if list_map_data[0][i] >100 :
                    list_map_data[0][i]=100
    
                if list_map_data[0][i] <0 :
                    list_map_data[0][i]=0
    

            self.map_msg.header.stamp =rclpy.clock.Clock().now().to_msg()
            self.map_msg.data=list_map_data[0]
            self.map_pub.publish(self.map_msg)

def save_map(node,file_path):

    pkg_path =os.getcwd()
    back_folder='..'
    folder_name='map'
    file_name=file_path
    full_path=os.path.join(pkg_path,back_folder,folder_name,file_name)
    print(full_path)
    f=open(full_path,'w')
    data=''
    for pixel in node.map_msg.data :

        data+='{0} '.format(pixel)
    f.write(data) 
    f.close()

    # 맵을 저장한 이후 원래 변수 값을 초기화 시켜준다.
    

        
def main(args=None):    
    rclpy.init(args=args)
    
    try :    
        run_mapping = Mapper()
        rclpy.spin(run_mapping)
        run_mapping.destroy_node()
        rclpy.shutdown()

    except :
        save_map(run_mapping,'map.txt')
 


if __name__ == '__main__':
    main()

  