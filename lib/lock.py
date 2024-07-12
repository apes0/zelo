import trio


def alock(afn):
    # make a function globally lock if it has any running instance
    # its basically just a queue lol
    ev = trio.Event()
    i = 0

    async def runner(*a, **kwa):
        nonlocal ev, i

        oldEv = ev
        myEv = trio.Event()
        ev = myEv

        i += 1

        try:
            if i - 1:
                await oldEv.wait()

            await afn(*a, **kwa)
        except trio.Cancelled:
            pass  # we still need to get to the finishing code, otherwise, we break the whole lock because i isn't decreased

        myEv.set()
        i -= 1

    return runner


def calock(afn):
    # alock, but locks only on the class level, instead of globally
    evs = {}
    i = {}

    async def runner(self, *a, **kwa):
        nonlocal evs, i

        oldEv = evs.get(self, trio.Event())
        myEv = trio.Event()
        evs[self] = myEv

        i[self] = i.get(self, 0) + 1

        try:
            if i[self] - 1:
                await oldEv.wait()

            await afn(self, *a, **kwa)
        except trio.Cancelled:
            pass  # same as alock

        myEv.set()
        i[self] -= 1

    return runner
