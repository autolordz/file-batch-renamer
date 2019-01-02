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
print("""
Batch Files Rename (Tika|Tesseract engine)

Created on Thu Dec 28 2018

@author: Autoz (autolordz@gmail.com)

=======================
""")

#%%
import zhon.hanzi,zhon.cedict
import os,re,sys,lob,string
from PIL import Image 

import subprocess,platform

os.environ['TIKA_VERSION'] = '1.20'
os.environ['TIKA_PATH'] = os.getcwd()

from tika import parser 
from tika import language
from tika import tika

#%%
def remove_file(file):
    if os.path.exists(file):
        print('>>> del',file)
        os.remove(file)
        
def os_rename(origin,dist):
    if dist:
        header = os.path.dirname(origin)+'\\' if os.path.dirname(origin) else ''
        file_n = header + dist + os.path.splitext(origin)[1]
        if not file_n == origin:
            try:
                os.rename(origin,file_n)
            except FileExistsError:
                os_rename(origin,dist+'_copy')
            print('>>> 重命名: 【%s】=>【%s】'%(origin,file_n))

def rename_file(file,txt,sfile='',img_h = 1):
    print('>>> 找到内容: 【%s】'%txt)
    if sfile or img_h > 1:
        os_rename(sfile,txt)
        remove_file(file)
    else:
        os_rename(file,txt)

#%%

def parse_subpath(path,file):
    '''make subpath'''
    if not path: return file
    if not os.path.exists(path):
        os.mkdir(path)
    return os.path.join(path,file)

def clean_txt_func(x,**kwargs):
    x = re.sub(r'\s+',',',x)
    s = int(kwargs.get('txt_l',len(''.join(x))))
    punc_all = string.punctuation + zhon.hanzi.punctuation
    char_all = string.printable + zhon.cedict.all
    if re.search(r'[\u4e00-\u9fff]+',x):
        x = re.sub(r'(?<=[%s\w]{2})[%s]'%(zhon.cedict.all,punc_all),'|',x)
        x = re.sub(r'[%s]'%punc_all.replace('|',''),'',x) # chinese punctuation
        x = re.sub(r'[^%s]'%char_all,'',x)
    else:
        x = re.sub(r'(?<=\w{2})[%s]'%(string.punctuation),'|',x)
        x = re.sub(r'[%s]'%string.punctuation.replace('|',''),'',x) # punctuation
        x = re.sub(r'[^%s]'%string.printable,'',x) # printable
    x = re.sub(r'PowerPoint|演示文稿|Sheet1','',x) # PowerPoint Excel
    xx = re.split(r'\|',x)
    xx = '_'.join(xx)[:s]
    return xx

#%%
from pptx import Presentation

class PresentationBuilder():

    def __init__(self,ifile):
        self.presentation = Presentation(ifile)

    @property
    def xml_slides(self):
        return self.presentation.slides._sldIdLst  # pylint: disable=protected-access

    def move_slide(self, old_index, new_index):
        slides = list(self.xml_slides)
        self.xml_slides.remove(slides[old_index])
        self.xml_slides.insert(new_index, slides[old_index])

    def delete_slide(self, index):
        slides = list(self.xml_slides)
        self.xml_slides.remove(slides[index])
    
    def remain_slide(self, starti, endi):
        slides = list(self.xml_slides)
        for i,slide in enumerate(slides):
            if i not in range(starti,endi):
                self.xml_slides.remove(slide)
    
    def save_ppt(self,ofile):
        self.presentation.save(ofile)

#%% slice pptx

def slice_pptx(file,starti=0,endi=0):
    endi = endi+1 if endi else starti+1 # 1 page or X pages
    print('尝试 slice %s: %s - %s'%(file,starti,endi))
    psr = PresentationBuilder(file)
    psr.remain_slide(starti,endi)
    ofile = os.path.splitext(file)[0]+'_slice'+os.path.splitext(file)[1]
    psr.save_ppt(ofile)
    return ofile

#%% slice pdf

from PyPDF2 import PdfFileWriter, PdfFileReader

def slice_pdf(file,num_pages=1):
    with open(file,'rb') as fp:
        pdfObj = PdfFileReader(fp,strict = False)
        print('pdf all page:【%s】'%pdfObj.getNumPages())
        num_pages = num_pages if num_pages < pdfObj.numPages else pdfObj.numPages
        output = PdfFileWriter()
        for i in range(num_pages):
            output.addPage(pdfObj.getPage(i))
        sfile = os.path.splitext(file)[0]+'_slice.pdf'
        print('尝试 slice 【%s】 pages of pdf'%num_pages)
        with open(sfile, 'wb') as fpo:
            output.write(fpo)
        return sfile
    return ''

#%% rename office
                        
import chardet

def get_txt_text(file):
    try:
        with open(file,'rb') as f:#,encoding='utf-8'
            x = f.read()
            typet = chardet.detect(x)
            x = re.sub(r'\s+',',',x.decode(typet['encoding']))
            print(x[:50])
            return x
    except Exception as e:
        print('>>> 读取 %s 失败,可能格式不正确 => %s'%(file,e))
    return ''

def rename_image(file,**kwargs):
    
    txt_last = kwargs.get('txt_last','')
    sfile = kwargs.get('sfile','')
    img_h = kwargs.get('img_h',1)
    try_rotate = kwargs.get('try_rotate',False)
    rotate_f = kwargs.get('rotate_f',0)
    
    cfile = file if not sfile else sfile
    print('cfile 1:',cfile)
    
    # cut image
    with Image.open(cfile) as img:
        print('image: %s kwargs: %s image size : %s'%(file,kwargs,img.size))
        if img_h > 1:
            img = img.crop((0,0,img.width,img.height/img_h))
            print('image size cuted:',img.size)
            sfile = os.path.splitext(file)[0]+'_cut' + os.path.splitext(file)[1]
            img.save(sfile)
        if rotate_f:
            img = img.rotate(rotate_f,expand=1)
            print('image size rotated:',img.size)
            sfile = os.path.splitext(file)[0]+'_rotated' + os.path.splitext(file)[1]
            img.save(sfile)
    
    cfile = file if not sfile else sfile
    print('cfile 2:',cfile)

    # cmd tesseract
    print('\n 尝试使用tesseract来读取,可能要等待... \n')
                        
    tmpf = os.path.splitext(cfile)[0]+'_tmp.txt' #chi_sim+
            
    catcmd = 'tesseract %s %s -l chi_sim+eng' \
            %(cfile,os.path.splitext(tmpf)[0])
    
    subprocess.check_output(catcmd)
    
    txt = get_txt_text(tmpf)
    txt = re.sub(r'\s+',',',txt) 
 
    # detect languages
    
    # PyICU-2.2-cp36-cp36m-win_amd64.whl  pycld2-0.31-cp36-cp36m-win_amd64.whl
    # from polyglot.detect import Detector  
    # from collections import Counter

    # inter_xy =[]
    # if len(txt)<50: txt += txt
    # try:
    #     detector = Detector(txt,quiet=True)
    #     langs = [x.name for x in detector.languages]
    #     print('可信度,',detector.reliable)
    #     if '中文' in langs:
    #         inter_xy = ['中文']
    #     elif detector.reliable:
    #         inter_xy = list((Counter(langs) & Counter(['中文','英语'])).elements())
    # except Exception as e:
    #     print(e)
    # print('inter_xy',inter_xy)
    
    # not detect
    inter_xy = txt

    if inter_xy: # if meaningful content
        txt = clean_txt_func(txt,**kwargs)
        rename_file(file,txt,sfile,img_h)
    elif txt_last == txt:
        rename_office(file) # meaningless try other method
    elif try_rotate:  # try rotate 
        if rotate_f / 360 != 1:
            kwargs.setdefault('rotate_f',0)
            kwargs['rotate_f'] += 90
            kwargs.setdefault('sfile',sfile)
            kwargs.setdefault('txt_last',txt)
            print('\n 尝试 旋转 %s 度 image \n'%kwargs['rotate_f'])
            rename_image(file,**kwargs)
    elif sfile:
        remove_file(sfile)
    remove_file(tmpf)
    
def parser_tika(file,pimage=False,parserd = '',txt=''):
    
    if not pimage:
        print('\n 尝试使用 Tika 来读取... \n')
        parserd = parser.from_file(file)
    else:
        print('\n 尝试使用 Tika Image 来读取... \n')
        headers = {'X-Tika-PDFextractInlineImages':'true',
                   'X-Tika-OCRLanguage':'chi_sim+eng'}
        parserd = parser.from_file(file,
                          serverEndpoint='http://localhost:9998/rmeta/text',
                          headers=headers)
    if parserd:
        txt = parserd.get('content','')
    return txt

def rename_office(file,txt='',sfile='',**kwargs):
    if '.txt' in file:
        print('\n 直接读取',file)
        txt = get_txt_text(file)
    elif '.pptx' in file and not 'slice' in file:
        sfile = slice_pptx(file)
        txt = parser_tika(sfile)
    elif '.pdf' in file and not 'slice' in file:
        sfile = slice_pdf(file)
        txt = parser_tika(sfile)    
        # txt = parser_tika(file,pimage=True)
        # print(12121212,txt)
    else:
        txt = parser_tika(file)
        
    if not txt and sfile:
        txt = parser_tika(sfile,pimage=True)
        # print(323232323,txt)
    
    if txt:
        # print(re.sub(r'\s+',',',txt[:30]))
        txt = clean_txt_func(txt,**kwargs)
        rename_file(file,txt)
        
    if sfile:
        remove_file(sfile)

#%% main

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
        
suffix_img = ['.png','.jpg','.jpeg','.bmp','.tif']
suffix_fast = ['.txt','.doc','.xls','.docx','.xlsx','.html','.epub','.rar','.zip','.tar']
suffix_slow = ['.ppt','.pptx','.pdf']

def get_files_list(dirs=[]):
    dirs = list(filter(os.path.exists,dirs))
    files = list(filter(os.path.isfile,dirs))
    dirs = list(filter(os.path.isdir,dirs))
    for dirx in dirs:
        files += glob.glob(dirx+'\\*.*')
    return sorted(files, key=lambda x:(suffix_img+suffix_slow).index(os.path.splitext(x)[1]) if os.path.splitext(x)[1] in (suffix_img+suffix_slow) else -1
)

print('''
      
支持文件
   
Supported Files: %s \n %s \n %s

'''%(suffix_img,suffix_fast,suffix_slow))

if sys.argv:
    print ("【sys.argv】:",sys.argv)
    if len(sys.argv)>1:
        files = get_files_list(sys.argv)
    else:
        files = get_files_list(['.'])

# set ocr env
setenv = 'setenv.bat'
if os.path.exists(setenv) and 'Tesseract-OCR' not in str(os.environ):
    p = subprocess.check_output(setenv)
    typet = chardet.detect(p)
    print(re.sub(r'\s+',',',p.decode(typet['encoding'])))                  
else:
    os.environ['path'] += ';c:\\Program Files (x86)\\Tesseract-OCR\\' \
                    if '64bit' in platform.architecture() else  \
                    ';c:\\Program Files\\Tesseract-OCR\\'
print('\n Tesseract-OCR in path >> %s \n'%('Tesseract-OCR' in str(os.environ)))

if len(files)>0:
    print('>>> 正在重命名 ...')
    oversize = 30
    try:
        for i,file in enumerate(files):
            if '~$' in file: continue
            print('处理文件: %s \n'%file)
            if os.path.getsize(file) > oversize * 1024 ** 2:
                print(' 跳过文件大于 %s \n'%convert_bytes(os.path.getsize(file)))
            elif os.path.splitext(file)[1] in ['.doc','.ppt','.xls','.txt',
                                           '.docx','.pptx','.xlsx','.epub',
                                           '.rar','.zip','.tar','.html','.pdf']:
                rename_office(file,txt_l = 30)
            elif os.path.splitext(file)[1] in ['.png','.jpg','.jpeg','.bmp','.tif']:
                rename_image(file,try_rotate = True,txt_l = 30,img_h = 1)
            else:
                print(' 跳过文件 \n')
            print('\n ================ \n')
        print('\n >>> 重命名完毕... \n')
    except FileNotFoundError as e:
        print(e)

#%% test for rename file
# import os,glob
# files = glob.glob('*.*')
# for i,file in enumerate(files):
#     os.rename(file,'file%s'%i+os.path.splitext(file)[1])
