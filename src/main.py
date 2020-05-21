import mido
import ft_argparse
import logger
import piano
import time
import sys
import part
import os
import serial_handler


def playing_loop(mid, p, port, gui, notes, t):
    length = p[-2]["time"]
    i = 0
    modif = 0
    tstart = time.time()
    paused = False
    while p[i]:
        tnow = time.time()
        if gui:
            #  flush the event on the main loop, you can't do it in the thread
            # if the player bar is clicked to change the moment of the music
            # i and modif will be changed and notes playuntil will be set to 0
            modif, i, paused = gui.get_events(p, i, length, modif, notes, port, paused)
            t.set_futurpart(part.get_futur_partition(p, i, gui.FUTUR_PART_TIME))
            t.set_timecode(tnow + modif - tstart)
        if tnow + modif > p[i]["time"] + tstart:
            logger.my_logger.debug(p[i])
            if p[i]["msg"].type == "note_on" and not p[i]["note_off"]:
                notes[p[i]["msg"].note - 21].playuntil = (
                    tnow + p[i]["new_velocity"] / 10
                )
                notes[p[i]["msg"].note - 21].velocity = p[i]["new_velocity"]
                notes[p[i]["msg"].note - 21].channel = p[i]["msg"].channel
            if port:
                port.send(p[i]["msg"])
            i += 1
            continue
        wait_time = p[i]["time"] + tstart - (tnow + modif)
        if wait_time > 0.01:
            time.sleep(0.01)
        if paused:
            modif -= time.time() - tnow


def get_port(args):
    if args.list_port:
        print(mido.get_output_names())
        sys.exit(0)
    if args.no_port:
        return None
    try:
        if args.port == "default":
            port = mido.open_output(mido.get_output_names()[0])
        else:
            port = mido.open_output(args.port)
    except IOError:
        logger.my_logger.error("Unknown port", args.port)
        return None
    except IndexError:
        logger.my_logger.error("No default port available")
        return None
    return port


def create_thread(f, *args):
    t = f(*args)
    t.daemon = True
    t.start()
    return t


def main():
    args = ft_argparse.get_args()
    logger.init(args)
    port = get_port(args)
    notes = []
    for n in range(0, 88):
        notes.append(piano.Note(n))
    gui = None
    if not args.no_gui:
        import gui_functions  # import the lib only if gui is specified

        gui = gui_functions
        gui.init(
            args.background_image,
            args.background_transparency,
            args.window_size,
            args.borderless,
        )
        gui.particles.init(
            args.no_particles, args.particles_texture,
        )
    threads = []
    threads.append(create_thread(piano.Piano, notes))
    if args.serial:
        threads.append(
            create_thread(
                serial_handler.SerialHandler, notes, args.serial, args.baudrate
            )
        )
    for midifile in args.midifiles:
        try:
            mid = mido.MidiFile(midifile)
            filename, _ = os.path.splitext(os.path.split(midifile)[1])
            name = filename if mid.tracks[0].name == "" else mid.tracks[0].name
        except (OSError, EOFError) as e:
            logger.my_logger.error("with file", midifile, e)
            continue
        partition, length = part.get_partition(mid, name)
        t = None
        if gui:
            t = create_thread(gui.gui_handler.Gui, notes, gui, args.fps, name, length)
        playing_loop(mid, partition, port, gui, notes, t)
        if gui:
            t.terminate()
    for thread in threads:
        thread.terminate()


if __name__ == "__main__":

    main()
