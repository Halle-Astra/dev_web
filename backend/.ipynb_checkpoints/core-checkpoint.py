"""
用于与终端交互
"""
import json
from threading import Thread 
from queue import Queue 
from fastapi import FastAPI, Request, Cookie
from pydantic import BaseModel
import subprocess
import shlex
import uvicorn
import random
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import platform
from loguru import logger 
import sys 
logger.remove()
logger.add(sys.stdout, level='DEBUG')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key='HalleAstra')

# Some global Variables 
simple_session = {}

class Custom_Cookie(BaseModel):
    session: str

class Request_With_Cookie(Request):
    cookie: Custom_Cookie

class DataFetchThread(Thread):
    def __init__(self, inp, q):
        super().__init__() 
        self.inp = inp 
        self.q = q

    def run(self):
        while True:
            data = self.inp.readline()
            self.q.put(data)

class PopenManager:
    def __init__(self, cmd=None, qsize=100000):
        if cmd is None:
            platform_name = platform.system()
            if platform_name == 'Windows':
                cmd = 'Powershell'
            elif platform_name == 'Linux':
                cmd = '/bin/bash' 
            else:
                logger.info('Your system neither Win nor Linux, so will run the Python process for you.')
                cmd = 'python3'
        self.p = subprocess.Popen([cmd], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.queue_output = Queue(maxsize=qsize)
        
        self.fetcher = DataFetchThread(self.p.stdout, self.queue_output)
        self.fetcher.start() 

        self.queue_err = Queue(maxsize = qsize)
        self.err_fetcher = DataFetchThread(self.p.stderr, self.queue_err)
        self.err_fetcher.start()

        self.cmd_count = 0
        self.end_mark = "\<end!\>"

    def input_unit(self, s_u):
        self.p.stdin.write(s_u+'\n')
        self.p.stdin.flush()

    def input(self, string):
        # self.queue.put(string)
        string_ls = string.split('&&') 
        string_ls = [i.strip() for i in string_ls if i.strip()] 
        for string_unit in string_ls:
            self.input_unit(string_unit)

        self.cmd_count+=1 
        self.input_unit('echo '+self.end_mark+' '+str(self.cmd_count)) # 只能用这种方法来传递是否完成命令了，这样子可以保证子进程内的规则时顺序执行的。

    def get_info_from_queue(self, q):
        qsize = q.qsize() 
        output_v = []
        for i in range(qsize):
            output_v.append(q.get())
        output_v = '\n'.join(output_v)
        return output_v 


@app.post("/create")
async def create_object(request:Request_With_Cookie): # 事实上真正起作用的是在前端传cookie
    logger.debug("create被访问")
    session = request.session
    logger.debug("session ", session)
    # p = subprocess.Popen(['python', '-c', 'while True: pass'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if 'c_id' in session and session['c_id'] in simple_session:
        logger.debug("这个是旧session，成功保持session")
        logger.info("current processes: {}".format(simple_session))
    else:
        while True:
            t = random.randint(0,10)
            if t not in simple_session:
                p = PopenManager()            
                simple_session[t] = {}
                simple_session[t]['process'] = p
                session['c_id'] = t
                break

    return json.dumps({"message": "Process created and stored in session, current processes have {}".format(len(simple_session))})

@app.post('/assign')
async def submit(request:Request):
    c_id = request.session['c_id']
    p = simple_session[c_id]['process'] 
    data = await request.json()
    cmd = data['cmd']
    logger.debug("the request json is {}".format(data))
    p.input(cmd)

    o = p.get_info_from_queue(p.queue_output)
    e = p.get_info_from_queue(p.queue_err)

    ret = dict(output = o, err = e)
    return json.dumps(ret)
    
    



if __name__ == '__main__':
    uvicorn.run(app=app, host='127.0.0.1', port=8100)
