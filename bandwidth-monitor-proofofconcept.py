#!/usr/bin/env python


import time
import random
from nodebox import graphics as nb
import math


last_bytes = -1
last_sample = time.time()
samples = []
slowsamples = []
FIRST = 200
HEIGHT = 1200
WIDTH = 100

def draw(canvas):
    collect_sample()
    
    canvas.clear()

    first = samples[0][0]
    last = samples[-1][0]
    delta = last - first
    if delta == 0.0:
        return
    
    perpixel = HEIGHT / delta

    samps = []
    for (tm,rb) in samples:
        samps.append(rb / tm)

    max = samps[0]
    average = samps[0]
    for rb in samps[1:101]:
        #average = (average + rb) / 2.0
        average += rb
    for rb in samps:
        if rb > max:
            max = rb
    average = average / float(len(samps))
            
    for (tm,mn,mx,avg,stddev) in slowsamples:
        if avg > max:
            max = avg

    if max == 0:
        return

    xrng = float(max) / WIDTH
    nb.stroke(.5,0,0)
    nb.fill(1,0,0)
    y = HEIGHT
    samps.reverse()
    for rb in samps[:FIRST]:
        if rb != 0:
            x = (float(rb)/max) * WIDTH
            if x > WIDTH:
                print "ERR",x
            nb.stroke(1,0,0)
            nb.line(0, y, x, y)
            nb.stroke(0,0,0)
            nb.line(x-1, y, x, y)
        y = y - 1
#    path.lineto(0,y)
#    path.lineto(0,HEIGHT)
#    path.closepath()
#    nb.drawpath(path)

    nb.stroke(0,0,1)
    if False:
        x0 = 0
        for i in range(10,FIRST,10):
            if i >= len(samps):
                break
            avg = 0
            for x in range(i-10,i):
                avg = avg + samps[i]
            avg = avg / 10.0
            x1 = (avg/max) * WIDTH
            nb.line(x0, HEIGHT-i-10, x1, HEIGHT-i)
            x0 = x1
            
    else:
        x1 = (average/max) * WIDTH
        nb.line(x1, HEIGHT, x1, HEIGHT-100)
    

    i = 0
    rbtot = 0
    lasttm = tm

    if False:
        ## this plots a red bar +- one std-deviation with a black bar
        ## for the average
        y = HEIGHT - FIRST - len(slowsamples)
        for (tm,mn,mx,avg,stddev) in slowsamples:
            pxdev = (stddev/max) * WIDTH
            x0 = (float(avg)/max) * WIDTH
            nb.stroke(1,0,0)
            nb.line(x0-pxdev, y, x0+pxdev, y)
            nb.stroke(0,0,0)
            nb.line(x0-1,y,x0+1,y)
            y = y + 1

    elif False:
        ## this plots a red bar between min and max and a black dot for average
        ## (commented code does that, current does line from avg->max)
        y = HEIGHT - FIRST - len(slowsamples)
        for (tm,mn,mx,avg,stddev) in slowsamples:
            x0 = (float(mn)/max) * WIDTH
            x1 = (float(mx)/max) * WIDTH
            x2 = (float(avg)/max) * WIDTH
            nb.stroke(1,0,0)
            nb.line(x2, y, x1, y)
            #nb.stroke(0,0,0)
            #nb.line(x2-1,y,x2+1,y)
            y = y + 1

    elif True:
        ## this just plots the average
        y = HEIGHT - FIRST - len(slowsamples)
        for (tm,mn,mx,avg,stddev) in slowsamples:
            x = (float(avg)/max) * WIDTH
            nb.stroke(1,0,0)
            nb.line(0, y, x, y)
#            nb.stroke(0,0,0)
#            nb.line(x-1,y,x,y)
            y = y + 1

    nb.fontsize(10)
    
    for i in range(0,FIRST+1,50):
        nb.stroke(0,0,0,0.5)
        nb.line(0, HEIGHT-i, WIDTH-22, HEIGHT-i)
        t = nb.Text("%ds"%(i/10), WIDTH-20, HEIGHT-i-4)
        nb.stroke(0,1,0)
        t.draw()
        
    for i in range(FIRST+50,HEIGHT,50):
        nb.stroke(0,0,0,0.5)
        nb.line(0, HEIGHT-i, WIDTH-32, HEIGHT-i)
        t = nb.Text("%ds"%((FIRST/10)+((i-FIRST))), WIDTH-30, HEIGHT-i-4)
        nb.stroke(0,0,1)
        t.draw()

#    nb.fill(0,0,0,.8)
#    t = nb.Text("max: " + str(max), 0, HEIGHT-50)
#    t.fontweight = nb.BOLD
#    t.draw()

    nb.fill(0,0,1,.8)
    x1 = (average/max) * WIDTH
    average = int(average)
    avgtext = str(average/1024) + " KiB/s"
    t = nb.Text(avgtext, x1+2, HEIGHT-12)
    t.fontweight = nb.BOLD
    t.draw()
        
        
def collect_sample():
    global last_bytes, samples, slowsamples, last_sample

    if False:
        s = random.randrange(10,1000)
        if len(slowsamples) == 4:
            s = 1600
        samples.insert(0, (time.time(), s))

    else:
        tm = time.time()
        if tm - last_sample < 0.05:
            return
        
        for line in open('/proc/net/dev','r').readlines():
            if 'eth0' in line[:10]:
                fields = line.split(':')[1].split()
                bytes_read = int(fields[0])
                #packets_read = fields[1]
                #bytes_written = fields[8]
                #packets_written = fields[9]
                #print bytes_read, packets_read, bytes_written, packets_written

                if last_bytes < 0:
                    last_bytes = bytes_read
                    last_sample = tm
                    return

                rb = bytes_read - last_bytes
                samples.append( (tm-last_sample, rb) )

                last_bytes = bytes_read
                last_sample = tm

    sz = len(samples)-FIRST
    if sz > 10:
        mn = samples[0][1]
        mx = samples[0][1]
        tot = samples[0][1]
        tmdelta = 0.0
        for (t, x) in samples[1:sz]:
            tmdelta += t
            if x < mn:
                mn = x
            if x > mx:
                mx = x
            tot = tot + x

        avg = tot/tmdelta
        stddev = 0.0
        for (t, x) in samples[0:sz]:
            stddev = stddev + ((x - avg) ** 2)
        stddev = stddev / sz
        stddev = math.sqrt(stddev)
            
        slowsamples.append((tmdelta, mn, mx, avg, stddev))
        samples = samples[sz:]
        if len(slowsamples) > (HEIGHT-FIRST):
            slowsamples = slowsamples[len(slowsamples) - (HEIGHT-FIRST):]

collect_sample()
time.sleep(0.05)
collect_sample()
samples = []

nb.fps = 5
nb.canvas.size = WIDTH, HEIGHT
nb.canvas.run(draw)
            
