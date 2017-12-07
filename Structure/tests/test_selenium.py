from selenium import webdriver
import unittest
from app import create_app,db
from app.models import Role,User,Post
import threading
import re
import time

class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        #启动Firefox
        #无法启动浏览器服务，所以忽略本次测试，下面的测试代码被注释
        try:
            cls.client = webdriver.Firefox()
        except:
            pass
        #如果无法启动，则跳过测试
        if cls.client:
            #创建程序
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            #禁止日志，保持输出简洁
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            #创建数据库，并使用一些虚拟数据填充
            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            #添加管理员
            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='john@example.com',username='john',password='cat',role=admin_role)
            admin.confirmed = True
            db.session.add(admin)
            db.session.commit()

            #在一个线程中启动flask服务器
            threading.Thread(target=cls.app.run).start()
            time.sleep(1)
    @classmethod
    def tearDownClass(cls):
        if cls.client:
            #关闭flask服务器和浏览器
            cls.client.get({'url':'http://localhost:5000/shutdown'})
            cls.client.close()

            #销毁数据库
            db.drop_all()
            db.session.remove()

            #删除上下文
            cls.app_context.pop()
        def setUp(self):
            if not self.client:
                self.skipTest('Web browser not available.')

        def tearDown(self):
            pass

    # def test_admin_home_page(self):
    #     #进入首页
    #     self.client.get('http://localhost:5000/')
    #     self.assertTrue(re.search('Hello,\s+Stranger!',self.client.page_source))
    #
    #     #进入登录页面
    #     self.client.find_element_by_link_text('Log In').click()
    #     self.assertTrue('<h1>Login</h1>' in self.client.page_source)
    #
    #     #登录
    #     self.client.find_element_by_name('email').send_keys('john@example.com')
    #     self.client.find_element_by_name('password').send_keys('cat')
    #     self.client.find_element_by_name('submit').click()
    #     self.assertTrue(re.search('Hello,\s+john!',self.client.page_source))
    #
    #     #进入用户个人资料页面
    #     self.client.find_element_by_link_text('Profile').click()
    #     self.assertTrue('<h1>john</h1>' in self.client.page_source)