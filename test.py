# flake8: noqa


from patterns.patterns import timeout
import time


class p:
	def p_fun(self):
		pass


class c(p):
	@timeout(2)
	def p_fun(self):
		time.sleep(5)


c().p_fun()
