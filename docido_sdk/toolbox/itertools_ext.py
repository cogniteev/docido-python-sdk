def fxrange(start=1.0, stop=None, step=1.0):
    cur = start * 1.0
    while 1:
        if not stop or cur <= stop:
            yield cur
            cur += step
        else:
            yield stop
