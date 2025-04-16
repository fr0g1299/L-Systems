from matplotlib import cm

axiom = "L"
rules = {"L": "L+R++R-L--LL-R+", "R": "-L+RR++R+L--L-R"}
angle = 60
iterations = 4
step = 5


def generate_spectrum_colors(num_segments):
    color_map = cm.get_cmap("hsv", num_segments)
    return [color_map(i) for i in range(num_segments)]
