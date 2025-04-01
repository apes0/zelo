import sys
from logging import DEBUG

import coverage
import trio
from junit_xml import TestCase, TestSuite

from lib.debcfg import cfg, logger
from tests.tester import Test, load, tests

# for c in cfg:
#    cfg[c] = False

# logger.setLevel(DEBUG)

# cfg['events'] = True

repeat = 3

junit = False
if sys.argv[-1] == '--junit':
    junit = True
    sys.argv.pop()

load(*sys.argv[1].split('.')) if len(sys.argv) > 1 else load(igndirs=['broken'])

res = []
# has this tuple (test, success?, time we took, error)


async def run(test: Test, nurs: trio.Nursery):
    t = trio.current_time()
    suc, err = await test.test(nurs)
    t = trio.current_time() - t
    res.append((test, suc, t, err))


# async def a(nurs):
#     while len(nurs.child_tasks) > 1:
#         print(nurs.child_tasks, len(nurs.child_tasks))
#         await trio.sleep(2.5)


async def main():
    cov = coverage.Coverage()
    cov.start()

    for test in tests:
        async with trio.open_nursery() as nurs:
            #            nurs.start_soon(a, nurs)
            for _ in range(repeat):
                nurs.start_soon(run, test, nurs)

    cov.stop()
    cov.save()


trio.run(main)

if junit:
    path = 'junit/test-results.xml'
    suits = {}
    for test, suc, t, err in res:
        sname = test.sname
        if sname not in suits:
            suits[sname] = TestSuite(sname)

        tcase = TestCase(name=test._lable, elapsed_sec=t)

        # TODO: logging
        if not suc:
            tcase.add_failure_info(f'encountered {err}')

        suits[sname].test_cases.append(tcase)

    open(path, 'w').write(TestSuite.to_xml_string(suits.values()))
else:
    succeeded = [test for (test, suc, _, _) in res if suc]
    failed = [test for (test, suc, _, _) in res if not suc]
    suc = len(succeeded)
    fai = len(failed)
    tot = suc + fai
    print(
        f'''
    Summary:
        succeeded: {suc}
        ({round(suc/tot*100, 1)}%, {suc}/{tot})
        failed:    {fai}
        ({round(fai/tot*100, 1)}%, {fai}/{tot})'''
        + (
            (':\n        ' + '\n        '.join([f.lable for f in failed]))
            if failed
            else ''
        )
    )
