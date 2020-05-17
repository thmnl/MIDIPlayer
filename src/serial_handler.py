from threading import Thread
import time
import serial
import logger

""" """


class SerialHandler(Thread):
    def __init__(self, notes, serial_port, baudrate):
        Thread.__init__(self)
        self.running = True
        self.notes = notes
        try:
            self.serial = serial.Serial(serial_port, baudrate, timeout=0.1)
        except (serial.serialutil.SerialException, ValueError) as e:
            self.serial = None
            logger.my_logger.error("Serial init", e)

    def run(self):
        delta = 0.01
        time.sleep(2)  # wait for init
        while self.running and self.serial:
            tnow = time.time()
            lst = []
            for note in self.notes:
                lst.append(note.is_on)
            barray = bytearray([])
            chunks = self.split_lst(lst, 8)
            for chunk in chunks:
                s = ""
                for bool in chunk:
                    s += "1" if bool else "0"
                barray.append(int(s, 2))
            self.serial.write(barray)
            time.sleep(0.01)
            delta = time.time() - tnow

    def split_lst(self, lst, n):
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    def terminate(self):
        self.running = False
        self.join()
