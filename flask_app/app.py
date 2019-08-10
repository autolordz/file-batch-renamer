from flask import Flask, render_template, request
from nltk.corpus import wordnet as wn
import re,string,json,subprocess,os
import jieba,time
import zhon.hanzi

punc_all = string.punctuation + zhon.hanzi.punctuation

app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    t = request.args.get('t', 'hahahah')
    return render_template('first_app.html',text=t)

def subprocess_cmd(func,file):
    print('cmd:',func(file))
    return subprocess.check_output(func(file),shell=1).decode("utf-8")

def get_curl_tesseract(file):#    os.path.splitext(tmpf)[0]
    return 'tesseract %s stdout -l chi_sim+eng'%(file,)

def remove_file(file):
    if file and os.path.exists(file):
        print('>>> del',file)
        try:
            os.remove(file)
        except Exception as e:
            print(e)

@app.route('/ocr',methods=['POST','PUT'])
def post2():
    s1 = time.time()

#    print("---data---\r\n", request.data)
    print("---files---\n", request.files)
#    print("---stream---\r\n", request.stream.read())
#    print("---form---\r\n", request.form)

    file = request.files['file']

    file.save(file.filename)
    print('files-name:',file.filename)
    t = subprocess_cmd(get_curl_tesseract,file.filename)
    remove_file(file.filename)
    s2 = time.time()
    print('2222 Running time: %s Seconds'%(s2-s1))
    return t

def tika_words_rate2(t,r=0):
    if t:
        t = re.sub(r'[\n%s|0-9]'%punc_all,'',t)
        s1 = time.time()
        j = jieba.lcut(t, cut_all=0,HMM=0)
        s2 = time.time()
        print('Running time: %s Seconds'%(s2-s1))

        s1 = time.time()
        wa = list(filter(lambda x:len(x)>1,j))
        if len(wa)==0:
            wa = list(filter(None,j))
        ws = list(filter(None,[w if wn.synsets(w,lang='eng') \
#             or wn.synsets(w,lang='jpn') \
             or wn.synsets(w,lang='cmn') \
             else None for w in wa]))

        s2 = time.time()
        print('Running time: %s Seconds'%(s2-s1))
        r = len(ws)/(len(wa)+.1)
    return r

@app.route('/',methods=['POST'])
def post1():
    s1 = time.time()
    j = request.get_json()
    if j:
        t = j.get('t', 'no txt !!')
    else:
        t = request.get_data(as_text=1)

    print('flask t= \n',t)
    r = tika_words_rate2(t)
    s2 = time.time()
    print('2222 Running time: %s Seconds'%(s2-s1))
    return json.dumps({'rate':r})

if __name__ == '__main__':
    app.run(debug=1,host='127.0.0.1',port=2121)
