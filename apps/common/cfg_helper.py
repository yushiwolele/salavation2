# --*-- coding:utf-8 --*--

from configobj import ConfigObj
import configparser


class MyConf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    # 这里重写了optionxform方法，直接返回选项名
    def optionxform(self, optionstr):
        return optionstr


class CfgHelper():
    cf = MyConf()

    def __init__(self, cfg_file):
        self.cfg_file = cfg_file

    # 这里重写了optionxform方法，直接返回选项名
    def optionxform(self, optionstr):
        return optionstr

    # 返回配置文件中sec列表
    def read_cfg_sec_nosort(self):
        self.cf.read(self.cfg_file)
        # 读配置文件（ini、conf）返回结果是列表
        sec = self.cf.sections()
        return sec

    # 返回sec下的key/value
    def read_cfg_key_value_nosort(self, sec):
        self.cf.read(self.cfg_file)
        opt = self.cf.items(sec)
        print(opt)
        d = dict(opt)
        return d

    # 返回cfg下面的sec列表
    def read_cfg_sec(self):
        config = ConfigObj(self.cfg_file, encoding='UTF8')
        sec = config.keys()
        return sec

    # 获取某个sec下的key和value值
    def read_cfg_key_value(self, sec):
        config = ConfigObj(self.cfg_file, encoding='UTF8')
        item = config.__getitem__(sec)
        return item

    # 获取某个sec下的key对应的value值
    def read_cfg_get_value_by_key(self, sec, key):
        config = ConfigObj(self.cfg_file, encoding='UTF-8')
        value = config[sec][key]
        return value

    # 写入cfg文件
    def write_cfg_key_vlaue(self, sec, sec_key, value):
        config = ConfigObj(self.cfg_file, encoding='UTF-8')
        config[sec][sec_key] = value
        config.write()
