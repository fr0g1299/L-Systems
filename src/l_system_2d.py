import importlib
from math import sin, cos, radians
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection

DEGREES_TO_RADIANS = radians(1)


def load_lsystem(name):
    """
    Loads an L-system module by name.

    Args:
        name (str): The name of the L-system module to load.

    Returns:
        module: The loaded module containing the L-system's parameters.

    Raises:
        ImportError: If the module cannot be found.

    Notes:
        The module name is expected to be in the format "L-Systems/<name>",
        and should be a valid Python module name.
    """

    module_path = f"L-Systems.{name}"
    lsys = importlib.import_module(module_path)
    return lsys


def turtle_coords(lsys, angle, step, starting_rotation, symbol_colors=None):
    """
    Converts an L-system string into a list of 2D line segments and their corresponding colors using turtle graphics.

    Args:
        lsys (str): The L-system string to interpret.
        angle (float): The angle in degrees to turn left or right for '+' or '-' symbols.
        step (float): The distance to move forward for each 'F' or similar symbol.
        starting_rotation (float): The initial rotation angle in degrees.
        symbol_colors (dict, optional): A mapping of symbols to their corresponding colors.

    Returns:
        tuple: A tuple containing:
            - segments (list of tuples): A list of line segments, each defined by start and end 2D coordinates.
            - colors (list of str): A list of colors for each segment, based on the symbol_colors mapping.
    """

    stack = []
    x, y, a = 0, 0, starting_rotation
    segments = []
    colors = []

    for symbol in lsys:
        if symbol.isalpha():  # Only draw for letters
            nx = x + step * cos(a * DEGREES_TO_RADIANS)
            ny = y + step * sin(a * DEGREES_TO_RADIANS)
            segments.append([(x, y), (nx, ny)])

            # Choose color based on symbol if available
            if symbol_colors and symbol in symbol_colors:
                colors.append(symbol_colors[symbol])
            else:
                colors.append("white")  # Default fallback

            x, y = nx, ny
        elif symbol == "+":
            a += angle
        elif symbol == "-":
            a -= angle
        elif symbol == "[":
            stack.append((x, y, a))
        elif symbol == "]":
            x, y, a = stack.pop()

    return segments, colors


def animate_lsystem(segments, seg_colors, interval=1):
    """
    Animate a 2D L-system with matplotlib.

    Parameters
    ----------
    segments : list of lists of tuples
        Coordinates of each segment of the L-system
    seg_colors : list of str
        Colors for each segment of the L-system
    interval : int, optional
        Time interval between frames in milliseconds. Defaults to 1.

    Returns
    -------
    None
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    ax.axis("off")

    line_collection = LineCollection([], linewidths=2)
    ax.add_collection(line_collection)

    x_vals = [pt[0] for seg in segments for pt in seg]
    y_vals = [pt[1] for seg in segments for pt in seg]
    margin = 10
    ax.set_xlim(min(x_vals) - margin, max(x_vals) + margin)
    ax.set_ylim(min(y_vals) - margin, max(y_vals) + margin)

    drawn_segments = []
    drawn_colors = []

    def update(i):
        drawn_segments.append(segments[i])
        drawn_colors.append(seg_colors[i])
        line_collection.set_segments(drawn_segments)
        line_collection.set_colors(drawn_colors)
        return (line_collection,)

    _ani = animation.FuncAnimation(fig, update, frames=len(segments), interval=interval, blit=True, repeat=False)

    fig.patch.set_facecolor("#1f1f1f")
    ax.set_facecolor("#1f1f1f")

    plt.show()


def run(lsys_module):
    """
    Execute the L-system generation and animation process using provided module parameters.

    Parameters
    ----------
    lsys_module : module
        A module containing the following attributes:
        - axiom : str
            The initial string of the L-system.
        - rules : dict
            A dictionary mapping symbols to their replacement strings.
        - iterations : int
            The number of iterations to apply the rules on the axiom.
        - angle : float
            The rotation angle in degrees for interpreting the L-system.
        - step : float
            The step size for each movement in the turtle graphic.
        - starting_rotation : float, optional
            The initial rotation angle in degrees. Defaults to 90.
        - colors : dict, optional
            A mapping of symbols to their corresponding colors for rendering.
    """

    axiom = lsys_module.axiom
    rules = lsys_module.rules
    iterations = lsys_module.iterations
    angle = lsys_module.angle
    step = lsys_module.step
    starting_rotation = getattr(lsys_module, "starting_rotation", 90)

    # Generate L-system string
    lsys = axiom
    for _ in range(iterations):
        lsys = "".join(rules.get(c, c) for c in lsys)

    # Try: generate_spectrum_colors() or use colors dictionary
    if hasattr(lsys_module, "generate_spectrum_colors"):
        segments = turtle_coords(lsys, angle, step, starting_rotation)[0]
        seg_colors = lsys_module.generate_spectrum_colors(len(segments))
    else:
        symbol_colors = getattr(lsys_module, "colors", None)
        segments, seg_colors = turtle_coords(lsys, angle, step, starting_rotation, symbol_colors)

    animate_lsystem(segments, seg_colors, interval=1)
