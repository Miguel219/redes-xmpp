import slixmpp
from slixmpp.xmlstream.asyncio import asyncio
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

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0096') # Jabber Search
        
        self.logged = False
        self.received = set()
        self.presences_received = asyncio.Event()


    async def session_start(self, event):
        self.send_presence(pstatus='Conectado')
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
                print("Ingresa una opción correcta")                
      
            self.send_presence(pstatus='Conectado')
            await self.get_roster()

            if(appMenu == 1):
                await self.displayContactsList()

            elif(appMenu == 2):
                self.addContact()
            
            elif(appMenu == 3):
                await self.displayContactInformation()
            
            elif(appMenu == 4):
                print("4")
            
            elif(appMenu == 5):
                print("5")
            
            elif(appMenu == 6):
                print("6")
            
            elif(appMenu == 7):
                print("Cerrando sesión...")
            
            elif(appMenu == 8):
                print("8")
            
            else:
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

    async def displayContactsList(self):

        contacts = []
        
        await asyncio.sleep(SLEEP)

        roster = self.client_roster.groups()
        for group in roster:
            for jid in roster[group]:
                status = 'Desconectado'
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
                status = 'Desconectado'
                info = ''
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                conexions = self.client_roster.presence(jid)                           
                for res, pres in conexions.items():
                    show = 'available'
                    if pres['show']:
                        show = pres['show']
                        info = str(res) + ' (' + str(show) + ')'
                    if pres['status']:
                        status = pres['status']
                if contact == jid:
                    contacts.append([
                        jid,
                        name,
                        sub,
                        status,
                        info
                    ])
                contacts

            df = pd.DataFrame(contacts, columns = ['JID', 'Nombre', 'Suscripción', 'Estado', 'Res'])
            print(tabulate(df, headers='keys', tablefmt='psql'))
