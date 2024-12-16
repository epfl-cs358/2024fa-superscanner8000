import math
import numpy as np

STEP_DISTANCE = 5
DEFAULT_CALLIBRATION_DISTANCE = 10000
CENTER_THRESHOLD = 50

class Navigator:
    def __init__(self, ss8, segmenter):
        self.ss8 = ss8

        self.trajectory = []
        self.ss8_pos = np.array([0, 0])
        self.ss8_angle = math.pi / 2
        self.obj_pos = np.array([0, 0])
        self.obstacles = np.array([])
        self.moving = False

    def callibrate(self, iteration, distance=DEFAULT_CALLIBRATION_DISTANCE, on_finish=lambda:None):
        """
        Start the callibration of the device.
        iteration (int): The number of iteration to do.
        """

        self._align_ss8_to_obj()

        iteration_dist = distance / iteration
        angles = np.array([])

        self.ss8.move_backward(int(-iteration/2*iteration_dist), lambda: self.ss8.get_arm_cam_angle(lambda angle: angles.append(angle.alpha)))

        def save_and_forward(i, max, on_finish):
            self.ss8.get_arm_cam_angle(lambda angle: angles.append(angle.alpha))
            if(i+1<max):
                self.ss8.move_forward(iteration_dist, lambda: save_and_forward(i+1, max))
            else :
                self.ss8.move_backward(int(-iteration/2*iteration_dist), on_finish)

        self.ss8.move_forward(iteration_dist, lambda: save_and_forward(1, iteration, on_finish))            

    def add_obstacle(self, relative_position, size=1):
        """
        Add an obstacle to the navigator.
        relative_position (NDArray[Any]): The relative position in sheeric coords of the obstacle to the ss8 (in cm).
        """
        self.obstacles = np.append(self.obstacles, ForcePoint(self.ss8_pos+relative_position, size, 3))
        
    def start_moving(self):
        self.moving = True
        self._compute_next_deplacement()
    
    def stop_moving(self):
        self.moving = False

    def _align_ss8_to_obj(self):
        frame = self.capture_image()
        obj_coords = self.segmenter.get_object_coords(frame)
        frame_center = frame.shape[:2]/2
        pos_diff = obj_coords - frame_center
        if(pos_diff[0] > CENTER_THRESHOLD):
            self.ss8.move_forward(10000)
            moving_state = 'forward'
        elif(pos_diff[0] < -CENTER_THRESHOLD):
            self.ss8.move_backward(10000)
            moving_state = 'backward'
        else:
            moving_state = 'none'

        def check_if_stop():
            frame = self.capture_image()
            obj_coords = self.segmenter.get_object_coords(frame)
            frame_center = frame.shape[:2]/2
            pos_diff = obj_coords - frame_center

            if(moving_state == 'forward' and pos_diff[0] < CENTER_THRESHOLD):
                self.ss8.stop_mov()
            elif(moving_state == 'backward' and pos_diff[0] > -CENTER_THRESHOLD):
                self.ss8.stop_mov()
            else:
                self.after(100, check_if_stop)

            self.ss8.forward()
        
    def _set_circle_trajectory(self, radius, step_nbr):
        """
        Compute the trajectory of a circle.
        radius (int): The radius of the circle.
        step_nbr (int): The number of steps in the circle.
        """
        self.obj_pos = self.pos - np.array([radius, 0])
        self.trajectory = []
        for a in range(0, 360, 360//step_nbr):
            x = radius * math.cos(math.radians(a))
            y = radius * math.sin(math.radians(a))
            self.trajectory.append((ForcePoint(np.array([x, y])), math.radians(a)))
    
    def _compute_next_deplacement(self):
        """
        Get the next deplacement to reach the next point in the trajectory while avoiding the obstacles.
        """
        
        # Get the angle to reach the next point
        angle = np.tan(self.ss8_pos - self.obj_pos)

        # Get the next point in the trajectory (the one with the closest angle above the current angle)
        reach_point = self.trajectory[0]
        while reach_point[1] < angle:
            self.moving = False
            reach_point = self.trajectory.pop(0)
            
        reach_point = self.trajectory[0][0]

        # Compute the next deplacement with the contribution of the obstacles and the reach point
        next_dep = reach_point.get_contribution(self.ss8_pos)
        for obs in self.obstacle:
            next_dep += obs.get_contribution(self.ss8_pos)

        next_dep = (next_dep / np.linalg.norm(next_dep)) * STEP_DISTANCE
        angle = np.tan(next_dep) - self.ss8_angle

        self._mov_of(angle, STEP_DISTANCE, self._compute_next_deplacement if self.moving else None)
    
    def _mov_of(self, angle, distance, next):
        """
        Move the device of a given angle and distance.
        angle (float): The angle to move.
        distance (float): The distance to move.
        """

        # Rotate the ss8 to the given angle (rotate left if the angle smaller than PI, right otherwise)
        if angle < np.pi:
            rotation_time = self.ss8.rotate_left(angle)
        else:
            rotation_time = self.ss8.rotate_right(2*np.pi - angle, self.ss8.move_forward(distance, next))

DEFAULT_FORCE_NORM = 1
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

        dist = np.array(pos) - self.pos
        dist_norm = np.linalg.norm(dist, ord=self.dist_order)

        if dist_norm < 0.1:
            return np.array([0, 0])

        return (self.force / (dist_norm ** self.dist_order)) * (dist / dist_norm)
