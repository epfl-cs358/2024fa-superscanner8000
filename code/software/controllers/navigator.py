import math
import numpy as np
import asyncio
import config.dev_config as dconfig

STEP_DISTANCE = 5
DEFAULT_CALLIBRATION_DISTANCE = 10000
DEFAULT_CALLIBRATION_ITERATION = 4
CENTER_THRESHOLD = 25

class Navigator:
    def __init__(self, ss8):
        self.ss8 = ss8

        self.trajectory = []
        self.arm_positions = []
        self.ss8_pos = np.array([0., 0.])
        self.ss8_angle = math.pi / 2
        self.obj_pos = np.array([0., 0.])
        self.obstacles = np.array([])
        self.moving = False

        self.vertical_precision = dconfig.DEFAULT_VERTICAL_PRECISION
        self.horizontal_precision = dconfig.DEFAULT_HORIZONTAL_PRECISION

    def set_precision(self, vertical, horizontal):
        """
        Set the precision of the navigator.
        vertical (int): The vertical precision.
        horizontal (int): The horizontal precision.
        """
        self.vertical_precision = vertical
        self.horizontal_precision = horizontal

    async def callibrate(self, iteration, distance=DEFAULT_CALLIBRATION_DISTANCE):
        """
        Start the callibration of the device.
        iteration (int): The number of iteration to do.
        """

        print('Callibrating...')

        self._set_circle_trajectory(50, self.horizontal_precision)
        self._set_arm_positions(self.vertical_precision)

        if dconfig.DEBUG_NAV:
            print(f'{len(self.trajectory)} added to the trajectory reach point')

        return 
        if not dconfig.SIMULATION_MODE:
            self._align_ss8_to_obj()

        iteration_dist = distance / iteration
        measures = np.array([])

        start_point = -iteration/2*iteration_dist
        await self.ss8.move_backward(int(start_point))
        measures.append(np.array([np.abs(start_point), await self.ss8.get_arm_cam_angle()]))

        for i in range(1, iteration):
            await self.ss8.move_forward(iteration_dist)

            if not dconfig.SIMULATION_MODE:
                measure = [np.abs(start_point+i*iteration_dist), await self.ss8.get_arm_cam_angle()]
                measures.append(np.array(measure))

        await self.ss8.move_backward(int(-iteration/2*iteration_dist))

        return np.mean(np.tan(measures[:, 0]) * measures[:, 1])

    def add_obstacle(self, relative_position, size=1):
        """
        Add an obstacle to the navigator.
        relative_position (NDArray[Any]): The relative position in sheeric coords of the obstacle to the ss8 (in cm).
        """
        self.obstacles = np.append(self.obstacles, ForcePoint(self.ss8_pos+relative_position, size, 3))
        
    async def start_moving(self, on_finish, callibrate=True):
        self.moving = True

        if(callibrate):
            await self.callibrate(DEFAULT_CALLIBRATION_ITERATION)

        while self.moving:

            next_dep, must_take_break = self._compute_next_deplacement()

            if must_take_break:
                await self._on_reach_point()

            if self.moving:
                abs_angle = math.atan2(next_dep[1], next_dep[0])
                diff_angle = abs_angle - self.ss8_angle
                norm = np.linalg.norm(next_dep)
                # print('Next deplacement : ', next_dep)
                #await asyncio.sleep(1)
                await self._move_of(diff_angle, norm)

        on_finish()
        return
    
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
        self.obj_pos = self.ss8_pos - np.array([radius, 0])
        self.trajectory = []
        step_angle = 360//step_nbr
        for a in range(step_angle, 360, step_angle):
            x = radius * (math.cos(math.radians(a))-1)
            y = radius * math.sin(math.radians(a))
            self.trajectory.append((ForcePoint(np.array([x, y])), math.radians(a)))
    def _set_arm_positions(self, step_nbr):
        pass

    def _compute_next_deplacement(self):
        """
        Get the next deplacement to reach the next point in the trajectory while avoiding the obstacles.
        """
        new_reach_point = False
        
        # Get the angle to reach the next point
        tracking_vec = self.ss8_pos - self.obj_pos
        angle = math.atan2(tracking_vec[1], tracking_vec[0]) % (2*np.pi)

        # Get the next point in the trajectory (the one with the closest angle above the current angle)
        reach_point = None
        while reach_point is None:
            if(len(self.trajectory) == 0):
                self.moving = False
                self.on_finish()
                return np.array([0, 0]), False
            
            if(self.trajectory[0][1] < angle):
                self.trajectory.pop(0)
                new_reach_point = True
            else:
                reach_point = self.trajectory[0][0]

        if dconfig.DEBUG_NAV:
            print(f'\n\nCurrent position : {self.ss8_pos} ||    Current angle : {angle} \nReach point : {reach_point.get_pos()}        || Reach angle : {self.trajectory[0][1]} \n\n')


        # Compute the next deplacement with the contribution of the obstacles and the reach point
        next_dep = reach_point.get_contribution(self.ss8_pos)
        """ for obs in self.obstacles:
            next_dep += obs.get_contribution(self.ss8_pos) """

        next_dep = (next_dep / np.linalg.norm(next_dep)) * STEP_DISTANCE
        

        return next_dep, new_reach_point
    
    async def _move_of(self, angle, distance):
        """
        Move the device of a given angle and distance.
        angle (float): The angle to move.
        distance (float): The distance to move.
        """

        # Rotate the ss8 to the given angle (rotate left if the angle smaller than PI, right otherwise)
        angle = angle % (2*np.pi)
        
        if angle < np.pi:
            await self.ss8.rotate_left(angle)
        else:
            await self.ss8.rotate_right(2*np.pi - angle)
        
        self.ss8_angle = (self.ss8_angle + angle) % (2*np.pi)
        
        # Move the ss8 forward
        await self.ss8.move_forward(distance)
        self.ss8_pos += np.array([distance * math.cos(self.ss8_angle), distance * math.sin(self.ss8_angle)])
        return
    
    async def _on_reach_point(self):
        """
        Pause the movement and restart it.
        """
        self.moving = False
        print('Take picture')
        self.moving = True
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

        if dist_norm < 0.1:
            return np.array([0, 0])

        return (self.force / (dist_norm ** self.dist_order)) * (dist / dist_norm)
    
    def get_pos(self):
        return self.pos
