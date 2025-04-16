import argparse

from src.L_Systems import _2D, _3D
from src import l_system_2d, l_system_3d


def main():
    """
    Parse command line arguments to run a 2D or 3D L-system simulation.

    Parameters
    ----------
    -d, --dimension : str
        Choose 2D or 3D simulation.
    lsystem : str
        The name of the L-system to run (e.g., gosper, dragon, etc.).
    -l, --list : bool
        List available L-systems.

    Returns
    -------
    None
    """

    parser = argparse.ArgumentParser(description="Run a 2D or 3D L-system simulation.")
    parser.add_argument("-d", "--dimension", choices=["2d", "3d"], help="Choose 2D or 3D simulation.")
    parser.add_argument("lsystem", nargs="?", help="The name of the L-system to run (e.g., gosper, dragon, etc.)")
    parser.add_argument("-l", "--list", action="store_true", help="List available L-systems.")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable L-Systems:")
        print("  2D:", ", ".join(_2D.available_2d.keys()))
        print("  3D:", ", ".join(_3D.available_3d.keys()))
        return

    if not args.lsystem:
        print("Please provide a lsystem name or use --list.")
        return

    if args.dimension == "2d":
        if args.lsystem not in _2D.available_2d:
            print(f"2D L-system '{args.lsystem}' not found.")
            return
        l_system_2d.run(_2D.available_2d[args.lsystem])

    elif args.dimension == "3d":
        if args.lsystem not in _3D.available_3d:
            print(f"3D L-system '{args.lsystem}' not found.")
            return
        print("Controls:")
        print("  ↑ / ↓ arrows  = rotate elevation")
        print("  t             = save rotating animation with transparent background")
        print("  s             = save rotating animation")
        print("Or you can drag around with your mouse")
        l_system_3d.run(_3D.available_3d[args.lsystem])


if __name__ == "__main__":
    main()
