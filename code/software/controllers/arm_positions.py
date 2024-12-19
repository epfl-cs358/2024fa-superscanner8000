import math

# Function to calculate the Euclidean distance between two points
def calculate_distance(start, end):
    return math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)

# Function to generate points for a line segment
def generate_line_points(N, start, end):
    points = []
    for i in range(N):
        t = i / N  # Normalize parameter t between 0 and 1
        x = round(start[0] + t * (end[0] - start[0]), 1)
        y = round(start[1] + t * (end[1] - start[1]), 1)
        points.append([x, y])
    return points

# Generate all points with the correct number based on segment lengths
def generate_path(N):
    all_points = []

    # Define the start and end points for each segment
    vertical_start = [-10, -2]
    vertical_end = [-10, 20]
    curve_start = [-10, 20]
    curve_end = [-40, 69]

    # Calculate the lengths of the segments
    vertical_length = calculate_distance(vertical_start, vertical_end)
    curve_length = calculate_distance(curve_start, curve_end)

    # Calculate the total length
    total_length = vertical_length + curve_length

    # Calculate the number of points for each segment based on their relative lengths
    vertical_points = int(round((vertical_length / total_length) * (N - 1))) + 1
    curve_points = (N - 1) - (vertical_points - 1)

    # 1. Generate vertical segment (-10, -10) to (-10, 20)
    vertical_segment = generate_line_points(vertical_points, vertical_start, vertical_end)
    all_points.extend(vertical_segment)
    all_points.pop()  # This removes the last point which is (-10, 20)

    # 2. Generate curve from (-10, 20) to (-40, 69)
    curve_segment = generate_line_points(curve_points, curve_start, curve_end)
    all_points.extend(curve_segment)

    # 3. Add the final point (0, 80)
    final_point = [0, 80]
    all_points.append(final_point)

    return all_points

if __name__ == "__main__":
    # Print all points
    path = generate_path(11)
    for point in path:
        print(f"x: {point[0]}, y: {point[1]}")