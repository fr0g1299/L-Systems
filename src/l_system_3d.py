import os
from math import sin, cos, radians
import importlib
import random
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

DEGREES_TO_RADIANS = radians(1)


def save_rotation_animation(ax, fig, transparency, output_dir="frames_3D", steps=359):
    """
    Saves a series of frames representing a 3D rotation animation.

    Args:
        ax: The matplotlib 3D axis object to rotate.
        fig: The matplotlib figure object containing the axis.
        transparency: A boolean indicating whether the output frames should have a transparent background.
        output_dir (str): The directory where the frames will be saved. Defaults to "frames_3D".
        steps (int): The number of frames to be generated for the complete rotation. Defaults to 359.

    Creates:
        A series of PNG files in the specified output directory, each representing a frame of the animation.
        The elevation angle is incremented per frame to achieve a smooth rotation animation.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in tqdm(range(steps), desc="Saving frames", unit="frame"):
        elev = i * (360 / steps)
        ax.view_init(elev=elev, azim=0, roll=90)
        fig.canvas.draw()
        fig.savefig(
            f"{output_dir}/frame_{i:03d}.png",
            bbox_inches="tight",
            transparent=transparency,
        )

    print(f"Animation saved to {output_dir}")


def load_lsystem(name):
    """
    Loads a 3D L-system module by name.

    Args:
        name (str): The name of the L-system module to load.

    Returns:
        module: The loaded module containing the L-system's parameters.

    Raises:
        ImportError: If the module cannot be found.

    Notes:
        The module name is expected to be in the format "L-Systems/3D.<name>",
        and should be a valid Python module name.
    """

    module_path = f"L-Systems/3D.{name}"
    return importlib.import_module(module_path)


def generate_lsystem(axiom, rules, iterations):
    """
    Generates an L-system string based on the given axiom, rules, and number of iterations.

    Args:
        axiom (str): The initial string of the L-system.
        rules (dict): A dictionary mapping each character in the axiom to either a single character
            (deterministic rule) or a list of tuples containing a replacement character and a probability
            (probabilistic rule). The probabilities should be normalized to 1.0.
        iterations (int): The number of times to apply the rules to the axiom.

    Returns:
        str: The resulting L-system string after the specified number of iterations.

    Notes:
        The function will raise a ValueError if any of the rules have probabilities that do not add up to 1.0.
    """

    for _ in range(iterations):
        new_axiom = []
        for c in axiom:
            if c in rules:
                rule_set = rules[c]
                if isinstance(rule_set, list):  # Probabilistic rules
                    r = random.random()
                    cumulative_prob = 0
                    for replacement, prob in rule_set:
                        cumulative_prob += prob
                        if r <= cumulative_prob:
                            new_axiom.append(replacement)
                            break
                else:
                    new_axiom.append(rule_set)
            else:
                new_axiom.append(c)
        axiom = "".join(new_axiom)
    return axiom


def turtle_coords_3d(lsys, angle, step):
    """
    Converts an L-system string into a list of 3D coordinates using the turtle graphics
    interpretation.

    Args:
        lsys (str): The L-system string to convert.
        angle (float): The angle (in degrees) to turn left or right when encountering a "+" or "-"
            symbol.
        step (float): The length of each step forward when encountering an "F" symbol.

    Returns:
        list: A list of tuples containing the start and end coordinates of each line segment
            in the L-system, along with the depth of that segment (i.e. the number of times
            the "[" symbol has been encountered minus the number of times the "]" symbol has
            been encountered).
    """

    stack = []
    x, y, z = 0, 0, 0
    yaw, pitch = 90, 90  # starting upwards
    segments = []
    depth = 0

    for symbol in lsys:
        if symbol == "F":
            nx = x + step * sin(radians(pitch)) * cos(radians(yaw))
            ny = y + step * sin(radians(pitch)) * sin(radians(yaw))
            nz = z + step * cos(radians(pitch))
            segments.append(((x, y, z), (nx, ny, nz), depth))
            x, y, z = nx, ny, nz
        elif symbol == "+":
            yaw += angle
        elif symbol == "-":
            yaw -= angle
        elif symbol == "&":
            pitch += angle
        elif symbol == "^":
            pitch -= angle
        elif symbol == "[":
            stack.append((x, y, z, yaw, pitch, depth))
            depth += 1
        elif symbol == "]":
            x, y, z, yaw, pitch, depth = stack.pop()

    return segments


def plot_3d(segments, main_color, point_color, points):
    """
    Plots a 3D representation of an L-system using the provided segments.

    Args:
        segments (list): A list of tuples, where each tuple contains the start and end
                         coordinates of a line segment in 3D space, along with its depth.
        main_color (str): The color to use for the branches in the plot.
        point_color (str): The color to use for the leaf tips in the plot.
        points (bool): Whether to plot the points of the L-system.

    The function sets up a 3D plot and draws each segment with varying line widths based
    on their depth. It identifies leaf tips (end points not used as start points) and
    highlights them with a scatter plot. Axes limits are set to provide an equal aspect
    ratio centered around the midpoint of all points. The plot's initial view is set with
    specific elevation, azimuth, and roll angles. It also includes keyboard interaction
    for rotating the view, and saving animations.
    """

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    start_points = set()
    end_points = []

    max_depth = max((segment[2] for segment in segments), default=1)

    all_coords = []

    for start, end, depth in segments:
        xs, ys, zs = zip(start, end)
        line_width = 1.5 + (max_depth - depth) * 0.5
        ax.plot(xs, ys, zs, color=main_color, linewidth=line_width)
        start_points.add(start)
        end_points.append(end)
        all_coords.extend([start, end])

    if points:
        leaf_tips = [pt for pt in end_points if pt not in start_points]
        if leaf_tips:
            xs, ys, zs = zip(*leaf_tips)
            ax.scatter(xs, ys, zs, color=point_color, s=20)

    # Gather all 3D points
    all_points = [p for segment in segments for p in segment[:2]]
    all_points = np.array(all_points)

    # Compute the midpoint and maximum span
    mid = all_points.mean(axis=0)
    max_range = (all_points.max(axis=0) - all_points.min(axis=0)).max() / 2

    # Set equal limits for all axes centered at midpoint
    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    ax.set_axis_off()

    # Set initial elevation and azimuth
    ax.view_init(elev=45, azim=-5, roll=85)

    plt.rcParams["keymap.save"] = []

    def on_key(event):
        if event.key == "up":
            ax.view_init(elev=ax.elev - 5, roll=90, azim=0)
        elif event.key == "down":
            ax.view_init(elev=ax.elev + 5, roll=90, azim=0)
        elif event.key == "t":
            save_rotation_animation(ax, fig, True)
        elif event.key == "s":
            save_rotation_animation(ax, fig, False)
        fig.canvas.draw()

    fig.canvas.mpl_connect("key_press_event", on_key)

    fig.patch.set_facecolor("#1f1f1f")
    ax.set_facecolor("#1f1f1f")

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    plt.show()


def run(lsys_module):
    """
    Given a module with L-system parameters, generate the 3D turtle
    coordinates and plot them.

    Parameters
    ----------
    lsys_module : module
        Module with the following attributes:
        - axiom : str
            The initial string of the L-system.
        - rules : dict
            Mapping from symbols to a list of strings and probabilities.
        - iterations : int
            Number of iterations to run the L-system.
        - angle : float
            Angle of rotation in degrees.
        - step : float
            Step size for the turtle.
        - main_color : str
            Color of the branches, in hex format.
        - point_color : str
            Color of the leaves, in hex format.
        - points : bool, optional
            Whether to plot the points of the L-system.
    """

    axiom = lsys_module.axiom
    rules = lsys_module.rules
    iterations = lsys_module.iterations
    angle = lsys_module.angle
    step = lsys_module.step
    main_color = lsys_module.main_color
    point_color = lsys_module.point_color
    points = getattr(lsys_module, "points", False)

    lsys = generate_lsystem(axiom, rules, iterations)
    segments = turtle_coords_3d(lsys, angle, step)

    plot_3d(segments, main_color, point_color, points)
