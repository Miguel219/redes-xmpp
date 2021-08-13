import slixmpp
from slixmpp.xmlstream.asyncio import asyncio
from slixmpp.xmlstream.stanzabase import ET 
from aioconsole import ainput
import pandas as pd
from tabulate import tabulate
from settings import *

class Client(slixmpp.ClientXMPP):

    def __init__(self, jid, password, login = True):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.logged = False
        self.nickName = ''
        self.groupjid = ''
        self.status = 'Activo'
        self.received = set()
        self.presences_received = asyncio.Event()

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
        self.register_plugin('xep_0085') # Chat State Notifications
        self.register_plugin('xep_0096') # Jabber Search
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0071')
        self.register_plugin('xep_0128')
        self.register_plugin('xep_0363')


    async def session_start(self, event):
        self.send_presence(pstatus=self.status)
        await self.get_roster()
        
        self.nickName = str(await ainput("Ingresa tu apodo con el que se te vera en todos los grupos: "))

        self.logged = True
        appMenu = 0
        
        while appMenu != 7 and appMenu != 8:
            try:
                appMenu = int(await ainput(""" 
--------------------------------------------------
Ingresa el número de la opción que deseas realizar:
1. Mostrar todos tus contactos y su estado
2. Agregar un usuario a tus contactos
3. Mostrar detalles de un contacto
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
                await self.addContact()
            
            elif(appMenu == 3):
                await self.displayContactInformation()
            
            elif(appMenu == 4):
                await self.sendMessage()
            
            elif(appMenu == 5):
                await self.sendMessageToGroup()
            
            elif(appMenu == 6):
                await self.definePresenceMessage()
            
            elif(appMenu == 7):
                print("Cerrando sesión...")
            
            elif(appMenu == 8):
                await self.deleteUser()
            
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
        if msg['type']  in ('normal', 'chat'):
            print("----------------Notificación----------------------")
            print(f"{msg['from'].username}: {msg['body']}")
            print("--------------------------------------------------")
        
        elif msg['type'] == 'groupchat':
            print("----------------Notificación----------------------")
            print(f"Grupo ({msg['from'].username}): {msg['body']}")
            print("--------------------------------------------------")
        else :
            print(msg)
            
    
    def groupchat_message(self, msg):
        if(msg['mucnick'] != self.nickName and self.nickName in msg['body']):
            print(f"Se te mencionó en el grupo ({msg['from'].username})")

    def muc_online(self, presence):
        # print(presence)
        if presence['muc']['nick'] != self.nickName:
            print(f"{presence['muc']['nick']} esta activo en el grupo ({presence['from'].bare})")


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
    
    
    async def addContact(self):
        try:
            newContact = str(await ainput("JID del usuario: "))
            self.send_presence_subscription(pto=newContact)
            print('Se agrego el usuario al contacto')
        except:
            print('No se pudo agregar el contacto')
    
    async def displayContactInformation(self):

        contact = str(await ainput("JID del usuario: "))
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
    
    async def sendMessage(self):

        contact = str(await ainput("JID del usuario al que deseas enviar mensaje: "))
        
        option = 0
        try:
            option = int(await ainput(""" 
--------------------------------------------------
Ingresa el número de la opción que deseas realizar:
1. Enviar un mensaje 
2. Enviar un archivo
--------------------------------------------------
>"""))
        except: 
            print("Ingresa una opción correcta")
        
        if option == 1:
            print("Mensaje:")
            message = str(await ainput(">")) 
            
            self.send_message(mto=contact,
                            mbody=message,
                            mtype='chat')

        elif option == 2:
            filename = str(await ainput("Dirección del archivo: "))
            domain = str(await ainput("Dominio para subir el archivo: "))
            
            try:
                print('Enviando el archivo...')
                url = await self['xep_0363'].upload_file(
                    filename, domain=domain, timeout=10
                )
                html = (
                    f'<body xmlns="http://www.w3.org/1999/xhtml">'
                    f'<a href="{url}">{url}</a></body>'
                )
                message = self.make_message(mto=contact, mbody=url, mhtml=html)
                message['oob']['url'] = message
                message.send() 
                print('Se envio el archivo correctamente')
            except:
                print('No se logro subir el archivo')
               
    
    async def sendMessageToGroup(self):

        self.groupjid = str(await ainput("Nombre del grupo: "))
      
        self.add_event_handler("muc::%s::got_online" % self.groupjid, self.muc_online)

        self.plugin['xep_0045'].join_muc(self.groupjid, self.nickName)

        option = 0
        try:
            option = int(await ainput(""" 
--------------------------------------------------
Ingresa el número de la opción que deseas realizar:
1. Enviar un mensaje 
2. Enviar un archivo
--------------------------------------------------
>"""))
        except: 
            print("Ingresa una opción correcta")
        
        if option == 1:
            print("Mensaje:")
            message = str(await ainput(">"))
        
            self.send_message(mto=self.groupjid,
                            mbody=message,
                            mtype='groupchat')

        elif option == 2:
            filename = str(await ainput("Dirección del archivo: "))
            domain = str(await ainput("Dominio para subir el archivo: "))
            
            try:
                print('Enviando el archivo...')
                url = await self['xep_0363'].upload_file(
                    filename, domain=domain, timeout=10
                )
                html = (
                    f'<body xmlns="http://www.w3.org/1999/xhtml">'
                    f'<a href="{url}">{url}</a></body>'
                )
                message = self.make_message(mto=self.groupjid, mbody=url, mhtml=html, mtype='groupchat')
                message['oob']['url'] = message
                message.send() 
                print('Se envio el archivo correctamente')
            except:
                print('No se logro subir el archivo')
    
    async def definePresenceMessage(self):

        self.status = str(await ainput("Estado: "))
        
        self.send_presence(pstatus=self.status, pnick=self.nickName)
        await self.get_roster()
    
    async def deleteUser(self):

        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['remove'] = True

        try:
            await resp.send()
            print("Usuario eliminado con éxito!")
        except:
            print("No se puede eliminar el usuario en este momento")
