# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 18:00:24 2019

@author: autol
"""

#%%
#import time
import zhon.hanzi,zhon.cedict,requests
import os,re,json,string,subprocess,configparser
from bs4 import BeautifulSoup

docs_ppt = ['.ppt','.pptx','.pptm']

#%%

class Var(object):
    def __init__(self,
                 target_file=0,
                 tika_url_local=0,
                 tika_url_remote=0,
                 txt_n=0,
                 img_correct=0,
                 img_clean=0,
                 ):
        self.target_file = target_file
        self.tika_url_local = tika_url_local
        self.tika_url_remote = tika_url_remote
        self.txt_n = txt_n
        self.img_correct = img_correct
        self.img_clean = img_clean

var = Var(
            target_file = '.',
            tika_url_local = 'http://127.0.0.1:3232/',
            tika_url_remote = 'http://45.78.19.198:3232/',
            txt_n=60,
            img_correct=1,
            img_clean=1,
            )

cfgfile = 'conf.txt'

punc_all = string.punctuation + zhon.hanzi.punctuation
char_all = string.printable + zhon.cedict.all

def txt_clean(t,tag=','):
    t = list(filter(None,re.split(r'[\n%s]'%punc_all,t)))
    t = list(map(lambda x:re.sub(r'\s+','',x),t))
    t = tag.join(t)
    return t

def txt_clean_type(t,suffix,is_cn=0):
    if suffix in docs_ppt:
        t = re.sub(r'Presentation1|演示文稿|幻灯片','',t) #ppt PowerPoint
    if suffix == '.html':
        t = re.sub(r'\<.*?\>','',t)#html
    if suffix in ['.doc','.docx']:
        t = re.sub(r'\[.*?\]','',t)#docx tags
    if is_cn:
        t = re.sub(r'[a-zA-Z0-9]+','',t)#only chinese
    t = txt_clean(t,tag='_')
    return t

def get_tika_put(file,url,headers,t=''):
    with open(file,'rb') as f:
        r = requests.put(url=url,
                         data=f,
                         headers=headers,
                         )
        r.encoding = r.apparent_encoding # 处理中文乱码
        t = r.text
    return t

# 使用远程
def get_tika_ocr(file):
    url = tika_url_ocr+'tika'
    headers = {
                'X-Tika-OCRLanguage':'chi_sim',
                'X-Tika-OCRpageSegMode':'6'
                }
    return get_tika_put(file,url,headers)

# 使用本地
def get_tika_rmeta(file):
    url = tika_url_txt+'rmeta/text'
    headers = {'Accept': 'application/json',}
    return get_tika_put(file,url,headers)

def get_tika_meta(file):
    url = tika_url_txt+'meta'
    headers = {'Accept': 'application/json',}
    return get_tika_put(file,url,headers)

def get_tika_pdf(file):
    url = tika_url_txt+'tika'
    headers = {
                'X-Tika-PDFextractInlineImages':'true',
                'X-Tika-OCRLanguage':'chi_sim',
                'X-Tika-OCRpageSegMode':'6'
                }
    return get_tika_put(file,url,headers)

def get_curl_ocr(file):
    #-H "X-Tika-PDFOcrStrategy:ocr_only"
    #-H "X-Tika-PDFextractInlineImages:true"
    url = tika_url_ocr+'tika'
    return '''curl -T %s %s -H "X-Tika-OCRLanguage: chi_sim" -H "X-Tika-OCRpageSegMode:6" ''' \
            %(file,url)

def get_tesseract(file):#    os.path.splitext(tmpf)[0]
    return 'tesseract %s stdout -l chi_sim+eng'%(file,)
#    return 'curl -T %s %s -H "Accept: application/json"'%(file,var.tika_url_local+'meta') # return type:list

def get_curl_pdf(file):
    return '''curl -T %s %s -H "X-Tika-PDFextractInlineImages:true" -H "X-Tika-OCRLanguage: chi_sim" -H "X-Tika-OCRpageSegMode:6" ''' \
            %(file,tika_url_ocr+'tika')

def get_curl_meta(file): #-H "X-Tika-OCRLanguage: chi_sim+eng"
    return 'curl -T %s %s -H "Accept: application/json"'%(file,tika_url_txt+'meta') # return type:list

def get_curl_rmeta(file): #-H "X-Tika-OCRLanguage: chi_sim+eng"
    # return 'curl -T %s %s -H "Accept: application/json"'%(file,var.tika_url_local+'rmeta') # return type:list
    return 'curl -T %s %s -H "Accept: application/json"'%(file,tika_url_txt+'rmeta/text')

def subprocess_cmd(func,file):
    try:
        print('cmd:',func(file))
        r = subprocess.check_output(func(file),shell=1).decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(e)
    return r

def subprocess_Popen(cmd):
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,shell=1)
    return iter(p.stdout.readline, b'')

def get_tika_version(url):
    try:
        print(requests.get(url=url+'version',timeout=0.5).text)
        return url
    except Exception as e:
        print('Tika Error',e)
        return None

def setup_local_tika():
    print('Now Start Tika Server...')
    url,url_r = var.tika_url_local,var.tika_url_remote
    if get_tika_version(var.tika_url_local):
        if not get_tika_version(var.tika_url_remote):
            url_r = None
    else:
        url = url_r = get_tika_version(var.tika_url_remote)
        if os.path.exists('tika-server.jar'):
            try:
                cmd = 'start /B java -Djava.awt.headless=true -jar tika-server.jar --config=tika-config.xml --host=127.0.0.1 --port=3232'
                for output_line in subprocess_Popen(cmd):
                    print(output_line)
                    if 'Started' in str(output_line):
                        break
#                if(subprocess.check_call(cmd,shell=1)==0):
#                    print('Start Ok!')
#                    time.sleep(1.5)
                url = get_tika_version(var.tika_url_local)
            except Exception as e:
                print(e,'Select Remote Server...')
    return url,url_r

tika_url_txt,tika_url_ocr = setup_local_tika()

def get_tika_version1():
    try:
        print(subprocess.check_output('curl %s '%(var.tika_url_local+'version'),shell=1))
    except subprocess.CalledProcessError as e:
        print(e)
        return False
    return True

def get_curl_ocr_txt(file):
    return get_tika_txt(subprocess_cmd(get_curl_ocr,file))

def get_tika_txt(txt,jtype=1):
        if is_json(txt): #json type
            if jtype == 1:
                txt = dict(json.loads(txt))
            else:
                txt = dict(json.loads(txt)[0])
        elif 'xmlns' in txt: #html type
            soup = BeautifulSoup(txt)
            txt = soup.find("div", class_="ocr")
            if txt: txt = txt.text
        return txt

def get_sizes_human(file):
    """
    this function will convert bytes to MB.... GB... etc
    """
    num = os.path.getsize(file)
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def print_log(*args, **kwargs):
    print(*args, **kwargs)
    with open('log.txt', "a",encoding='utf-8') as file:
        print(*args, **kwargs, file=file)

def rename_file(file,t):
    if '_mod' in file:
        file = file.replace('_mod','')
    print_log('>>> 找到内容: 【%s】=>【%s】'%(file,t))
    os_rename(file,t)

def os_rename(file,t):
    if file:
        dirname = os.path.dirname(file)
        suffix = os.path.splitext(file)[1]
        oldname =  os.path.splitext(os.path.basename(file))[0]
        header = dirname+'\\' if dirname else ''
        nfile = header + t + '_vs_' + oldname + suffix
        nfile_copy = header + t + '_vs_' + oldname + '_copy' + suffix
        cond = t == os.path.splitext(os.path.basename(file))[0].split('_vs_')[0]
        if not cond:
            print_log('>>> 重命名: 【%s】=>【%s】'%(file,nfile))
            try:
                os.rename(file,nfile)
            except FileExistsError:
                os_rename(file,nfile_copy)

def mkdir_file(path):
    if not os.path.exists(path):
        os.mkdir(path)

def parse_subpath(path,file):
    '''make subpath'''
    if not path: return file
    if not os.path.exists(path):
        os.mkdir(path)
    return os.path.join(path,file)

def remove_file(file):
    if file and os.path.exists(file):
        print('>>> del',file)
        try:
            os.remove(file)
        except Exception as e:
            print(e)

def check_size(file,is_img=0):
    if is_img:
        return os.path.getsize(file) >  500 * 1024 # 大于 500k
    return os.path.getsize(file) >  30 * 1024 ** 2

def get_file_name(file):
    return os.path.splitext(file)[0]

def get_file_suffix(file):
    return os.path.splitext(file)[1]

def get_mod_name(file,tag='_mod',suffix=0):
    # import tempfile # optional use tempfile
    # _, tmp_name = tempfile.mkstemp(prefix='tmp_')
    # file = tmp_name + get_file_suffix(file)
    tag = '' if tag in file else tag
    suffix = suffix if suffix else get_file_suffix(file)
    file = get_file_name(file) + tag + suffix
    return file

def is_json(s):
    try:
        json.loads(s)
    except ValueError:
        return False
    return True

#%% optional config

def process_config():
    try:
        if not os.path.exists(cfgfile):
            '''生成默认配置'''
            write_config()
        read_config()
    except Exception as e:
        print('>>> 配置文件出错 %s ,删除...'%e)
        if os.path.exists(cfgfile):
            os.remove(cfgfile)
        try:
            write_config()
            read_config()
        except Exception as e:
            '''这里可以添加配置问题预判问题'''
            print('>>> 配置文件再次生成失败 %s ...'%e)
    return var

def write_config():
    cfg = configparser.ConfigParser(allow_no_value=1,
                                    inline_comment_prefixes=('#', ';'))

    cfg['config'] = {

                    'target_file': var.target_file+'    # 重命名目录,留空就是当前目录',
                    'tika_url_local': var.tika_url_local+'    # tika本地',
                     'tika_url_remote': var.tika_url_remote+'    # tika远程',
                     'img_cut': str(var.img_cut)+'    # 是否裁剪',
                     'img_thumbnail':str(var.img_thumbnail)+'    # 是否缩小,推荐',
                     'img_correct':str(var.img_correct)+'    # 是否修正',
                     'img_clean':str(var.img_clean)+'    # 是否清理,模糊图片用',
                     'txt_n':str(var.txt_n)+'    # 名字长度',
                     }
    with open(cfgfile, 'w',encoding='utf-8-sig') as configfile:
        cfg.write(configfile)
    print('>>> 重新生成配置 %s ...'%cfgfile)

def read_config():
    cfg = configparser.ConfigParser(allow_no_value=1,
                                    inline_comment_prefixes=('#', ';'))
    cfg.read(cfgfile,encoding='utf-8-sig')
    var.target_file = cfg['config']['target_file']
    var.tika_url_local = cfg['config']['tika_url_local']
    var.tika_url_remote = cfg['config']['tika_url_remote']
    var.img_cut = int(cfg['config']['img_cut'])
    var.img_thumbnail = int(cfg['config']['img_thumbnail'])
    var.img_correct = int(cfg['config']['img_correct'])
    var.img_clean =int(cfg['config']['img_clean'])
    var.txt_n = int(cfg['config']['txt_n'])
    return dict(cfg.items('config'))

