#!/usr/bin/python
# -*- coding: utf8 -*-


# 参考: https://automatetheboringstuff.com/chapter10/
import logging as log

# 配置用于调试的log对象
log.basicConfig(level=log.DEBUG, format=' %(asctime)s - %(levelname)s - '
	'%(thread)d - %(module)s - %(funcName)s - %(lineno)d - %(message)s')

import atexit
import signal as sig
import time   as t

from auto_check import AutoCheck

class AutoCheckService:

	def __init__(self):

		#sig.signal(sig.SIGINT,  self.__stop)
		#sig.signal(sig.SIGTERM, self.__stop)
		#
		#self.__stop_sig = False
		self.__ac       = AutoCheck()

		atexit.register(self.__ac.exit)

	#def __stop(self, signum, frame):
	#
	#	self.__stop_sig = True

	def start(self):

		log.info('C programming course auto check service starting...')

		while True:

			#if self.__stop_sig:
			#
			#	log.info('C programming course auto check service stoping...')
			#
			#	break

			self.__ac.run()

			t.sleep(60)

		log.info('C programming course auto check service down.')


if __name__ == '__main__':

	AutoCheckService().start()
