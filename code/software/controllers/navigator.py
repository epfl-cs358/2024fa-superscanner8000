import math
import numpy as np

STEP_DISTANCE = 5

class Navigator:
    def __init__(self):
        self.obstacles = np.array([])
        self.ss8_pos = np.array([0, 0])
        self.ss8_angle = math.pi / 2
        self.trajectory = []
        self.obj_pos = np.array([0, 0])

    def set_circle_trajectory(self, radius, step_nbr):
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
    
    def _get_next_deplacement(self):
        """
        Get the next deplacement to reach the next point in the trajectory while avoiding the obstacles.
        """
        
        # Get the angle to reach the next point
        angle = np.tan(self.ss8_pos - self.obj_pos)

        # Get the next point in the trajectory (the one with the closest angle above the current angle)
        reach_point = self.trajectory[0]
        while reach_point[1] < angle:
            reach_point = self.trajectory.pop(0)
        reach_point = self.trajectory[0][0]

        # Compute the next deplacement with the contribution of the obstacles and the reach point
        next_dep = reach_point.get_contribution(self.ss8_pos)
        for obs in self.obstacle:
            next_dep += obs.get_contribution(self.ss8_pos)

        next_dep = (next_dep / np.linalg.norm(next_dep)) * STEP_DISTANCE
        angle = np.tan(next_dep) - self.ss8_angle

        return angle, STEP_DISTANCE
    
    def add_obstacle(self, pos):
        self.obstacles = np.append(self.obstacles, ForcePoint(pos, 1, 4))
        
    def start_moving(self):
        def compute_next_deplacement():
            angle, distance = self.nav.get_next_deplacement()
            self._mov_of(angle, distance, compute_next_deplacement)


    def _mov_of(self, angle, distance, next):
        """
        Move the device of a given angle and distance.
        angle (float): The angle to move.
        distance (float): The distance to move.
        """

        # Rotate the ss8 to the given angle (rotate left if the angle smaller than PI, right otherwise)
        if angle < np.PI:
            rotation_time = self.controller.ss8.rotate_left(angle)
        else:
            rotation_time = self.controller.ss8.rotate_right(2*np.PI - angle)

        # Function to be called after the ss8 has completed the rotation
        def after_rotation():
            moving_time = self.controller.ss8.move_forward(distance)
            self.after(moving_time, next)

        self.after(rotation_time, after_rotation)
        

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
