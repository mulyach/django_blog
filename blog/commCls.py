#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 07:28:33 2019

@author: mulya
"""
class wscomm:
    from .consumers import ChatConsumer
    import websocket,json
    from .enc_dec import encrypt,decrypt

    def __init__(self,domain,room_name):
        self.room_name = room_name
        self.domain = domain
        self.ChatConsumer({'url_route':{'kwargs':{'room_name':self.room_name}}})
        self.sentLs = []
        self.startWS()
        print('CONNECTING')     #TO BE DELETED

    def startWS(self):
        self.ChatConsumer({'url_route':{'kwargs':{'room_name':self.room_name}}})
        self.connectWS()
        
    def connectWS(self):
        try:
            self.wS = self.websocket.create_connection('wss://'+self.domain+'/ws/chat/'+self.room_name+'/')    #how to detect http/https protocol?
        except self.websocket._exceptions.WebSocketBadStatusException:
            self.ChatConsumer({'url_route':{'kwargs':{'room_name':self.room_name}}})
            self.wS = self.websocket.create_connection('wss://'+self.domain+'/ws/chat/'+self.room_name+'/')    #how to detect http/https protocol?

    def sendWS(self,message,chat_key,chat_iv):
        from .enc_dec import encrypt
        success = [True,'']
        loop = True
        while loop:
            try:
                self.wS.send(encrypt(self.json.dumps({'message':message}), chat_key,chat_iv))
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

    def receiveWS(self,chat_key,chat_iv):
        from .enc_dec import decrypt
        success = [True,'']
        result,loop = '',True
        while loop:
            try:
                result = self.json.loads(decrypt(self.wS.recv(), chat_key,chat_iv))['message']
            except (ConnectionResetError,BrokenPipeError):
                print('RECONNECTING')     #TO BE DELETED
                self.connectWS()
            except self.websocket._exceptions.WebSocketConnectionClosedException:
                print('RESTARTING')     #TO BE DELETED
                self.startWS()
            except Exception as er:
                success = [False,str(er)]
                print('ERROR',er)     #TO BE DELETED
                loop = False
            if result in self.sentLs:
                self.sentLs.remove(result)
            else:
                loop = False
        return success,result