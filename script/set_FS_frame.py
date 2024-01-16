import pyvista as pv
import numpy as np
from scipy.interpolate import CubicSpline

def smooth_vectors(vectors, window_size=10, passes=1):
    """ Apply a simple smoothing filter to vectors multiple times. """
    smoothed_vectors = vectors.copy()
    for _ in range(passes):
        # Pad the vectors at the start and end
        pad_width = window_size // 2
        padded_vectors = np.pad(smoothed_vectors, ((pad_width, pad_width), (0, 0)), mode='edge')

        # Apply a uniform filter
        for i in range(len(smoothed_vectors)):
            smoothed_vectors[i] = np.mean(padded_vectors[i:i + window_size], axis=0)

        # Normalize the smoothed vectors
        norms = np.linalg.norm(smoothed_vectors, axis=1)
        smoothed_vectors = smoothed_vectors / norms[:, np.newaxis]

    return smoothed_vectors



def interpolate_line(points, num_points=None):
    points = np.array(points)
    # Use the number of original points if num_points is not specified
    if num_points is None:
        num_points = len(points)

    # Calculate the cumulative distance along the line to use as a parameter
    distance = np.cumsum(np.r_[0, np.linalg.norm(np.diff(points, axis=0), axis=1)])
    # Normalize distance to the range [0, 1]
    distance_normalized = distance / distance[-1]

    # Create a spline for each dimension
    spline_x = CubicSpline(distance_normalized, points[:, 0])
    spline_y = CubicSpline(distance_normalized, points[:, 1])
    spline_z = CubicSpline(distance_normalized, points[:, 2])

    # Interpolate points along the spline
    interpolated_distance = np.linspace(0, 1, num_points)
    interpolated_points = np.vstack((spline_x(interpolated_distance), 
                                     spline_y(interpolated_distance), 
                                     spline_z(interpolated_distance))).T

    return interpolated_points


def compute_tangent_vectors(interpolated_points):
    # Compute tangent vectors using finite differences
    tangents = np.diff(interpolated_points, axis=0)
    tangents = np.vstack((tangents, tangents[-1]))  # Ensure same number of tangents as points
    # Normalize the tangent vectors
    norms = np.linalg.norm(tangents, axis=1)
    tangents = tangents / norms[:, np.newaxis]
    tangents = smooth_vectors(tangents)  # Smooth the tangent vectors
    return tangents

def compute_MRF(tangents):
    normals = np.zeros_like(tangents)
    binormals = np.zeros_like(tangents)

    # Initialize the normal for the first point
    # Make sure this is orthogonal to the first tangent
    normals[0] = np.array([tangents[0][1], -tangents[0][0], 0])
    normals[0] /= np.linalg.norm(normals[0])

    # Compute the binormal for the first point
    binormals[0] = np.cross(tangents[0], normals[0])

    # Propagate the frame along the curve
    for i in range(1, len(tangents)):
        # Project the previous normal onto the plane orthogonal to the current tangent
        normals[i] = normals[i - 1] - np.dot(normals[i - 1], tangents[i]) * tangents[i]
        normals[i] /= np.linalg.norm(normals[i])

        # Compute the binormal as the cross product of tangent and normal
        binormals[i] = np.cross(tangents[i], normals[i])

    normals = smooth_vectors(normals)
    binormals = smooth_vectors(binormals)

    return normals, binormals

def compute_normal_vectors(tangents):
    # Use finite differences to approximate normal vectors
    normals = np.diff(tangents, axis=0)
    normals = np.vstack((normals, normals[-1]))  # Ensure same number of normals as tangents
    
    # Replace any zero vectors with NaN to avoid division by zero
    norms = np.linalg.norm(normals, axis=1)
    zeros = norms < 1e-6
    normals[zeros] = np.nan
    
    # Normalize the normal vectors, skipping any NaN entries
    normals = normals / norms[:, None]
    
    # Handle NaNs if there were any zero vectors
    normals[zeros] = [0, 0, 0]  # or any other placeholder for zero vectors

    normals = smooth_vectors(normals)  # Smooth the normal vectors
    return normals

def compute_binormal_vectors(tangents, normals):
    # Compute binormal vectors as the cross product of tangent and normal vectors
    binormals = np.cross(tangents, normals)
    # Normalize the binormal vectors
    norms = np.linalg.norm(binormals, axis=1)
    zeros = norms < 1e-6
    binormals[zeros] = np.nan
    binormals = binormals / norms[:, np.newaxis]
    binormals[zeros] = [0, 0, 0]  # or any other placeholder for zero vectors
    binormals = smooth_vectors(binormals)  # Smooth the binormal vectors
    return binormals

def draw_FS_frames(num_points=10, draw_tangent=True, draw_normal=True, draw_binormal=True):
    # Load the .vtp file
    line_model = pv.read("data/mesh/vascularmodel/0023_H_AO_MFS/sim/path.vtp")

    # Interpolate the line for smoothing
    interpolated_points = interpolate_line(line_model.points)

    # Compute tangent vectors for the interpolated points
    tangents = compute_tangent_vectors(interpolated_points)

    # Compute normal and binormal vectors for the interpolated points
    #normals = compute_normal_vectors(tangents)
    #binormals = compute_binormal_vectors(tangents, normals)

    # Compute the Frenet-Serret frame using the MRF algorithm
    normals, binormals = compute_MRF(tangents)

    # Create a plotter
    plotter = pv.Plotter()
    # Add the original line to the plotter
    plotter.add_mesh(line_model, color='blue', line_width=2)

    # Select random points from the interpolated line to display tangents
    random_indices = np.random.choice(len(interpolated_points), num_points, replace=False)

    # Add Frenet-Serret frames to the plotter for the random points
    for idx in random_indices:
        point = interpolated_points[idx]
        tangent = tangents[idx]
        normal = normals[idx]
        binormal = binormals[idx]
        
        # Draw the tangent vector
        if draw_tangent:
            plotter.add_arrows(point[np.newaxis], tangent[np.newaxis], color='green', mag=0.1)
        # Draw the normal vector
        if draw_normal:
            plotter.add_arrows(point[np.newaxis], normal[np.newaxis], color='red', mag=0.1)
        # Draw the binormal vector
        if draw_binormal:
            plotter.add_arrows(point[np.newaxis], binormal[np.newaxis], color='blue', mag=0.1)

    # Show the plotter
    plotter.show()

    return

if __name__ == "__main__":
    draw_FS_frames(num_points=689, draw_tangent=True, draw_normal=True, draw_binormal=True)

