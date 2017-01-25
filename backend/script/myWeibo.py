# coding=utf-8
import mylib

user = ['hanyuan', 'lunhui']

token = {
	user[0]: {u'access_token': u'2.00MWTfnF0ca5Dwab01857013ne2utC', u'remind_in': u'157679999', u'uid': u'5314589544', u'expires_at': 1575323059}, #hanyuanz on hanyuanapp
	user[1]: {u'access_token': u'2.00sENwqFIKyuBE0c7ba8a9b8a1etpD', u'remind_in': u'157679999', u'uid': u'5362906930', u'expires_at': 1575326383} #lunhui018 on lunhui018 
}

app = {
	user[0]: {'key': '857836998', 'secret': 'c6867477b71519d5cda03f0906bf23e0', 'callback': 'http://comp.social.gatech.edu'},
	user[1]: {'key': '3692885300', 'secret': 'd8921779fb11d953af5ba97ab563c4b0', 'callback': 'http://www.georgia.gov'}
}

client = { }
for u in user:
	client[u] = (app[u]['key'], app[u]['secret'], app[u]['callback'], token[u])

def translateRuntimeError(e):
	error = str(e).split(' ', 1)
	errNo = mylib.parseInt(error[0])
	errStr = error[1]
	return (errNo, errStr)

def convertWeiboTime(string):
	from datetime import datetime
	return datetime.strptime(string, '%a %b %d %H:%M:%S +0800 %Y')

if __name__ == '__main__':
	from weibo import Client
	'''
	c = Client('3692885300', 'd8921779fb11d953af5ba97ab563c4b0', 'http://www.georgia.gov')
	print c.authorize_url

	c.set_code('2b17a393ffc9d8e27c7020dd80f55a3d')

	token = c.token
	'''