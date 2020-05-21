import argparse


def get_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("midifiles", nargs="*")
    ## GUI
    parser.add_argument(
        "--no_gui", action="store_true", help="No graphical outpup",
    )
    # Particles
    parser.add_argument(
        "--no_particles", action="store_true", help="No particles",
    )
    parser.add_argument(
        "--particles_texture", default="dot", help="dot/note/circle/square/star",
    )
    # Window configuration
    parser.add_argument(
        "--window_size", nargs="+", type=int, help="change the window size by value x y"
    )
    parser.add_argument(
        "--borderless", action="store_true", help="Remove border from the window"
    )
    # Background settings
    parser.add_argument("--background_image", default=None)
    parser.add_argument(
        "--background_transparency",
        default=0.6,
        type=float,
        help="background transparency from 0.0 (invisible) to 1.0 (fully visible)",
    )
    parser.add_argument(
        "--fps", action="store_true", help="Print frame per second on stdout",
    )
    ## Serial communication
    parser.add_argument(
        "--serial",
        default=None,
        help="Sending 88bits corresponding to notes to the specified serial port",
    )
    parser.add_argument(
        "--baudrate", default=9600, type=int, help="baudrate for serial communication",
    )
    ## Port MIDI
    parser.add_argument(
        "--list_port", action="store_true", help="List aviable port and exit",
    )
    parser.add_argument(
        "--no_port", action="store_true", help="no output port",
    )
    parser.add_argument(
        "-p",
        "--port",
        default="default",
        help="specify the output port, default will me the first port of the get_output_names() list",
    )
    return parser.parse_args()
