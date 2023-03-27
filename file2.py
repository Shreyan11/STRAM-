import pyqtgraph as pg
import numpy as np
from PyQt5.QtCore import QTimer, Qt, QEvent, QObject, QCoreApplication
from PyQt5.QtGui import QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QApplication
import sys
import os

zz = int(sys.argv[1])
# print(zz)

selected_channels = [int(arg) for arg in sys.argv[2:]]
# with open('settings.txt', 'r') as f:
#     lines = f.readlines()
#     b = int(lines[-1]) 
#     print(b)

count = 0
data = []

if zz != 2:
    raw = "raw.txt"
    print("Board 1")
else:
    raw = "raw2.txt"
    print("Board 2")

class MyPlotWidget(pg.PlotWidget, QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.installEventFilter(self)
        self.paused = False
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Space:
                self.paused = not self.paused
        return False

app = pg.mkQApp()
win = MyPlotWidget()
win.show()
# win.setWindowTitle()

legend = win.addLegend()
curves = []

for i, channel in enumerate(selected_channels):
    curve = win.plot(pen=pg.intColor(i), name=f'Channel {channel}')
    curves.append(curve)
    # legend.addItem(curve, f'Channel {channel}')

grid = pg.GridItem()
win.addItem(grid)

def read_data():
    global count, data
    with open(raw, 'r') as f:
        f.seek(0, os.SEEK_END) # move the file pointer to the end of the file
        size = f.tell() # get the current position of the file pointer
        
        # If the file size is less than or equal to the previous file size, return
        if size <= count:
            return
        
        # Otherwise, read the new data starting from the previous file size
        f.seek(count)
        for line in f:
            line = line.strip().split(',')
            line = [x for x in line if x != '']

            try:
                m = np.array(line, dtype=float)
                if m.size == 19:
                    data.append(m)
            except Exception as e:
                count += 1
                continue
                
        count = size # update the file size

# timer = QTimer()
# timer.timeout.connect(read_data)
# timer.start(100) # read data every 100 ms

def update():
    global data, curves, win
    if win.paused or not data:
        return

    arr = np.vstack(data)
    # x_min, x_max = win.viewRange()[0]
    # x_max = max(x_max, len(arr))
    # win.setXRange(max(0, x_max - 1000), x_max)

    for j, curve in enumerate(curves):
        channel_data = arr[:, np.array(selected_channels[j]) - 1]
        curve.setData(channel_data)
    
timer_plot = QTimer()
timer_plot.timeout.connect(update)
timer_plot.timeout.connect(read_data)
timer_plot.start(1) 


if __name__ == '__main__':
    if sys.flags.interactive != 1:
        QApplication.instance().exec_()
