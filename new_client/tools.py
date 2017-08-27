from functools import wraps


class Timer:
    """一个计时器实现，用于在view_frame当中计时"""
    def __init__(self, hour=0, minute=0, second=0):
        """初始化计时器，传入已累计的时间，方便从该时间点开始计时

        :param hour: 小时
        :param minute: 分钟
        :param second: 秒
        """
        self.hour = hour
        self.minute = minute
        self.second = second

    def add_time(self):
        """计时器核心"""
        if self.second < 59:
            self.second += 1
        elif self.minute < 59:
            self.second = 0
            self.minute += 1
        else:
            self.hour = 0

    def display(self):
        """显示时间，返回一个表示累计时间的str"""
        # 使用神奇的format字符串填充解决时间显示的问题
        return '{:0>2}: {:0>2}: {:0>2}'.format(self.hour, self.minute, self.second)


class Proxy:
    """用来做button command处理函数的代理，保存当前参数，方便使用循环创建button"""
    def __init__(self, method, *args):
        """构造函数

        :param method: 被代理的方法
        :param args: 被代理方法所需要的参数序列
        """
        self.method = method
        self.args = args

    def __call__(self):
        """当button事件触发时被调用"""
        self.method(*self.args)


def frame_init(method):
    """任何切换页面的行为都要进行页面初始化，切换页面后判断是否所有的页面都已经被delete，保证
    当前vocabulary.main当中的所有frame都已经被delete，防止frame重叠
    """
    # wraps用来防止method名字被修改为decorate
    @wraps(method)
    def decorate(self, *args, **kwargs):
        if not self.upper_frame.view_frame.is_deleted:
            self.upper_frame.view_frame.delete()
        if not self.upper_frame.login_frame.is_deleted:
            self.upper_frame.login_frame.delete()
        if not self.upper_frame.register_frame.is_deleted:
            self.upper_frame.register_frame.delete()
        return method(self, *args, **kwargs)
    return decorate

