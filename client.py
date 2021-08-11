import slixmpp
from slixmpp.xmlstream.asyncio import asyncio
from slixmpp.xmlstream.stanzabase import ET 
import pandas as pd
from tabulate import tabulate
from settings import *

class Client(slixmpp.ClientXMPP):

    def __init__(self, jid, password, login = True):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        if not login:
            self.add_event_handler("register", self.register)
        
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("changed_status", self.wait_for_presences)
        self.add_event_handler("message", self.message)
        self.add_event_handler("groupchat_message", self.groupchat_message)

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0096') # Jabber Search
        
        self.logged = False
        self.groupName = ''
        self.status = 'Activo'
        self.received = set()
        self.presences_received = asyncio.Event()


    async def session_start(self, event):
        self.send_presence(pstatus=self.status)
        await self.get_roster()
        
        self.logged = True
        appMenu = 0
        
        while appMenu != 7 and appMenu != 8:
            try:
                appMenu = int(input(""" 
--------------------------------------------------
Ingresa el número de la opción que deseas realizar:
1. Mostrar todos tus contactos y su estado
2. Agregar un usuario a tus contactos
3. Mostrar detalles de un contacto de un usuario
4. Enviar un mensaje directo
5. Enviar un mensaje a un grupo
6. Definir mensaje de presencia
7. Cerrar Sesión
8. Eliminar mi usuario
--------------------------------------------------
>"""))
            except: 
                appMenu = 0
                print("Ingresa una opción correcta")                
      
            self.send_presence(pstatus=self.status)
            await self.get_roster()

            if(appMenu == 1):
                await self.displayContactsList()

            elif(appMenu == 2):
                self.addContact()
            
            elif(appMenu == 3):
                await self.displayContactInformation()
            
            elif(appMenu == 4):
                self.sendMessage()
            
            elif(appMenu == 5):
                self.sendMessageToGroup()
            
            elif(appMenu == 6):
                await self.definePresenceMessage()
            
            elif(appMenu == 7):
                print("Cerrando sesión...")
            
            elif(appMenu == 8):
                print("8")
            
            elif(appMenu != 0):
                print("Ingresa una opción correcta")
        
        #Se cierra sesion
        self.disconnect()

    async def register(self, iq):
        msg = self.Iq()
        msg['type'] = 'set'
        msg['register']['username'] = self.boundjid.user
        msg['register']['password'] = self.password

        try:
            await msg.send()
            print("Cuenta creada!")
        except:
            print("Error al crear cuenta, intenta con cambiar el nombre del usuario")
            self.disconnect()

    def wait_for_presences(self, pres):

        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()

    def message(self, msg):
        print("Tienes un mensaje nuevo:")
        if msg['type'] in ('chat'):
            print(f"{msg['from'].username}: {msg['body']}")
    
    def groupchat_message(self, msg):
        if(str(msg['from']).split('/')[1]!=self.groupName):
            print(str(msg['from']).split('/')[1] + ": " + msg['body'])
            message = input("Write the message: ")
            self.send_message(mto=msg['from'].bare,
                              mbody=message,
                              mtype='groupchat')

    async def displayContactsList(self):

        contacts = []
        
        await asyncio.sleep(SLEEP)

        roster = self.client_roster.groups()
        for group in roster:
            for jid in roster[group]:
                status = 'Inactivo'
                conexions = self.client_roster.presence(jid)                           
                for answer, pres in conexions.items():
                    if pres['status']:
                        status = pres['status']

                contacts.append([
                    jid,
                    status
                ])
                contacts

        if len(contacts)==0:
            print('No hay ningún usuario conectado')
        else:
            df = pd.DataFrame(contacts, columns = ['JID', 'Estado'])
            print(tabulate(df, headers='keys', tablefmt='psql'))
    
    
    def addContact(self):
        try:
            newContact = str(input("JID del usuario: "))
            self.send_presence_subscription(pto=newContact)
            print('Se agrego el usuario al contacto')
        except:
            print('No se pudo agregar el contacto')
    
    async def displayContactInformation(self):

        contact = str(input("JID del usuario: "))
        contacts = []
        
        await asyncio.sleep(SLEEP)

        roster = self.client_roster.groups()
        for group in roster:
            for jid in roster[group]:
                status = 'Inactivo'
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                conexions = self.client_roster.presence(jid)                           
                for res, pres in conexions.items():
                    if pres['status']:
                        status = pres['status']
                if contact == jid:
                    contacts.append([
                        jid,
                        name,
                        sub,
                        status
                    ])
                contacts

            df = pd.DataFrame(contacts, columns = ['JID', 'Nombre', 'Suscripción', 'Estado'])
            print(tabulate(df, headers='keys', tablefmt='psql'))
    
    def sendMessage(self):

        contact = str(input("JID del usuario al que deseas enviar mensaje: "))
        print("Mensaje:")
        message = str(input(">"))
        
        self.send_message(mto=contact,
                          mbody=message,
                          mtype='chat')
    
    def sendMessageToGroup(self):

        self.groupName = str(input("Nombre del grupo: "))
        groupjid = self.groupName + "@conference.alumchat.xyz"
        print("Mensaje:")
        message = str(input(">"))
        
        self.send_message(mto=groupjid,
                          mbody=message,
                          mtype='groupchat')
    
    def sendMessageToGroup(self):

        self.groupName = str(input("Nombre del grupo: "))
        groupjid = self.groupName + "@conference.alumchat.xyz"
        print("Mensaje:")
        message = str(input(">"))
        
        self.send_message(mto=groupjid,
                          mbody=message,
                          mtype='groupchat')
    
    async def definePresenceMessage(self):

        self.status = str(input("Estado: "))
        self.nickName = str(input("Apodo: "))
        
        self.send_presence(pstatus=self.status, pnick=self.nickName)
        await self.get_roster()