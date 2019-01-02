# file-batch-renamer Python 批量重命名文件脚本

> a file batch renamer based on python (include Chinese)

- Updated 2019.1.2:
    - 新版 **Apache Tika** 解析全文件版本 
    - 旧版 **Python 3rd party** 解析文件版本

----------------

## Tutorial

### 1. Tika | Tesseract OCR

- Files
    - batch-renamer-tika.py

- Requirements  
    - [zhon](https://pypi.org/project/zhon/) zhon to deal with Chinese
    - [tika](https://pypi.org/project/tika/) tika for python
    - [Java Jre jre-8u91-windows-x64](https://www.oracle.com/technetwork/java/javase/downloads/java-archive-javase8-2177648.html) Jre8 is at least and fitting package
    - [Tesseract v4.0.0.20181030](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-v4.0.0.20181030.exe) Tesseract for Image OCR

- Supported Platform:
    - [x] win7 32bit,win10 64bit,其他没测试过

- Supported Files:
    - [x] docx,pptx,xlsx
    - [x] doc,ppt,xls
    - [x] epub,rar,zip,tar,html,pdf
    - [x] png,jpg,jpeg,bmp,tif
    - [x] others(follows [tika](http://tika.apache.org/1.20/formats.html))

- Usage:
    - 安装必须
        - installplug.bat
        - setenv.bat
    - 要重命名的文件放在当前目录
    - 执行batch-renamer-tika.(py|exe)

#### 2. Python 3rd party | Tesseract OCR

- Files
    - batch-renamer.py
    - extrectImage.py (Author: BJ Jang (jangbi882 at gmail.com))

- Requirements
    - [python-pptx](https://pypi.org/project/python-pptx/) ppt格式
    - [python-docx](https://pypi.org/project/python-docx/) word格式
    - [xlrd](https://pypi.org/project/xlrd/) excel格式
    - [zhon](https://pypi.org/project/zhon/) 提取中文
    - [PyPDF2](https://github.com/mstamy2/PyPDF2) 提取PDF
    - [PDFMiner](https://github.com/euske/pdfminer/) 提取PDF
    - [pytesseract](https://pypi.org/project/pytesseract/) 识别图像

- Supported Platform:
    - [x] win7 32bit,win10 64bit,其他没测试过

- Supported Files:
    - [x] docx,pptx,xlsx
    - [x] doc,ppt,xls
    - [x] pdf
    - [x] png,jpg,jpeg,bmp,tif

- Usage:
    - 安装必须或手动安装包
        - installplug.bat
        - setenv.bat
    - 要重命名的文件放在当前目录
    - 执行batch-renamer.(py|exe)

[![ForTheBadge built-with-science](http://ForTheBadge.com/images/badges/built-with-science.svg)](https://github.com/autolordz/docx-content-modify/blob/master/LICENSE)

That's it,enjoy.
