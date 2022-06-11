#  _*_ coding:   utf-8 _*_
#  @Time     :   2022/6/9 16:57
#  @Author   :   Luohen
#  @Email    :   2794998378@qq.com
#  @Software :   pycharm

import redis

class Manager:
    def __init__(self):
        self.client = redis.Redis()

    #查询昵称
    def check_nickname(self,name):
        flag = self.client.sadd('userinfo',name)
        if flag:
            return False  ##用户不存在
        else:
            return True   # 用户已经存在
    # 设置token
    def set_token(self,name,token):
        self.client.set(name,token,ex=36000)

    # 校验token
    def check_token(self,name):
        token = self.client.get(name)
        return token
    # 获取聊天消息
    def get_message(self):
        self.client.ltrim('chat_list',-20,-1) # 保留前二十条信息
        chat_list = self.client.lrange('chat_list',-20,-1)
        chat_list = [i.decode() for i in chat_list]
        return chat_list
