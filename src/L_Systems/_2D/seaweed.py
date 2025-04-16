from matplotlib import cm

axiom = "F"
rules = {"F": "FF-[-F+F+F]+[+F-F-F]"}
angle = 22.5
iterations = 4
step = 5


def generate_spectrum_colors(num_segments):
    color_map = cm.get_cmap("hsv", num_segments)
    return [color_map(i) for i in range(num_segments)]
