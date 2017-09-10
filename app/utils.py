#coding=utf-8
import os
import sys
sys.path.append(sys.path[0] + "/lib/")
from werkzeug.contrib.fixers import ProxyFix
import packet
from client import Client
from dictionary import Dictionary
import mschap2
from socket import gethostname
from time import time
import random 
from PIL import Image, ImageDraw, ImageFont, ImageFilter 
import StringIO

_letter_cases = "abcdefghjkmnpqrstuvwxy"
_upper_cases = _letter_cases.upper()
_numbers = ''.join(map(str, range(3, 10)))
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))


def radius_challenge(username, password, host, secret, port, nasip, debug):
        hostname = gethostname()
        dict_path = sys.path[0] + "/lib/dicts/dictionary"
        radius = Client(server = host, secret = secret, authport = port, dict = Dictionary(dict_path))
        request = radius.CreateAuthPacket(code = packet.AccessRequest)
        if debug:
                print "[DEBUG] assembling packet attributes"
        request["User-Name"] = username
        request["NAS-IP-Address"] = nasip
        request["NAS-Identifier"] = hostname
        if debug:
                print "[DEBUG] auth method: mscharpv2"
        auth = mschap2.MSCHAP2()
        authAttrs = {}
        authAttrs = auth.getAuthAttrs(username, password)
        for key in authAttrs.keys():
                request[key] = authAttrs[key]
        if debug:
                print "[DEBUG] dumping request attributes..."
                for key in request.keys():
                        print "[DEBUG]\t\t %s : %s" % (key,request[key])
        tsStart = time()
        try:
                reply = radius.SendPacket(request)
        except packet.PacketError,e:
                if debug:
                        print e
                print "CRITICAL: Timeout sending Access-Request"
                return False
        tsStop = time()
        if debug:
                print "[DEBUG] dumping reply attributes..."
                for key in reply.keys():
                        print "[DEBUG]\t\t %s : %s" % (key,reply[key])
        if reply.code == packet.AccessAccept:
                print username," OK: Access-Accept in: %0.2f seconds" % (tsStop - tsStart)
                return True
        else:
                print "CRITICAL: Access-Reject in: %0.2f seconds" % (tsStop - tsStart)
                return False

_letter_cases = "abcdefghijklnmopqrstuvwxyz"
_upper_cases = _letter_cases.upper()
_numbers = ''.join(map(str, range(3, 10)))
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))
FONT_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'framd.ttf')

def create_validate_code(size=(150, 40),
                         chars=init_chars,
                         img_type="jpeg",
                         mode="RGB",
                         bg_color=(255, 255, 255),
                         fg_color=(0, 0, 255),
                         font_size=18,
                         font_type=FONT_FILE_PATH,
                         length=6,
                         draw_lines=True,
                         n_line=(1, 2),
                         draw_points=True,
                         point_chance=2):
    """
    @todo: 生成验证码图片
    @param size: 图片的大小，格式（宽，高），默认为(120, 30)
    @param chars: 允许的字符集合，格式字符串
    @param img_type: 图片保存的格式，默认为GIF，可选的为GIF，JPEG，TIFF，PNG
    @param mode: 图片模式，默认为RGB
    @param bg_color: 背景颜色，默认为白色
    @param fg_color: 前景色，验证码字符颜色，默认为蓝色#0000FF
    @param font_size: 验证码字体大小
    @param font_type: 验证码字体，默认为 ae_AlArabiya.ttf
    @param length: 验证码字符个数
    @param draw_lines: 是否划干扰线
    @param n_lines: 干扰线的条数范围，格式元组，默认为(1, 2)，只有draw_lines为True时有效
    @param draw_points: 是否画干扰点
    @param point_chance: 干扰点出现的概率，大小范围[0, 100]
    @return: [0]: PIL Image实例
    @return: [1]: 验证码图片中的字符串
    """

    width, height = size  # 宽， 高
    img = Image.new(mode, size, bg_color)  # 创建图形
    draw = ImageDraw.Draw(img)  # 创建画笔

    def get_chars():
        """生成给定长度的字符串，返回列表格式"""
        return random.sample(chars, length)

    def create_lines():
        """绘制干扰线"""
        line_num = random.randint(*n_line)  # 干扰线条数
        for i in range(line_num):
            # 起始点
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            # 结束点
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))

    def create_points():
        """绘制干扰点"""
        chance = min(100, max(0, int(point_chance)))  # 大小限制在[0, 100]

        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        """绘制验证码字符"""
        c_chars = get_chars()
        strs = ' %s ' % ' '.join(c_chars)  # 每个字符前后以空格隔开

        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)
        draw.text(((width - font_width) / 3, (height - font_height) / 3),
                  strs, font=font, fill=fg_color)

        return ''.join(c_chars)

    if draw_lines:
        create_lines()
    if draw_points:
        create_points()
    strs = create_strs()
    # 图形扭曲参数
    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)  # 创建扭曲
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强（阈值更大）
    return img, strs
