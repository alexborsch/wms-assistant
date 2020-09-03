import sys
import time


def updt(total, progress):
    """
    Displays or updates a console progress bar.

    Original source: /questions/27978/python-progress-bar/205178#205178
    """
    barLength, status = 20, ""
    progress = float(progress) / float(total)
    if progress >= 1.:
        progress, status = 1, "\r\n"
    block = int(round(barLength * progress))
    text = "\r[{}] {:.0f}% {}".format(
        "#" * block + "-" * (barLength - block), round(progress * 100, 0),
        status)
    sys.stdout.write(text)
    sys.stdout.flush()


runs = 300
for run_num in range(runs):
    time.sleep(.1)
    updt(runs, run_num + 1)