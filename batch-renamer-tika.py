# Copyright (c) 2018 Autoz https://github.com/autolordz

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -*- coding: utf-8 -*-

print('''

Batch Files Renamer (Tika|Tesseract engine)

终极自动重命名机

Created on Thu Dec 28 2018

Updated on 2019-08-05

@author: Autoz (autolordz@gmail.com)

''')

#%%
import os,re,sys,string,json,glob,time
from depends import *
from img_process import *

print('分析文字地址:',tika_url_txt)
print('分析图片地址:',tika_url_ocr)

#%% header
time1 = time.time()
#tg = ['nosysargv','1.jpg']
#tg = ['.','aa']
tg = sys.argv
if len(tg)<=1:
    tg = ['nosysargv','target']

docs_major = ['.txt','.html','.epub','.chm','.wps','.md',
             '.doc','.odt','.docx','.xlsx','.csv','.xls','.rtf',
             '.rar','.zip','.tar','.tgz','.7z',
             '.mp4','.gif','.flv','.mkv','.swf','.psd',
             '.mp3','.m4a','.flac',
             '.pdf',
             ]
docs_file = docs_major+docs_ppt
pics_file = ['.png','.jpg','.jpeg','.bmp','.tif']
filter_suffix = ['.bat','.jar','.exe','.py','.ini']
filter_file = ['log.txt','conf.txt']

print('\n Supported Files:\n Yes: %s  %s \n No: %s'%(docs_file,pics_file,filter_suffix+filter_file))
#remove_file('log.txt')

#%%

def process_tika(file,t=0):
    suffix = get_file_suffix(file)
#    jtxt = get_tika_txt(subprocess_cmd(get_curl_rmeta,file),jtype=2)
    jtxt = get_tika_txt(get_tika_rmeta(file),jtype=2)
    if not jtxt: return file,t
    title = jtxt.get('title','')
    t = jtxt.get('X-TIKA:content','')
    if not t:
        if jtxt.get('Content-Type','') == 'application/pdf':
            print('\n 尝试使用 Tika PDF 来读取...')
            # t = get_tika_txt(subprocess_cmd(get_curl_pdf,file))
            # t = get_tika_txt(get_tika_pdf(file))
            # n_page = int(jtxt.get('xmpTPg:NPages',0))
            # if n_page > 1:
            # file = slice_pdf(file) # 切割 pdf
            print('提取pdf图像.')
            file = img_extra(file)
            t = process_img(file,isfast=0)
        else:
            if not suffix in docs_ppt: # not ppt use ocr
                print('suffix:',suffix)
#                t = get_tika_txt(subprocess_cmd(get_curl_ocr,file))
                t = get_tika_txt(get_tika_ocr(file))
    if not t and title: # 没内容就标题
        return title
    return t

def process_img(file,isfast):
    t = img_correct(file,
                       var.img_correct,
                       var.img_clean,
                       isfast,
                       )
    return t

def rename_img(file):
    t = process_img(file,isfast=1) # 读取图片
    return t

def rename_func(file):
    t = process_tika(file)
    return t

def get_files_list(tg):

    if not tg:
        tg=['.']

    def filter_files(files):
        files = list(filter(lambda x: get_file_suffix(x) not in filter_suffix,files))
        files = list(filter(lambda x: os.path.basename(x) not in filter_file,files))
        return files

    if '*' in tg[0]:
        files = list(map(glob.glob,tg))[0]
    else:
        files = list(filter(os.path.isfile,tg))

    dirs = list(filter(os.path.isdir,tg))

    if len(dirs)>0:
        for dirx in dirs:
            files0 = glob.glob(dirx+'\\*.*')
            files += filter_files(files0)

    return sorted(files, key = lambda x: \
                  docs_file.index(get_file_suffix(x)) if get_file_suffix(x) in docs_file else -1)

def clean_tmp(tg):
    files = get_files_list(tg)
    for f in files:
        if '_mod' in f:
            remove_file(f)

#%% main
mkdir_file('target')

print ("参数: %s \n"%tg)
if tg and len(tg)>0:
    tg.pop(0)

files = get_files_list(tg)
print('>>> files:',files)
print('\n ================ \n')

if len(files)>0:
    try:
        for i,file in enumerate(files):
            if os.path.exists(file):
                if ' ' in file:
                    file0 = file
                    file = file.replace(' ','')
                    os.rename(file0,file)

                suffix = get_file_suffix(file)
                if '_mod' in file or \
                    '~$' in file or \
                    '_vs_' in file:continue # 忽略临时和已Do的文件
                print('>>> 处理文件%s【%s - %s】 \n'%(i,file,get_sizes_human(file)))
                t = ''
                if check_size(file):
                    print('>>> 跳过大文件')
                elif suffix in docs_file:
                    print('尝试使用 Tika 来读取... \n')
                    t = rename_func(file)
                elif suffix in pics_file:
                    print('尝试使用 Tika (图像) 来读取... \n')
                    t = rename_img(file)
                    # if os.path.getsize(file) > 1 * 1024 ** 2:
                    #     print('>>> 跳过文件大于 %s \n'%human_size(os.path.getsize(file)))
                    # else:
                    # print('>>> 跳过文件 %s \n'%file)
                if t:
                    t = txt_clean_type(t,suffix,is_cn=0)[:var.txt_n] # 按类型和字段来清除
                    rename_file(file,t)
                else:
                    print('没有找到内容',file)
                print('\n ================ \n')

        print('>>> 重命名完毕 \n>>> 清除 mod 文件')
        clean_tmp(tg)
        print('>>> 所有操作完成 THE END')
    except FileNotFoundError as e:
        print(e)

time2 = time.time()
print('All Running time: %s Seconds'%(time2-time1))