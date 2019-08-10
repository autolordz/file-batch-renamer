# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 10:42:16 2019

@author: autol

This script is to getting txt through processing img
"""

#%%
import os,re
import fitz
import cv2
import numpy as np
from PIL import Image
import time
from depends import txt_clean,get_mod_name,get_sizes_human
from depends import get_tika_ocr,get_tika_txt
import requests,json
img_log = 'img_log.csv'

#%% CV2 Adaptive Thresholding

def laplacian(img):
    ddepth = cv2.CV_16S
    kernel_size = 3
    img = cv2.Laplacian(img, ddepth, ksize=kernel_size)
    img = cv2.convertScaleAbs(img) # converting back to uint8
    return img

def remove_noise(img):
    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    return img

def img_resize_cv2(img):
    img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    # img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_LINEAR)
    return img

def img_blur(img,bt=0):
    # img = cv2.GaussianBlur(img, (3, 3), 0) # 高斯模糊去噪
    img = cv2.GaussianBlur(img, (9, 9),bt) # 高斯模糊去噪
    return img

def img_BGR2RGB(img):
    return cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

def img_sharpen_cv2(img):
    n=6;m=70
    kr = np.ones((n,n),np.float32)/20
    img = cv2.filter2D(img, -1, kr)
    img = cv2.addWeighted(img, 4, cv2.blur(img, (m,m)), -4, 128)
    # img = cv_imread_cn(file,0)
    # kr = np.ones((5,5),np.float32)/25
    # kr = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    # kr = np.eye(3,dtype = np.uint8)
    # img = cv2.filter2D(img, -1, kr)
    # img = cv2.addWeighted(img, 4, cv2.blur(img, (60, 60)), -4, 128)
    # img = cv2.GaussianBlur(img, (5, 5),0)
    # img = cv2.medianBlur(img,5)
    # img = cv2.blur(img, (30, 30))
    # img = cv2.bilateralFilter(img,9,75,75)
    return img

def get_cv2(img):
    return  {
            # 'grey': cv2.cvtColor(cv_imread_cn(file), cv2.COLOR_BGR2GRAY), # convert_to_gray
            # 'blur' : cv2.medianBlur(img,5),
            # 'EHIST' : cv2.equalizeHist(img),
            'BINARY' : cv2.threshold(img,127,255,cv2.THRESH_BINARY)[1],
            'BINARY1' : cv2.threshold(cv2.GaussianBlur(img, (3, 3), 0),127,255,cv2.THRESH_BINARY)[1],
            'BINARY_INV' : cv2.threshold(img,127,255,cv2.THRESH_BINARY_INV)[1],
            'TRUNC': cv2.threshold(img,127,255,cv2.THRESH_TRUNC)[1],
            'TRUNC1': cv2.threshold(img,127,255,cv2.THRESH_TRUNC+cv2.THRESH_BINARY)[1],
            'TRUNC2': cv2.threshold(cv2.GaussianBlur(img, (3, 3), 0),127,255,cv2.THRESH_TRUNC)[1],
#            'TRUNC3': cv2.threshold(img,127,255,cv2.THRESH_TRIANGLE+cv2.THRESH_TRUNC)[1],
            # 'TOZERO' : cv2.threshold(img,127,255,cv2.THRESH_TOZERO)[1],
            # 'THRESH_TRIANGLE' : cv2.threshold(img,127,255,cv2.THRESH_TRIANGLE)[1],
            # 'TOZERO_INV' : cv2.threshold(img,127,255,cv2.THRESH_TOZERO_INV)[1],
            # 'Otsu’s Threshold' : cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # 'Otsu1': cv2.threshold(cv2.GaussianBlur(img, (9, 9), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # 'Otsu2': cv2.threshold(cv2.GaussianBlur(img, (7, 7), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # 'Otsu3': cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # 'Otsu4':cv2.threshold(cv2.medianBlur(img, 5), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # 'Otsu5':cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # 'Adaptive Mean Thresholding':cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2),
            # 'Adaptive Gaussian Thresholding':cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2),
           }

#%%

def img_extra(file):
    doc = fitz.open(file)
    for i in range(len(doc)):
        for img in doc.getPageImageList(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            # file = "p%s-%s.png" %(i, xref)
            file = get_mod_name(file,suffix='.png')
            if pix.n < 5:       # this is GRAY or RGB
                pix.writePNG(file)
                return file
            else:               # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.writePNG(file)
                return file
            pix = None
    return file

def img_save_cv(file,cv_img,tag='_mod'):
    nfile = get_mod_name(file,tag=tag)
    # img = cv_imread_cn('idcard1.jpg',0)
#    cv2.imwrite(nfile,cv_img)
    # plt.imsave(nfile,cv_img,cmap='gray')
    cv2.imencode(os.path.splitext(nfile)[1], cv_img)[1].tofile(nfile) # 为了保存中文
    return nfile

def img_save_pli(file,img,tag='_mod'):
    nfile = get_mod_name(file,tag=tag)
    img.save(nfile)
    return nfile

def img_pli2cv(img):
    return np.array(img)

def img_cv2pli(img):
    return Image.fromarray(img)

def img_clean_cv(img,method='TRUNC1'):
    ss = 1.7
    img = cv2.resize(img, None, fx=ss, fy=ss, interpolation=cv2.INTER_AREA)
    img = get_cv2(img).get(method,'')
    img = cv2.resize(img, None, fx=1/ss, fy=1/ss, interpolation=cv2.INTER_AREA)
    return img

def img_clean_pli(img):
    img = img_pli2cv(img)
    img = img_clean_cv(img,method='BINARY')
    img = img_clean_cv(img,method='TRUNC3')
    return img

def img_rotate_pli(img,angle):
    w,h = img.size
    if angle:
        img = img.rotate(angle,expand=1,fillcolor=255)
        # plt.imshow(img,'gray')
    return img

def img_cut(imgs,arate):
    def cutt(img):
        if not img is None:
            h,w=img.shape
#            arate = 1/3 if h/w > 1 else 1
            ofs = 60
            img = img[ofs:ofs+int(arate*h),0:w]
#                plt.figure()
#                plt.imshow(img,'gray')
        return img
    return [cutt(img) for img in imgs]

def img_buffer(img,n=8):
    h,w = img.shape
    h,w = h//n,w//n
    roi = img[h:(n-1)*h,w:(n-1)*w]
    return roi

def img_buffer_sq(img,a=.2):
    s = min(img.shape)
    a1 = int((1-a)/2*s)
    a2 = a1+int(a*s)
    roi = img[a1:a2,a1:a2]
    return roi

def img_buffer_check_fill(img,file):
    arate = .25
    imgb = img_buffer_sq(img,arate)
#    plt.figure()
#    plt.imshow(imgb,'gray')
    t,rate = img_tika_txt(imgb,file,'_buf',clean_nums=1)
#    print('img_buffer_check_fill \n',t)
    if len(t)<20:
        arate = .6
    print('arate',arate)
    return arate

def img_rotate_horizon(img,file,arate):

    src = img_clean_cv(img.copy(),method='BINARY')
    src1 = img_clean_cv(img.copy(),method='BINARY1')
#    src1 = img_clean_cv(img_clean_cv(img.copy(),method='BINARY'),method='TRUNC')
#    src1 = img_clean_cv(img_clean_cv(img.copy(),method='BINARY2'),method='TRUNC1')
    angle = 0
    while angle < 360:#360
#        roi = img_buffer_sq(img_rotate_cv(src,angle),n=5)
        roi = img_rotate_cv(img_buffer_sq(src.copy(),a=arate),angle)
        roi1 = img_rotate_cv(img_buffer_sq(src1.copy(),a=arate),angle)
        row_sums = roi.sum(axis=1)
        row_sums = (row_sums/max(row_sums)) * 255
#        print('angle:',angle,'\n',row_sums)
#        score = sum(row_sums>np.mean(row_sums))
        score = np.count_nonzero(row_sums)
        ay = np.array([[angle,score,roi1]])
        print(ay[:,:2])
        if angle == 0:
            scores = ay
        else:
            scores = np.vstack([scores,ay])
        angle += 90#.5

    ss = scores[scores[:,1].argsort()][:2]
    df =[]
    for score in ss:
        angle = score[0]
        roi = score[2]
#            plt.figure()
#            plt.imshow(roi,'gray')
#            plt.title(angle)
        t,rate = img_tika_txt(roi,file,str(angle),clean_nums=1)
        if angle == 0:
            rate += .3
        if angle == 90:
            rate += .1
        df.append([angle,t,rate,roi])

    dfn = img_tika_df_best(np.array(df))
    best_angle = dfn[0]
    print('best angle:【%s】'%best_angle)
    return best_angle


#%%

#url_flask = 'http://127.0.0.1:2121/'
url_flask = 'http://45.78.19.198:2121/'

def flask_ocr_get(file):
    files = {'file': open(file, 'rb')}
    r = requests.post(url=url_flask+'ocr',
                      files=files)
    return r.text

def tika_words_rate3(t): # 使用远程flask来处理,减少压缩包
    t = json.dumps({'t':t})
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url=url_flask,
                      data=t,
                      headers=headers)
    r = float(dict(json.loads(r.text)).get('rate',0))
    return r

def tika_words_rate1(t):
    en = list(filter(None,re.split(r'[^a-zA-z]',t)));print(en)
    zh = list(filter(None,re.split(r'[^\u4e00-\u9fa5]',t)));print(zh)
    r = len(en)/len(zh)
    r = 0 if .5<r<1.5 else 1
    print(r)
    return r

def img_tika_txt(img,file='',index='',clean_nums=0):

    s1 = time.time()
    nfile = img_save_cv(file,img,tag='_mod_'+index)
    t = get_tika_txt(get_tika_ocr(nfile))
#    t = flask_ocr_get(nfile)
#    t = pytesseract.image_to_string(img,config=r'--psm 6 -l chi_sim');t
    if clean_nums: t = re.sub(r'[0-9]','',t);t #^\u4e00-\u9fa5
    if not t:return t,0
    s2 = time.time()
    print('get_tika_txt Running time: %s Seconds'%(s2-s1))

    s1 = time.time()
#    r = tika_words_rate2(t)
    r = tika_words_rate3(t)
    s2 = time.time()
    print('tika_words_rate3 Running time: %s Seconds'%(s2-s1))
    return txt_clean(t,tag='_'),r

#%%
def img_major_color(file):
    img = Image.open(file).convert('L') # 转换灰度图
    if img.getcolors():
        npcolors = np.array(img.getcolors())
        return npcolors[np.argmax(npcolors[:,0])][1]

def img_thumbnail(file):
    img = Image.open(file).convert('L')
    img.thumbnail((1200,1200), Image.ANTIALIAS)
    cv_img = np.array(img)
    return cv_img

def img_rotate_cv(img, angle):
    if angle:

        img = np.rot90(img,k=angle//90)
    return img

def img_read_pli(file,
                 iscorrect=0,
                 isclean=0,
                 isfast=1,
                 ):

    n = 1000 # 裁剪范围
    img0 = Image.open(file)
    img0_t = img0.copy()
    img0_t.thumbnail((n,n), Image.ANTIALIAS)
    img_t = img0.copy().convert('L')
    img_t.thumbnail((n,n), Image.ANTIALIAS)

    if isfast:
        npcolors = np.array(img_t.getcolors())
        mc_rate = npcolors[np.argmax(npcolors[:,0])][0] / sum(npcolors[:,0]);mc_rate
        if mc_rate > .5:
            print('不做处理')
            return (np.array(img0_t),)

    img_nt = np.array(img_t)
    arate = img_buffer_check_fill(255-img_nt.copy(),file)
    img2=None

    if iscorrect:
        angle = img_rotate_horizon(255-np.array(img_t),file,arate)
        img_r = img_nt.copy()
        if angle:
            img_r = np.array(img_rotate_pli(img_t,angle))

        img2 = img_clean_cv(img_clean_cv(255-img_r.copy(),
                                         method='BINARY'),
                            method='TRUNC2')
    img1=None
    if isclean:
        img1 = img_clean_cv(img_clean_cv(img_nt.copy(),
                                         method='BINARY'),
                            method='TRUNC')

    img_nt = img_clean_cv(img_nt.copy(),
                          method='TRUNC')

    imgs = (img1,img2,img_nt)

    if arate<.5:
        imgs = img_cut(imgs,arate)

    return imgs

def array1d2d(df):
    if len(df)>0 and df.ndim == 1:
        return df[np.newaxis,:]
    return df

def img_tika_df_best(df1):
    df1 = df1[df1[:,2].astype(float).argsort()[::-1]]
    print('======111===\n',df1[:,:3])
#    for d in df1:
#        plt.figure()
#        plt.imshow(d[3],'gray')
#        plt.title(d[0])
    lens = [len(x) for x in df1[:,1]]
    if sum(lens)/len(lens) < max(lens)/2: # 选择最长的结果
        df2 = df1[np.argmax(lens)]
    else:
        df2 = df1[0] # df1[len(df1)//2-1] # 差不多长选择第一个结果
#    print('====222====\n',df2[:3])
    return df2

def img_tika_df(file,iscorrect,isclean,isfast):

    print('修正图像:',get_sizes_human(file))
#    plt.imshow(imgs[3],'gray')
    df = []
    if os.path.exists(img_log):
        df = np.genfromtxt(img_log, delimiter=',',dtype=str,encoding='utf-8')
        df = array1d2d(df)

    dfn = []
    if len(df)>0:
        checks = [file in x for x in df[:,0]]
    if len(df)>0 and any(checks):
        dfn = df[checks]
    else:
        imgs = img_read_pli(file,iscorrect,isclean,isfast)
        df1 = []
        for i,img in enumerate(imgs):
            if not img is None:
                t,rate = img_tika_txt(img,file,'_ix'+str(i))
                if len(t)>10: # 过滤内容不够的
                    tk = np.array([[file+str(i),t,rate,img]],dtype=object);tk
                    df1 = np.vstack([df1,tk]) if len(df1)>0 else tk
        if len(df1)>0:
            dfn = img_tika_df_best(df1)
#            plt.figure()
#            plt.imshow(dfn[3],'gray')
            dfn = array1d2d(dfn[:3])
            df = np.vstack([df,dfn]) if len(df)>0 else dfn
            np.savetxt(img_log, df ,fmt='%s', delimiter=',',encoding='utf-8')
    if len(dfn)>0:
        return dfn[0,1]
    return ''


def img_correct(file,iscorrect,isclean,isfast):
    start = time.time()
    t = img_tika_df(file,iscorrect,isclean,isfast)
    print('----final----- \n',t)
    end = time.time()
    print('Running time: %s Seconds'%(end-start))
    return t

