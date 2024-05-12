from tests.tester import tests, load, Shared
import trio
import sys

repeat = 3
Shared.mul = repeat

load(*sys.argv[1].split('.')) if len(sys.argv) > 1 else load()

failed = []
succeeded = []

async def main():
    async with trio.open_nursery() as nurs:
        for test in tests:
            for _ in range(repeat):
                suc = await test.test(nurs)
                [failed, succeeded][suc].append(test)
        return

trio.run(main)

suc = len(succeeded)
fai = len(failed)
tot = suc + fai

print(f'''
Summary:
    succeeded: {suc}
    ({round(suc/tot*100, 1)}%, {suc}/{tot})
    failed:    {fai}
    ({round(fai/tot*100, 1)}%, {fai}/{tot})''' + (( ':\n        ' + '\n        '.join([f.lable for f in failed])) if failed else ''))

if fai:
    exit(1)