from threading import Thread
import time


class Gui(Thread):
    def __init__(self, notes, gui, fps, name, length):
        Thread.__init__(self)
        self.notes = notes
        self.gui = gui
        self.running = True
        self.timecode = 0
        self.length = length
        self.name = name
        self.futurpart = None
        self.fps = fps

    def run(self):
        delta = 0.001
        total = delta
        while self.running:
            tnow = time.time()
            if self.gui:
                self.gui_handler(tnow, delta, total)
            delta = time.time() - tnow
            total += delta
            if self.fps:
                print("fps :", int(1 / delta))

    def gui_handler(self, tnow, delta, total):
        image = self.gui.image_base.copy()  # reset
        self.gui.particles.draw_particles(image, delta)
        for note in self.notes:
            if note.is_on:
                self.gui.particles.create_particles(self.gui.pos_list[note.id], note)
                self.gui.draw_note(image, self.gui.pos_list[note.id], note.channel)
        self.gui.draw_futurpart(image, self.futurpart, self.timecode, self.notes, tnow)
        self.gui.draw_player(image, self.length, self.timecode)
        if self.timecode < 2:
            y = self.timecode * (self.gui.PIANO_PIX_START / 2) / 2
            self.gui.print_text(
                self.name,
                image,
                int(self.gui.PIANO_X / 2 - len(self.name) * 7),
                int(y),
                alpha=1,
            )  # display title dropping from floor
        if self.timecode < 7 and self.timecode >= 2:
            self.gui.print_text(
                self.name,
                image,
                int(self.gui.PIANO_X / 2 - len(self.name) * 7),
                int(self.gui.PIANO_PIX_START / 2),
                alpha=1 - ((self.timecode - 2) / 5),
            )  # display title middle fading out
        timer_str = "{}:{:02d}/{}:{:02d}".format(
            int(self.timecode / 60),
            int(self.timecode % 60),
            int(self.length / 60),
            int(self.length % 60),
        )

        self.gui.print_text(
            timer_str, image, self.gui.PIANO_X - 130, 25,
        )  # display timer top right
        image = self.gui.cv2.resize(
            image, (self.gui.scx, self.gui.scy), interpolation=self.gui.cv2.INTER_CUBIC
        )
        self.gui.np.copyto(self.gui.windowArray, image.swapaxes(0, 1))
        self.gui.window.refresh()

    def set_timecode(self, timecode):
        self.timecode = timecode

    def set_futurpart(self, futurpart):
        self.futurpart = futurpart

    def terminate(self):
        self.running = False
        self.join()
