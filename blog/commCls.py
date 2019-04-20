#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 07:28:33 2019

@author: mulya
"""
from threading import Thread
class myThread(Thread):
    def __init__(self,ws,chat_key,chat_iv,threadProc):
        Thread.__init__(self)
        self.threadProc = threadProc
        self.ws = ws
        self.chat_key = chat_key
        self.chat_iv = chat_iv

    def run(self):
        self.threadProc(self.ws,self.chat_key,self.chat_iv)

class wscomm:
    from .consumers import ChatConsumer
    import websocket,json,time
    from .enc_dec import encrypt,decrypt
    loop_exp = 15       #seconds

    def __init__(self,domain,room_name,chat_key,chat_iv):
        self.room_name = room_name
        self.domain = domain
        self.chat_key = chat_key
        self.chat_iv = chat_iv
        self.ChatConsumer({'url_route':{'kwargs':{'room_name':self.room_name}}})
        self.sentLs = []
        self.receivedLs = []
        self.startWS()
        print('CONNECTING')     #TO BE DELETED
        self.rcv_thrd = myThread(self.wS,self.chat_key,self.chat_iv,self.receive_chat)
        self.rcv_thrd.start()

    def startWS(self):
        self.ChatConsumer({'url_route':{'kwargs':{'room_name':self.room_name}}})
        self.connectWS()
        
    def connectWS(self):
        try:
            self.wS = self.websocket.create_connection('wss://'+self.domain+'/ws/chat/'+self.room_name+'/')    #how to detect http/https protocol?
        except self.websocket._exceptions.WebSocketBadStatusException:
            self.ChatConsumer({'url_route':{'kwargs':{'room_name':self.room_name}}})
            self.wS = self.websocket.create_connection('wss://'+self.domain+'/ws/chat/'+self.room_name+'/')    #how to detect http/https protocol?

    def sendWS(self,message):
        from .enc_dec import encrypt
        success = [True,'']
        loop = True
        while loop:
            try:
                self.wS.send(encrypt(self.json.dumps({'message':message}),self.chat_key,self.chat_iv))
                self.sentLs.append(message)
                loop = False
            except (ConnectionResetError,BrokenPipeError):
                print('RECONNECTING')     #TO BE DELETED
                self.connectWS()
            except self.websocket._exceptions.WebSocketConnectionClosedException:
                print('RESTARTING')     #TO BE DELETED
                self.startWS()
            except Exception as er:
                success = [False,str(er)]
                print('ERROR:',er)     #TO BE DELETED
                loop = False
        return success

    def receiveWS(self):
        success = [False,'Response timeout']
        result,loop,start_time = '',True,self.time.time()
        ct =0
        while loop and self.time.time()-start_time<self.loop_exp:
            ct+=1
            #if ct%1000==0:print('loop receivedLs:',self.receivedLs)
            if self.receivedLs:
                result = self.receivedLs[0]
                self.receivedLs = self.receivedLs[1:]
                loop = False
                success = [True,'']
        return success,result

    def receive_chat(self,ws,chat_key,chat_iv):
        from .enc_dec import decrypt
        print('receive_chat started!!')
        while True:
            try:
                msg = self.json.loads(decrypt(ws.recv(),chat_key,chat_iv))
                self.receivedLs.append(msg['message'])
                print('receivedLs:',self.receivedLs)
            except:
                continue
