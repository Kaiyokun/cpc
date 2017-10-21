#!/usr/bin/python
# -*- coding: UTF-8 -*-


# 参考: https://automatetheboringstuff.com/chapter10/
import logging as log

# 配置用于调试的log对象
log.basicConfig(level=log.DEBUG, format=' %(asctime)s - %(levelname)s - '
	'%(thread)d - %(module)s - %(funcName)s - %(lineno)d - %(message)s')

import mimetypes as mime
import os
import pyzmail   as smtp # http://www.magiksys.net/pyzmail/

from datetime   import datetime
from imapclient import IMAPClient # http://imapclient.readthedocs.org/
from threading  import Timer, Lock
from util       import Util

class Mail:

	@staticmethod
	def __add_attachments(file_list):

		# 附件list
		attachments = []

		# 如果file_list是单个文件名则将其包装为list
		# 否则作为文件名list处理
		for file_name in [file_list
			] if isinstance(file_list, str) else file_list:

			mime_main_type, mime_sub_type = mime.guess_type(
				file_name)[0].split('/')

			with open(file_name, 'rb') as file:

				attachments += [(
					file.read(),
					mime_main_type,
					mime_sub_type,
					os.path.basename(file_name),
					'UTF-8')]

		return attachments

	def __init__(self, conf_file_name):

		# 清空imap对象
		self.imap = None

		# 读取邮箱帐户以及imap和smtp的配置
		self.__conf = Util.read_conf_from_json(conf_file_name)

		# 构造lock对象
		self.__noop_mode_lock = Lock()

		# NOOP模式标识
		self.__noop_mode = False

	def __connect(self):

		if self.imap is not None:

			return

		# 建立imap连接, 使用ssl
		self.imap = IMAPClient(
			self.__conf['imap']['server'],
			self.__conf['imap']['port'],
			ssl=True)

		# 登录邮箱
		self.imap.login(
			self.__conf['profile']['account'],
			self.__conf['profile']['password'])

	def get_white_list(self):

		return self.__conf['auth_sender']

	def open_mailbox(self, readonly=False):

		self.__connect()

		# 默认以读写模式打开指定的邮箱文件夹
		self.imap.select_folder(self.__conf['imap']['folder'].decode('UTF-8'),
			readonly)

		# 返回self以支持链式操作
		return self

	def close_mailbox(self):

		if self.imap is None:

			return

		# 除非发生IMAPClientAbortError异常, 否则应该登出邮箱
		self.imap.logout()

		# 清空imap对象
		self.imap = None

	def get_today_unread(self):

		# 指定搜索条件(未读 + 今天)
		return self.imap.search(['UNSEEN', 'ON',
			# 获取今天的日期, 格式为day-month-year, 如: 30-Sep-2017
			datetime.now().strftime('%d-%b-%Y')])

	def get(self, *cond):

		return self.imap.search(cond)

	def fetch_header(self, uids):

		# 未读邮件摘要列表
		mail_digests = []

		# 获取邮件头信息
		for uid, envelope in self.imap.fetch(uids, ['ENVELOPE']).items():

			envelope = envelope['ENVELOPE']
			sender   = envelope.from_[0]

			# 摘要的dict, keys = (邮件UID, 收件日期, 邮件主题, 发件人, 消息ID)
			digest = {
				'uid':     uid,
				'date':    envelope.date,
				'subject': smtp.parse.decode_mail_header(envelope.subject)
					.encode('UTF-8'),
				'sender': (smtp.parse.decode_mail_header(sender.name)
					.encode('UTF-8'), sender.mailbox + '@' + sender.host),
				'msg_id':  envelope.message_id}

			log.info('Received mail(uid: <%d>)\n'
				'date: <%s>\n'
				'sub:  <%s>\n'
				'who:  <%s: %s>\n'
				%(uid,
				envelope.date,
				digest['subject'],
				digest['sender'][0], digest['sender'][1]))

			# 添加到邮件摘要队列
			mail_digests += [digest]

		return mail_digests

	def mark_as_read(self, uid):

		self.imap.add_flags(uid, '\\SEEN')

	def mark_as_unread(self, uid):

		self.imap.remove_flags(uid, '\\SEEN')

	def mark_as_answered(self, uid):

		self.imap.add_flags(uid, '\\ANSWERED')

	def star_message(self, uid):

		self.imap.add_flags(uid, '\\FLAGGED')

	def fetch_body(self, uid):

		# 读取邮件正文
		return smtp.PyzMessage.factory(
			self.imap.fetch(uid, ['BODY[]'])[uid]['BODY[]'])

	def enter_noop_mode(self):

		if self.__noop_mode:

			return

		def keep_imap_alive():

			# 对self.__noop_mode的读取加锁
			self.__noop_mode_lock.acquire()

			# 如果当前处于NOOP模式
			if self.__noop_mode:

				# 向imap服务器发送NOOP指令
				self.imap.noop()

				# 15秒以后再次执行
				Timer(15, keep_imap_alive).start()

			# 释放锁
			self.__noop_mode_lock.release()

		# 将NOOP模式标识打开
		self.__noop_mode = True

		# 进入NOOP模式
		keep_imap_alive()

	def quit_noop_mode(self):

		# 对self.__noop_mode的写入加锁
		self.__noop_mode_lock.acquire()

		# 将NOOP模式标识关闭(退出NOOP模式)
		self.__noop_mode = False

		# 释放锁
		self.__noop_mode_lock.release()

	def wait_new_mail(self, timeout=None):

		# 将imap服务器设置为IDLE模式(消息推送模式)
		self.imap.idle()

		log.info('Waiting for a new mail...')

		# 等待消息推送
		msg = self.imap.idle_check(timeout)

		# 退出IDLE模式
		self.imap.idle_done()

		# 等待消息超时
		if not msg:

			log.info('Wait timeout.')

			return False

		log.info('Maybe a new mail has arrived?')

		# 已获得消息推送
		return True

	def send(self, mail_header, text='', html=None, file_list=None):

		# 构造邮件
		payload, mail_from, rcpt_to, msg_id = smtp.compose_mail(
			(self.__conf['profile']['name'], self.__conf['profile']['mailbox']),
			mail_header['recipients'],
			mail_header['subject'],
			'UTF-8',
			(text, 'UTF-8'),
			None if html      is None else (html, 'UTF-8'),
			[]   if file_list is None else Mail.__add_attachments(file_list),
			headers=mail_header['others'] if mail_header.has_key('others')
				else [])

		# 发送邮件
		ret = smtp.send_mail(
			payload,
			mail_from,
			rcpt_to,
			self.__conf['smtp']['server'],
			self.__conf['smtp']['port'],
			self.__conf['smtp']['mode'],
			self.__conf['profile']['account'],
			self.__conf['profile']['password'])

		# 发生错误
		if not isinstance(ret, dict):

			log.error('Send error: ' + ret)

			return False

		else:

			# 发送至某些收件人失败
			if ret:

				log.warning('Failed recipients: ')

				for recipient, (code, msg) in ret.iteritems():

					log.warning('code: %d recipient: %s error: %s', code,
						recipient, msg)

				return False

			# 发送成功
			log.info('Send to %s success.' %(rcpt_to))

			return True

	def reply(self, mail_digest, subject=None, text='', html=None,
		file_list=None):

		return self.send({
			'recipients': [mail_digest['sender']],
			'subject':     subject if subject is not None else
				'回复: ' + mail_digest['subject'],
			'others':     [
				('IN-REPLY-TO', mail_digest['msg_id']),
				('REFERENCES',  mail_digest['msg_id'])]},
			text,
			html,
			file_list)
