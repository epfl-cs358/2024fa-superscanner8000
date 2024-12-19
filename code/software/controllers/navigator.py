import math
import numpy as np
import asyncio
import time

import config.dev_config as dconfig
from controllers.arm_positions import generate_path
from controllers.ss8 import SS8
from controllers.image_segmenter import ImageSegmenter


STEP_DISTANCE = 5
DEFAULT_CALLIBRATION_DISTANCE = 50
DEFAULT_CALLIBRATION_ITERATION = 5
CENTER_THRESHOLD = 25
ANGLE_TOLERANCE = 0.05

class Navigator:
    def __init__(self, ss8: SS8, segmenter: ImageSegmenter):
        self.ss8 = ss8
        self.segmenter = segmenter

        self.trajectory = []
        self.arm_positions = []
        self.ss8_pos = np.array([0., 0.])
        self.ss8_angle = math.pi / 2
        self.obj_pos = np.array([0., 0.])
        self.obstacles = np.array([])
        self.moving = False

        self.vertical_precision = dconfig.DEFAULT_VERTICAL_PRECISION
        self.horizontal_precision = dconfig.DEFAULT_HORIZONTAL_PRECISION
        self.taken_picture = 0

    def set_precision(self, vertical, horizontal):
        """
        Set the precision of the navigator.
        vertical (int): The vertical precision.
        horizontal (int): The horizontal precision.
        """
        self.vertical_precision = vertical
        self.horizontal_precision = horizontal

    def _callibrate(self, iteration=DEFAULT_CALLIBRATION_ITERATION, distance=DEFAULT_CALLIBRATION_DISTANCE):
        """
        Start the callibration of the device.
        iteration (int): The number of iteration to do.
        """

        print('Callibrating...')

        iteration_dist = distance / iteration

        print(f'Iteration dist : {iteration_dist}')

        if not dconfig.CONNECT_TO_TOP_CAM or not dconfig.CONNECT_TO_MOV_API:
            self._set_circle_trajectory(50, self.horizontal_precision)
            if dconfig.DEBUG_NAV:
                print(f'{len(self.trajectory)} added to the trajectory reach points :')
            
            if dconfig.DEBUG_NAV:
                for point in self.trajectory:
                    print(point[0].get_pos())
                    
            return

        self.ss8.align_to(mode='pos')
        
        if(dconfig.DEBUG_NAV):
            print('Aligned with object and ready to measure')

        distances = np.array([])
        angles = np.array([])
        
        for i in range(0, iteration):
            # y_pos = start_point+i*iteration_dist

            # if(y_pos==0):
            #     if(dconfig.DEBUG_NAV):
            #         print('Align during middle point')
                
            #     self.ss8.align_to('body')
            #     continue

            self.ss8.move_backward(iteration_dist)
            y_pos = -(i+1)*iteration_dist

            #The angle measure angle
            time.sleep(dconfig.ALIGNMENT_WAIT/2)
            theta = self.ss8.align_to(mode='cam')
            
            distances = np.append(distances, np.abs(y_pos))
            angles = np.append(angles, theta)
            if dconfig.DEBUG_NAV:
                print(f'Measure : {[y_pos, theta]}')
            
        # Could be replaced by the line below if movement is precise enough
        # self.ss8.move_backward(int(np.abs(iteration/2*iteration_dist)))
        self.ss8.move_forward(distance)
        time.sleep(dconfig.ALIGNMENT_WAIT)
        self.ss8.stop_align_to()
        self.ss8.align_to('body')

        if dconfig.DEBUG_NAV:
            print(f'Angles measured : {angles}')
            print(f'Distances measured : {distances}')

        all_radius = np.tan(np.radians(angles)) * distances
        mean_radius = np.mean(all_radius)
        if(dconfig.DEBUG_NAV):
            print(f'Mean radius : {mean_radius} cm')

        self._set_circle_trajectory(mean_radius, self.horizontal_precision)

    def add_obstacle(self, absolute_position, size=1):
        """
        Add an obstacle to the navigator.
        relative_position (NDArray[Any]): The relative position in sheeric coords of the obstacle to the ss8 (in cm).
        """
        if self._assert_no_obstacle(absolute_position, 20):
            self.obstacles = np.append(self.obstacles, ForcePoint(absolute_position, size, 2))
    
    def _assert_no_obstacle(self, pos, radius = 25):
        """
        Check if there is no obstacle in the sphere of radius around the position.
        pos (NDArray[Any]): The position to check.
        radius (int): The radius of the circle.
        """
        
        for obs in self.obstacles:
            if np.linalg.norm(obs.get_pos() - pos) < radius:
                return False
        
        return True
    
    def get_obstacle_plot_data(self):
        obstacle_contributions = np.array([obs.get_contribution(self.ss8_pos) for obs in self.obstacles])
        return self.ss8_pos, self.ss8_angle, self._get_obstacles_pos(), obstacle_contributions

    def get_trajectory_plot_data(self):
        trajectory_positions = np.array([point[0].get_pos() for point in self.trajectory])
        trajectory_contributions = np.array([point[0].get_contribution(self.ss8_pos) for point in self.trajectory])
        return trajectory_positions, trajectory_contributions

    def _get_obstacles_pos(self):
        return np.array([obs.get_pos() for obs in self.obstacles])

    def start_moving(self, on_finish):
        self._set_arm_positions(self.vertical_precision)

        for arm_pos in self.arm_positions:
            if(dconfig.SKIP_CALLIBRATION_STEP):
                if dconfig.CONNECT_TO_TOP_CAM:
                    self.ss8.align_to(mode='pos')
                self._set_circle_trajectory(80, self.horizontal_precision)
            else :
                self._callibrate()

            self.ss8.goto_cam(-90, 90)  
            if dconfig.CONNECT_TO_TOP_CAM:
                self.ss8.align_to(mode='cam', wait_for_completion=False, keep_arm_cam_settings=True)
            
            self.ss8.goto_arm(arm_pos[0], arm_pos[1])

            self.moving = True
            self._move_one_turn()
            
            self.ss8.stop_align_to()

        self.ss8.goto_arm(0, 0)
        on_finish()
        return
    
    def _move_one_turn(self):
        next_dep = None
        if dconfig.DEBUG_NAV:
            print('Start the turn')

        while self.moving:
            print('Start new dep :', next_dep)
            if next_dep is not None:
                abs_angle = math.atan2(next_dep[1], next_dep[0])
                diff_angle = abs_angle - self.ss8_angle
                norm = np.abs(np.linalg.norm(next_dep))
                self._move_of(diff_angle, norm)

            next_dep, must_take_break = self._compute_next_deplacement()
            print(f"Next dep : {next_dep}")

            time.sleep(0.5)

            if must_take_break:
                self._on_reach_point()
            
                
        return
    
    def stop_moving(self):
        self.moving = False
        
    def _set_circle_trajectory(self, radius, step_nbr):
        """
        Compute the trajectory of a circle.
        radius (int): The radius of the circle.
        step_nbr (int): The number of steps in the circle.
        """
        
        self.obj_pos = self.ss8_pos - np.array([radius, 0])
        self.trajectory = []
        step_angle = 360//step_nbr
        for a in range(0, 360, step_angle):
            x = radius * (math.cos(math.radians(a))-1)
            y = radius * math.sin(math.radians(a))
            self.trajectory.append((ForcePoint(np.array([x, y]), 50, 0), math.radians(a)))
    
    def _set_arm_positions(self, step_nbr):
        self.arm_positions = generate_path(step_nbr)
        self.arm_positions= [[0, 0]]

        if dconfig.DEBUG_ARM:
            print(f'Arm positions : \n{self.arm_positions}')

    def _get_trajectory_angle(self):
        # Get the angle to reach the next point
        tracking_vec = self.ss8_pos - self.obj_pos
        return math.atan2(tracking_vec[1], tracking_vec[0]) % (2*np.pi)

    def _compute_next_deplacement(self):
        """
        Get the next deplacement to reach the next point in the trajectory while avoiding the obstacles.
        """
        new_reach_point = False

        # Get the next point in the trajectory (the one with the closest angle above the current angle)
        reach_point = None
        while reach_point is None:
            if(len(self.trajectory) == 0):
                self.moving = False
                return None, True
            
            if(np.linalg.norm(self.trajectory[0][0].get_pos() - self.ss8_pos) < STEP_DISTANCE/2) or self._get_trajectory_angle() > self.trajectory[0][1]:
                self.trajectory.pop(0)
                new_reach_point = True
            else:
                reach_point = self.trajectory[0][0]

        if dconfig.DEBUG_NAV and False:
            print(f'\n\nCurrent position : {self.ss8_pos} || Current angle : {angle} \nReach point : {reach_point.get_pos()} || Reach angle : {self.trajectory[0][1]} \n')

        # Compute the next deplacement with the contribution of the obstacles and the reach point
        next_dep = reach_point.get_contribution(self.ss8_pos)
        for obs in self.obstacles:
            next_dep += obs.get_contribution(self.ss8_pos)

        if np.linalg.norm(next_dep) > STEP_DISTANCE:
            next_dep = (next_dep / np.linalg.norm(next_dep)) * STEP_DISTANCE

        return next_dep, new_reach_point
    
    def _move_of(self, angle, distance):
        """
        Move the device of a given angle and distance.
        angle (float): The angle to move.
        distance (float): The distance to move.
        """

        # Rotate the ss8 to the given angle (rotate left if the angle smaller than PI, right otherwise)
        angle = angle % (2*np.pi)
        
        if angle < np.pi:
            self.ss8.rotate_left(angle)
        else:
            self.ss8.rotate_right(2*np.pi - angle)
        
        self.ss8_angle = (self.ss8_angle + angle) % (2*np.pi)
        
        # Move the ss8 forward
        if(distance>00.1):
            self.ss8.move_forward(distance)
            self.ss8_pos += np.array([distance * math.cos(self.ss8_angle), distance * math.sin(self.ss8_angle)])
        
        return
    
    def _on_reach_point(self):
        """
        Pause the movement and restart it.
        """
        # Try to be in the right direction to look at the object
        correction_angle = self._get_trajectory_angle() - self.ss8_angle + np.pi/2
        
        time.sleep(dconfig.ARM_MOV_WAITING_TIME)
        self._move_of(correction_angle, 0)
        self.ss8.stop_align_to()
        self.ss8.align_to(mode='body', keep_arm_cam_settings=True)

        time.sleep(dconfig.ARM_MOV_WAITING_TIME)
        self.ss8.align_to(mode='cam', keep_arm_cam_settings=True, wait_for_completion=False)
        self.ss8.top_cam_udp_receiver.save_frame()
        self.taken_picture += 1

        picture_status_text = f'{self.taken_picture}/{self.horizontal_precision*self.vertical_precision} pictures taken'
        self.ss8.display_text(picture_status_text)

        return

DEFAULT_FORCE_NORM = 1000
DEFAULT_DIST_ORDER = 1

class ForcePoint:
    def __init__(self, pos=np.array([0, 0]), force=DEFAULT_FORCE_NORM, dist_order=DEFAULT_DIST_ORDER):
        """
        This point can either be an obstacle with a negative force norm or an object to reach with a positive force norm.
        force (int): The force norm of the point.
        pos (tuple): The position of the point.
        dist_order (int): The order of the distance norm.
        """
        self.force = force
        self.pos = pos
        self.dist_order = dist_order
    
    def get_contribution(self, pos):
        """
        Get the contribution vector of the point to the global force at a given position.
        pos (tuple): The position to compute the contribution.
        """

        dist =  self.pos - np.array(pos)
        dist_norm = np.linalg.norm(dist, ord=self.dist_order)

        return (self.force / (dist_norm ** self.dist_order)) * (dist / dist_norm)
    
    def get_pos(self):
        return self.pos
