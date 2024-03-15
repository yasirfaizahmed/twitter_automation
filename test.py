from patterns.patterns import timeout
import time


@timeout(2)
def fun():
	time.sleep(4)


fun()
