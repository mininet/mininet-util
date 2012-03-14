from helper import *
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', dest="port", default='5001')
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)

args = parser.parse_args()

def first(lst):
    return map(lambda e: e[0], lst)

def second(lst):
    return map(lambda e: e[1], lst)

"""
Sample line:
2.221032535 10.0.0.2:39815 10.0.0.1:5001 32 0x1a2a710c 0x1a2a387c 11 2147483647 14592 85
"""
def parse_file(f):
    times = defaultdict(list)
    cwnd = defaultdict(list)
    srtt = []
    for l in open(f).xreadlines():
        fields = l.strip().split(' ')
        if len(fields) != 10:
            break
        if fields[2].split(':')[1] != args.port:
            continue
        sport = int(fields[1].split(':')[1])
        times[sport].append(float(fields[0]))

        c = int(fields[6])
        cwnd[sport].append(c * 1480 / 1024.0)
        srtt.append(int(fields[-1]))
    return times, cwnd

added = defaultdict(int)
events = []

def plot_cwnds(ax):
    global events
    for f in args.files:
        times, cwnds = parse_file(f)
        for port in sorted(cwnds.keys()):
            t = times[port]
            cwnd = cwnds[port]

            events += zip(t, [port]*len(t), cwnd)
            ax.plot(t, cwnd)

    events.sort()
total_cwnd = 0
cwnd_time = []

min_total_cwnd = 10**10
max_total_cwnd = 0
interested = []

m.rc('figure', figsize=(16, 6))
fig = plt.figure()

axPlot = fig.add_subplot(1, 2, 1)
axHist = fig.add_subplot(1, 2, 2)
plot_cwnds(axPlot)

for (t,p,c) in events:
    if added[p]:
        total_cwnd -= added[p]
    total_cwnd += c
    cwnd_time.append((t, total_cwnd))
    added[p] = c
    if t > 20:
        interested.append(total_cwnd)
        min_total_cwnd = min(min_total_cwnd, total_cwnd)
        max_total_cwnd = max(max_total_cwnd, total_cwnd)

axPlot.axhline(y=min_total_cwnd, ls='--')
axPlot.axhline(y=max_total_cwnd, ls='--')
axPlot.text(10, min_total_cwnd - 20, "min total = %.2fKB" % min_total_cwnd)
axPlot.text(10, max_total_cwnd + 10, "max total = %.2fKB" % max_total_cwnd)

axPlot.plot(first(cwnd_time), second(cwnd_time), lw=2, label="$\sum_i W_i$")
axPlot.grid(True)
axPlot.legend()
axPlot.set_xlabel("seconds")
axPlot.set_ylabel("cwnd KB")

n, bins, patches = axHist.hist(interested, 50, normed=1, facecolor='green', alpha=0.75)

axHist.set_xlabel("bins (KB)")
axHist.set_ylabel("Fraction")

if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()
