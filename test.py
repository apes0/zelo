from tests.tester import tests, Test, load

load()

test: Test
for test in tests:
    test.test()
    if test.success:
        print(f'{test.lable} succeeded!')
