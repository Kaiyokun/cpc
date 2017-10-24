#!/usr/bin/python
# -*- coding: utf8 -*-


# 参考: https://automatetheboringstuff.com/chapter10/
import logging as log

# 配置用于调试的log对象
log.basicConfig(level=log.DEBUG, format=' %(asctime)s - %(levelname)s - '
	'%(thread)d - %(module)s - %(funcName)s - %(lineno)d - %(message)s')

import openpyxl   as xl
import os
import re
import shutil     as sh
import subprocess as sp
import time       as t

from mail import Mail
from util import Util

class AutoCheck:

	__subject_regex = re.compile(r'.*(cpc\s+.*)')

	@staticmethod
	def __set_dflt_arg(args, dflt_arg_name):

		if None in args:

			args[dflt_arg_name] = args.pop(None)

	def __load_tmplts(self, conf_file_name):

		# 读取邮件回复模板配置
		tmplt_list = Util.read_conf_from_json(self.root + conf_file_name)

		# 模板哈希表
		self.tmplts = {}

		# 模板名: 模板文件名
		for tmplt_name, tmplt_file_name in tmplt_list['tmplts'].items():

			self.tmplts[tmplt_name] = self.root + tmplt_list['folder'
				] + tmplt_file_name

	def __load_cmds(self, conf_file_name):

		# 读取指令集配置
		cmd_list = Util.read_conf_from_json(self.root + conf_file_name)

		# 指令集哈希表
		self.cmds = {}

		# 指令获取邮件内容标识
		self.cmd_fetch = {}

		# 指令集列表
		cmd_list_table = [[cmd_list['cmd_hdr'], cmd_list['args_hdr']]]

		for cmd in cmd_list['cmds']:

			# 将方法指针绑定到指令名上
			self.cmds[cmd['name']] = eval(cmd['method'])

			# 指令是否需要邮件内容
			self.cmd_fetch[cmd['name']] = cmd['fetch']

			# +---------------+--------------+
			# | 指令名 + 参数 | 指令参数说明 |
			# +---------------+--------------+
			cmd_list_table += [[' '.join(['cpc', cmd['name'], cmd['param']]),
				cmd['desc']]]

		# 指令集说明文档
		self.help_doc = Util.create_html_list(self.tmplts['list_container'],
			cmd_list_table, cmd_list['usage'])

	def __load_ex_list(self, conf_file_name):

		# 保存练习内容配置文件路径
		self.ex_conf_file_name = self.root + conf_file_name

		# 读取练习内容配置到内存
		self.ex_list = Util.read_conf_from_json(self.ex_conf_file_name)

	def __save_ex_list(self):

		# 保存练习内容配置到文件
		Util.write_conf_to_json(self.ex_list, self.ex_conf_file_name)

	def __load_stu_list(self, conf_file_name):

		# 学生花名册excel表格
		self.stu_list = Util.read_conf_from_excel(self.root + conf_file_name,
			ref=(2,1))

	def __init_mail_client(self, conf_file_name):

		# 邮件客户端
		self.mail = Mail(self.root + conf_file_name)

	def __load_ex_stat(self, stat_file_name):

		# 保存练习统计文件路径
		self.ex_stat_file_name = self.root + stat_file_name

		# 读取练习练习统计信息到内存
		with open(self.ex_stat_file_name, 'rb') as ex_stat_file:

			self.wb = xl.load_workbook(ex_stat_file)

	def __save_ex_stat(self):

		# 保存练习练习统计文件到文件
		self.wb.save(self.ex_stat_file_name)

	def __init__(self, root=os.getcwd() + '/'):

		# 项目文件根目录
		self.root = root

		# 加载配置文件
		self.__load_tmplts('./config/template_list.json')
		self.__load_cmds('./config/command_list.json')
		self.__load_ex_list('./config/exercise_list.json')
		self.__load_stu_list('./config/student_list.xlsx')

		# 初始化邮件客户端
		self.__init_mail_client('./config/mail_config.json')

		# 打开练习记录文件
		self.__load_ex_stat('./exercise_statistics.xlsx')

	def parse_cmd_line(self, cmd_line):

		try:

			# 用正则表达式匹配cpc及其之后的内容
			cmd_args = {
				'cmd_line': AutoCheck.__subject_regex.match(cmd_line).group(1)}

			# 以空格分割各参数
			argv = cmd_args['cmd_line'].split()

			# 获取指令对应函数的指针
			cmd_args['cmd']   = self.cmds[argv[1]]

			# 获取指令获取邮件内容的标识
			cmd_args['fetch'] = self.cmd_fetch[argv[1]]

		# AttributeError - 非法的命令行
		# KeyError       - 无效的<cmd>
		except (AttributeError, KeyError):

			return None

		# 之后的参数依次按key=value出现
		# 如果只有value则为默认参数, 只允许有1个
		dflt_arg_occur = False

		# 如果len(argv) < 3, 那么argv[2:]将返回[]
		for arg in argv[2:]:

			try:

				key, value = arg.split('=')

			except ValueError:

				# 默认参数, 只允许有1个
				if not dflt_arg_occur:

					dflt_arg_occur = True

					key   = None
					value = arg

				# 跳过没有指定key的参数
				else:

					continue

			cmd_args[key] = value

		return cmd_args

	def __reply(self, args, subject, text=None, html=None, file_list=None):

		# 获取邮件摘要
		mail_digest = args['mail_digest']

		# 邮件UID 发件时间 发件人 邮箱 主题 回复主题
		mail_record = [
			mail_digest['uid'],
			mail_digest['date'],
			mail_digest['sender'][0],
			mail_digest['sender'][1],
			mail_digest['subject'],
			subject]

		# 回复邮件
		if not self.mail.reply(mail_digest, subject, text, html, file_list):

			# 发送失败, 记录统计信息
			self.wb['mail_record'].append(mail_record + ['failed'])

			return False

		# 发送成功, 记录统计信息
		self.wb['mail_record'].append(mail_record + ['success'])

		return True

	def help(self, args, subject='邮件指令说明, 如: cpc get-ex-list'):

		self.__reply(args, subject, html=self.help_doc)

	def get_exer_list(self, args,
		subject='练习列表, 可获取练习内容: cpc get-ex ', list_text=''):

		self.__reply(args, subject,
			html=Util.create_html_list(
				self.tmplts['list_container'],
				[['作业编号', '说明']] + [[ex['id'], ex['brief']]
					for ex in self.ex_list['exs']],
				list_text))

	def __get_ex_info(self, args):

		try:

			# 获取练习信息索引
			ex_idx = [ex['id'] for ex in self.ex_list['exs']].index(args['eid'])

		except KeyError:

			raise KeyError('未提供作业编号')

		except ValueError:

			raise ValueError('无效的作业编号%s' %(args['eid']))

		return {
			'ex_idx':  ex_idx,
			'ex_info': self.ex_list['exs'][ex_idx]}

	def __get_stu_info(self, args):

		try:

			# 获取学生信息索引
			stu_idx = [stu['学号'] for stu in self.stu_list].index(args['sid'])

		except KeyError:

			raise KeyError('未提供学号')

		except ValueError:

			raise ValueError('无效的学号%s' %(args['sid']))

		return {
			'stu_idx':  stu_idx,
			'stu_info': self.stu_list[stu_idx]}

	def get_exer(self, args):

		# 设置默认参数eid
		AutoCheck.__set_dflt_arg(args, 'eid')

		try:

			ex_info = self.__get_ex_info(args)['ex_info']

			self.__reply(args, '已获取练习%s的内容, '
				'可提交: cpc commit-ex %s sid=' %(ex_info['id'], ex_info['id']),
				file_list=self.root + self.ex_list['folder'] + ex_info['src'])

		except (KeyError, ValueError) as err:

			self.get_exer_list(args, '获取练习内容请求无效, %s: %s'
				%(err[0], args['cmd_line']), '请在以下列表中重新选择:')

	def __valid_ex(self, args):

		try:

			ex_info  = self.__get_ex_info(args)['ex_info']
			stu_info = self.__get_stu_info(args)['stu_info']

			# 练习目录由 $root/ + source/ + 学号/ + ex_练习编号/ 构成
			src_dir = '%s/source/%s/ex_%s/' %(
				self.root, stu_info['学号'], ex_info['id'])

			# 防止重复创建目录
			if not os.path.exists(src_dir):

				os.makedirs(src_dir)

			# 提取练习代码

			# 先设定错误消息
			err_msg = '未找到代码附件'

			# 获取邮件主体
			mail_body = args['mail_body']

			# 遍历邮件附件
			for part in mail_body.mailparts:

				if part.filename is None:

					continue

				# 文件名转码为UTF-8
				file_name = part.filename.encode('UTF-8')

				# 检查扩展名
				if file_name.endswith('.c'):

					# 已找到代码
					err_msg = None

					# 保存代码到指定文件夹
					with open(src_dir + file_name, 'wb') as src:

						src.write(part.get_payload())

			# 未找到代码附件
			if err_msg is not None:

				raise ValueError(err_msg)

		except (KeyError, ValueError) as err:

			# subject, text, html, file_list
			raise RuntimeError('提交练习请求无效, %s:%s'
				%(err[0], args['cmd_line']), '', None, None)

		# 获取邮件摘要信息
		mail_digest = args['mail_digest']

		# 记录练习信息
		# 日期 练习编号 班级 学号 姓名 邮箱 邮件UID
		self.wb['ex_record'].append([
			mail_digest['date'],
			ex_info['id'],
			stu_info['班级'],
			stu_info['学号'],
			stu_info['姓名'],
			mail_digest['sender'][1],
			mail_digest['uid']])

		return {
			'stu_cls':    stu_info['班级'],
			'stu_name':   stu_info['姓名'],
			'stu_id':     stu_info['学号'],
			'ex_id':      ex_info['id'],
			'ex_brief':   ex_info['brief'],
			'test_spent': ex_info['time_spent'],
			'test_src':   self.root + self.ex_list['folder'] + ex_info['test'],
			'src_dir':    src_dir}

	def __check_ex(self, ex_report):

		# 切换到练习代码所在路径
		os.chdir(ex_report['src_dir'])

		# 防止重复拷贝练习代码相应的单元测试代码
		if not os.path.exists(os.path.basename(ex_report['test_src'])):

			sh.copy(ex_report['test_src'], '.')

		# 编译链接练习代码和相应的单元测试代码
		stdout, build_error = sp.Popen(['make', '-f', self.root + 'makefile'],
			stderr=sp.PIPE).communicate()
		if '' != build_error:

			# error: stray ‘\???’ in program
			try:

				build_error.decode('UTF-8')

			except UnicodeDecodeError:

				build_error = 'error: stray ‘\???’ in program'

			# subject, text, html, file_list
			raise RuntimeError(
				'练习%s未通过编译' %(ex_report['ex_id']),
				None,
				Util.create_html_from_template(
					self.tmplts['ex_build_report'], {
					'ex_id':          ex_report['ex_id'],
					'ex_build_error': build_error}),
				None)

		# 运行测试(Google Test)
		proc = sp.Popen(['make', 'test', '-f', self.root + 'makefile'],
			stdout=sp.PIPE)

		# 等待
		t.sleep(ex_report['test_spent'])

		# 获取测试返回代码
		ret_code = proc.poll()

		# 测试仍在运行, 是否存在死循环?
		if ret_code is None:

			# 终止测试
			proc.kill()

			# subject, text, html, file_list
			raise RuntimeError('练习%s运行超时, 参考用时%f秒' %(
				ex_report['ex_id'], ex_report['test_spent']), '', None, None)

		# 测试失败
		if 0 != ret_code:

			# subject, text, html, file_list
			raise RuntimeError(
				'练习%s测试失败' %(ex_report['ex_id']),
				None,
				Util.create_html_test_detail(
					self.tmplts['ex_test_report'], ex_report['ex_id']),
				None)

		# 获取测试输出
		ex_report['ex_output'] = proc.communicate()[0]

	def commit_exer(self, args):

		# 设置默认参数eid
		AutoCheck.__set_dflt_arg(args, 'eid')

		try:

			# 验证提交的练习参数
			ex_report = self.__valid_ex(args)

			# 检查练习代码
			self.__check_ex(ex_report)

			# 创建字段
			ex_report['ex_code'] = '\n'

			# 附加代码
			for src_name in os.listdir('.'):

				if src_name.endswith('.c'):

					with open(src_name, 'rb') as src:

						ex_report['ex_code'] += '----- ' + src_name + ' -----\n'
						ex_report['ex_code'] += src.read() + '\n\n'

			# 生成实验报告文件名
			ex_report_docx = 'C语言程序设计实验报告%s(%s %s).docx' %(
				ex_report['ex_id'], ex_report['stu_id'], ex_report['stu_name'])

			# 生成实验报告
			Util.create_docx_table(self.tmplts['ex_report_doc'], ex_report,
				ex_report_docx)

			# subject, text, html, file_list
			raise RuntimeError('练习%s已通过测试' %(ex_report['ex_id']),
				'实验报告已作为附件发送', None, ex_report_docx)

		except RuntimeError as err:

			# subject, text, html, file_list
			self.__reply(args, err[0], err[1], err[2], err[3])

	def __ex_info_to_html(self, ex_info):

		def get_ex_file(ex_file_name):

			if ex_info[ex_file_name] is not None:

				with open(self.root + self.ex_list['folder']
					+ ex_info[ex_file_name], 'rb') as ex_file:

					return ex_file.read()

			return ''

		return Util.create_html_from_template(
			self.tmplts['ex_info'], {
			'ex_id':         ex_info['id'],
			'ex_brief':      ex_info['brief'],
			'ex_src_name':   ex_info['src'],
			'ex_src_code':   get_ex_file('src'),
			'ex_test_name':  ex_info['test'],
			'ex_test_code':  get_ex_file('test'),
			'ex_time_spent': ex_info['time_spent']})

	def __valid_sender(self, args):

		# 获取发件人邮箱地址
		sender_mailbox = args['mail_digest']['sender'][1]

		# 检查是否为授权的发件人
		if sender_mailbox not in self.mail.get_white_list():

			log.info('Untrusted sender: ' + sender_mailbox)

			return False

		return True

	def add_exer(self, args):

		if not self.__valid_sender(args):

			return

		# 设置默认参数eid
		AutoCheck.__set_dflt_arg(args, 'eid')

		try:

			ex_info = self.__get_ex_info(args)['ex_info']
			subject = '练习%s已更新' %(ex_info['id'])

		except KeyError as err:

			self.get_exer_list(args, '添加练习内容请求无效, %s: %s'
				%(err[0], args['cmd_line']), '请在以下列表中选择或新增:')

			return

		except ValueError:

			# 建立新的练习信息
			ex_info = {
				'id':         args['eid'],
				'brief':      None,
				'src':        None,
				'test':       None,
				'time_spent': None}

			# 添加新练习
			subject = '练习%s已添加' %(ex_info['id'])

			# 将新练习信息添加到练习列表中
			self.ex_list['exs'] += [ex_info]

		# 检查命令行可选参数
		if args.has_key('ts'):

			ex_info['time_spent'] = float(args['ts'])

		# 获取邮件主体
		mail_body = args['mail_body']

		# 从邮件正文寻找练习说明
		if mail_body.text_part is not None and mail_body.text_part != '':

			ex_info['brief'] = mail_body.text_part.get_payload(
				).decode(mail_body.text_part.charset).encode('UTF-8')

		# 检查命令行可选参数
		src_name  = args['src']  if args.has_key('src')  else None
		test_name = args['test'] if args.has_key('test') else None

		# 存在一个即可
		if src_name is not None or test_name is not None:

			# 从邮件附件寻找练习代码及其单元测试代码
			for part in mail_body.mailparts:

				if part.filename is None:

					continue

				# 文件名转码为UTF-8
				file_name = part.filename.encode('UTF-8')

				# 检查文件名
				if file_name in [src_name, test_name]:

					with open(self.root + './test/' + file_name, 'wb') as file:

						file.write(
							'/*\n * '
							+ ex_info['brief'].replace('\n', '\n * ')
							+ '\n */\n'
							+ part.get_payload())

					ex_info['src' if file_name == src_name
						else 'test'] = file_name

		self.__reply(args, subject, html=self.__ex_info_to_html(ex_info))

	def del_exer(self, args):

		if not self.__valid_sender(args):

			return

		# 设置默认参数eid
		AutoCheck.__set_dflt_arg(args, 'eid')

		try:

			ex_info = self.ex_list['exs'].pop(
				self.__get_ex_info(args)['ex_idx'])

			self.__reply(args, '练习%s已删除' %(ex_info['id']),
				html=self.__ex_info_to_html(ex_info))

		except (KeyError, ValueError) as err:

			self.get_exer_list(args, '删除练习内容请求无效, %s: %s'
				%(err[0], args['cmd_line']), '请在以下列表中选择:')

	def get_exer_stat(self, args):

		if not self.__valid_sender(args):

			return

		self.__save_ex_stat()
		self.__reply(args, '已获取练习统计表', '统计表已作为附件发送',
			file_list=self.ex_stat_file_name)

	def __deal_mail_task(self):

		# 循环检查今日新邮件
		while True:

			# 新邮件UIDS
			uids = self.mail.get('UNSEEN')

			# 直到没有新邮件为止
			if not uids:

				break

			# 邮件任务队列
			mail_tasks = []

			# 提取今日邮件内容
			for mail_digest in self.mail.fetch_header(uids):

				# 邮件UID
				uid = mail_digest['uid']

				# 标记为已读
				self.mail.mark_as_read(uid)

				# 邮件主题作为命令行参数解析
				cmd_args = self.parse_cmd_line(mail_digest['subject'])

				# 非练习相关的邮件
				if cmd_args is None:

					log.info('Unrelated mail(uid: <%d>).' %(uid))

					# 标星邮件
					self.mail.star_message(uid)

					# 回复邮件 - 无效的邮件指令
					self.help({'mail_digest': mail_digest},
						'无效的邮件指令, 请在以下列表中重新选择:')

					continue

				log.info('C programming course mail(uid: <%d>).' %(uid))

				# 标记为已回复
				self.mail.mark_as_answered(uid)

				# 添加邮件摘要
				cmd_args['mail_digest'] = mail_digest

				# 是否获取邮件正文
				if cmd_args['fetch']:

					cmd_args['mail_body'] = self.mail.fetch_body(uid)

				# 添加到邮件任务队列
				mail_tasks += [cmd_args]

			# 进入keep alive模式, 新线程定时发送NOOP指令以保持imap连接
			self.mail.enter_noop_mode()

			# 处理邮件任务
			for task in mail_tasks:

				task['cmd'](task)

			# 退出keep alive模式
			self.mail.quit_noop_mode()

	def run(self, sec=1800):

		# 计时开始
		tic = t.time()

		# 打开收件箱
		self.mail.open_mailbox()

		# 处理邮件任务
		self.__deal_mail_task()

		# 循环检查新邮件, 直到到达指定的运行时长
		while t.time() - tic < sec:

			# 等待新邮件推送
			if self.mail.wait_new_mail(600):

				# 处理邮件任务
				self.__deal_mail_task()

		# 关闭收件箱, 断开imap连接
		self.mail.close_mailbox()

	def exit(self):

		self.__save_ex_list()
		self.__save_ex_stat()
