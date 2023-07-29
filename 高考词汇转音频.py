import multiprocessing
import os
import edge_tts
import asyncio
import requests
import random
import json
from hashlib import md5
from multiprocessing import Process, Pool, freeze_support
from lxml import etree
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Referer": "http://www.iciba.com/"
}
url = "http://www.iciba.com/word?w="

VOICE = "zh-CN-XiaoyiNeural"  
OUTPUT_FILE =  os.path.realpath(__file__)
OUTPUT_FILE = OUTPUT_FILE.replace('高考词汇转音频.py','')

from_lang = 'en'
to_lang =  'zh'
endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path
query = 'abandon'
appid = '' #自己在百度开放平台找
appkey = '' #同上

def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


async def my_function(TEXT):
    communicate = edge_tts.Communicate(TEXT, VOICE,rate="+50%")  
    await communicate.save(OUTPUT_FILE+'音频/'+TEXT+'.mp3')  

#读取文件
with open(OUTPUT_FILE + '高考词汇.txt' , encoding='utf-8') as f1:
    高考词汇 = f1.readlines()
#去除换行符
for i in range(len(高考词汇)):
    高考词汇[i] = 高考词汇[i].strip('\n')
#获取数列长度
length = len(高考词汇)
#创建空白mp3文件
k = " "
#创建文档说明已写入单词
已完成1=open(OUTPUT_FILE + '已完成1.txt','a')
已完成1.write('已写入单词：\n')
已完成2=open(OUTPUT_FILE + '已完成2.txt','a')
已完成2.write('已写入单词：\n')
空白 = open(OUTPUT_FILE + '1空白.mp3','rb')
#循环

def 翻译1(i,中文):
    query = 高考词汇[i]
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    print(result)
    中文[i]=result["trans_result"][0]["dst"]
    print(高考词汇[i]+'的结果为'+中文[i])

def 翻译2(i):
    query = i
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    print(result)
    return result["trans_result"][0]["dst"]





def run_a_sub_proc(v):
    #如果文件存在则跳过
    if os.path.exists(OUTPUT_FILE+'音频/'+v[0]+'.mp3'):
        print('已存在'+v[0])
    else:
        print('开始'+v[0])
        url = "http://dict.youdao.com/dictvoice?type=1&audio=" + v[0]
        r = requests.get(url,headers=headers)
        with open(OUTPUT_FILE+'音频/'+v[0]+'.mp3','wb') as f2:
            f2.write(r.content)
        f2.close()
        print('完成'+v[0])
        已完成1.write(v[0])
    
    if os.path.exists(OUTPUT_FILE+'音频/'+v[1]+'.mp3'):
        print('已存在'+v[1])
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(my_function(v[1]))
    
    if os.path.exists(OUTPUT_FILE+'音频/'+v[2]+'.mp3'):
        print('已存在'+v[2])
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(my_function(v[2]))
        
        

def 翻译(i,中文):
    中文[i]=字典[高考词汇[i]]
    print(高考词汇[i]+'的结果为'+中文[i])
    if 中文[i] == '':
        翻译1(i,中文)

if __name__ == "__main__":
    #初始化字典
    with open(OUTPUT_FILE + '简明英汉词典.txt',encoding='utf-8') as f:
        词性 = ['vi.','vt.','n.','adj.','adv.','pron.','prep.','conj.','art.','num.','int.','v']
        初始 = f.readlines()
        for i in range(len(初始)):
            初始[i] = 初始[i].strip('\n')
        print(初始[100])
        #使用逗号分割单词和中文
        for i in range(len(初始)):
            初始[i] = 初始[i].split(',')
            if len(初始[i]) > 2:
                for j in range(len(初始[i])-2):
                    初始[i][1] = 初始[i][1] + ',' + 初始[i][j+2]
                初始[i] = 初始[i][0:2]
        print(初始[100][1])

    #移出中文中的英文
    for i in range(len(初始)):
        初始[i][1] = re.sub('\"','',初始[i][1])
        #点 = 初始[i][1].find('.')
        #if 点 != -1:
        #    初始[i][1] = 初始[i][1][点+1:]
        for j in range(len(词性)):
            初始[i][1] = 初始[i][1].replace(词性[j],'')
    print(初始[100][1])
    #创建字典
    字典 = {}
    
    for i in range(len(初始)):
        字典[初始[i][0]] = 初始[i][1]
    print(字典['abandon'])
    print('字典初始化完成')
    #从字典中获取翻译

    中文 = {}

    for i in range(length):
        if 高考词汇[i] in 字典:
            if len(字典[高考词汇[i]]) <= 12:
                中文[i]=字典[高考词汇[i]]
                print(高考词汇[i]+'的结果为'+中文[i])
            else:
                字典[高考词汇[i]]= 翻译2(高考词汇[i])
                中文[i]=字典[高考词汇[i]]
        else:
            字典[高考词汇[i]]= 翻译2(高考词汇[i])
            中文[i]=字典[高考词汇[i]]
    print('翻译完成')
    #保存字典
    with open(OUTPUT_FILE + '字典.txt','w',encoding='utf-8') as f:
        f.write(str(字典))
    
    print(中文)
    #创建进程池
    '''
    中文 = multiprocessing.Manager().dict()
    print('开始翻译')
    p3 = Pool(12)
    for i in range(length):
        p3.apply_async(翻译, args=(i,中文,))
    p3.close()
    p3.join()
    print(中文)
    '''
    
    词汇表 = [[高考词汇[0],k.join(高考词汇[0]),中文[0]],[高考词汇[1],k.join(高考词汇[1]),中文[1]]]
    for i in range(2,length):
        
        词汇表.append([高考词汇[i],k.join(高考词汇[i]),中文[i]])
        print(词汇表[i])
    #保存词汇表
    with open(OUTPUT_FILE + '词汇表.txt','w',encoding='utf-8') as f:
        f.write(str(词汇表))
    print('词汇表保存完成')
    p2 = Pool(12)
    for i in range(length):
        p2.apply_async(run_a_sub_proc, args=(词汇表[i],))
    p2.close()
    p2.join()

    f3 = open(OUTPUT_FILE + '1合成.mp3','ab')

    for i in range(length):
        c1 = open(OUTPUT_FILE+'音频/'+词汇表[i][0]+'.mp3','rb')
        c2 = open(OUTPUT_FILE+'音频/'+词汇表[i][1]+'.mp3','rb')
        c3 = open(OUTPUT_FILE+'音频/'+词汇表[i][2]+'.mp3','rb')
        f3.write(c1.read())
        f3.write(c2.read())
        f3.write(c1.read())
        f3.write(c2.read())
        f3.write(c3.read())
        f3.write(c1.read())
        c1.close()
        c2.close()
        c3.close()
        f3.write(空白.read())
        已完成2.write(词汇表[i][0])


    



'''
with open(OUTPUT_FILE + '1合成.mp3','ab') as f3:
    for i in range(length):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(my_function(高考词汇[i]))
        拼读 = k.join(高考词汇[i])
        loop.run_until_complete(my_function(拼读))
        query = 高考词汇[i]
        salt = random.randint(32768, 65536)
        sign = make_md5(appid + query + str(salt) + appkey)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()
        中文=result["trans_result"][0]["dst"]
        print(中文)
        loop.run_until_complete(my_function(中文))
        c1 = open(OUTPUT_FILE+高考词汇[i]+'.mp3','rb')
        c2 = open(OUTPUT_FILE+拼读+'.mp3','rb')
        c3 = open(OUTPUT_FILE+中文+'.mp3','rb')
        f3.write(c1.read())
        f3.write(c2.read())
        f3.write(c1.read())
        f3.write(c2.read())
        f3.write(c3.read())
        f3.write(c1.read())
        c1.close()
        c2.close()
        c3.close()
        f3.write(空白.read())
        已完成.write(高考词汇[i])
'''

#print('已完成')



        


'''
#for i in range(length):
#    高考词汇拼读[i] = k.join(高考词汇[i])
'''