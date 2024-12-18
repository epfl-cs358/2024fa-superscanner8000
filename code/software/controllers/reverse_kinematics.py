import numpy as np
from scipy.spatial.transform import Rotation as Rot
import scipy.optimize  as opt

def get_top_cam_angles(hor_angle, vert_angle, arm_angle):
    # Given final rotation matrix
    R_final = Rot.from_euler('xyz', [hor_angle, 0, vert_angle], degrees=True).as_matrix()

    # Fixed angle alpha: defines the axis of R1 on the XY plane
    gamma = np.radians(arm_angle)
    u1 = np.array([np.cos(gamma), np.sin(gamma), 0])  # Rotation axis for R1
    print(u1)

    # Function to compute the error between R_final and R2 @ R1
    def error_function(params):
        alpha, beta = params  # Rotation angles for R1 and R2

        # R1: Rotation around custom axis u1
        R1 = Rot.from_rotvec(alpha * u1).as_matrix()
        print(f'R1 :\n{np.round(R1, 3)}')
        
        # R2: Rotation around Z-axis
        R2 = Rot.from_euler('z', beta).as_matrix()
        print(f'R2 :\n{np.round(R2, 3)}')

        # Combined rotation
        R_combined = R2 @ R1

        # Compute error as Frobenius norm
        error = np.linalg.norm(R_final - R_combined, ord='fro')
        print(f'RF :\n{np.round(R_final, 3)}')
        print(f'RC :\n{np.round(R_combined, 3)}')
        return error

    initial_guess = [0, 0]

    result = opt.minimize(error_function, initial_guess)
    alpha, beta = result.x % (2*np.pi)

    return alpha, beta


if __name__ == "__main__":
    get_top_cam_angles(90, 0, 89)

""" # Initial guess for theta1 and beta
  # Start with 0 degrees for both rotations

# Solve the optimization problem


# Reconstruct the rotations
R1_optimal = R.from_rotvec(optimal_theta1 * u1).as_matrix()
R2_optimal = R.from_euler('z', optimal_theta2, degrees=True).as_matrix()
R_combined_optimal = R2_optimal @ R1_optimal

# Print results
print("Optimal Angles:")
print(f"R1 (around custom axis at {np.degrees(alpha)}° with Y): {np.degrees(optimal_theta1)} degrees")
print(f"R2 (around Z-axis): {optimal_theta2} degrees")

print("\nReconstructed R_final:")
print(R_combined_optimal)

print("\nOriginal R_final:")
print(R_final)

# Verify error
print("\nError:", np.linalg.norm(R_final - R_combined_optimal, ord='fro')) """
