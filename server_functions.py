import sys
import threading
from json import JSONDecodeError

from dbFunctions import *
from filter import *
import signal
from utils import  *

def server_insertion(clientsocket, lock,ip,client_opt):

    clientsocket.send(messages.OPT_ADD_TICK.encode())

    ticketrecv = clientsocket.recv(1024)

    decoded_t = recvJson(ticketrecv.decode())

    addTicket(decoded_t, lock)

    clientsocket.send(messages.TCKT_CREATED.encode())

    generateHistory(ip, client_opt.decode())

    os.kill(os.getpid(), signal.SIGUSR1)

def server_list(clientsocket,ip,client_opt):

    clientsocket.send(messages.OPT_LIST_TICK.encode())

    client_filters = clientsocket.recv(1024)

    data_ticket = clientsocket.recv(1024)

    client_filters = client_filters.decode()

    filters_decoded = json.loads(client_filters)

    data_ticket = recvJson(data_ticket.decode())

    result = filterAction(filters_decoded, data_ticket)

    result = str(result)

    clientsocket.send(result.encode())

    print(messages.TCKTS_LISTED, ip)

    generateHistory(ip, client_opt.decode())

def server_editTicket(clientsocket,ip,client_opt ,current_ids):

    event = threading.Event()

    clientsocket.send(messages.OPT_EDIT_TICK.encode())

    recievingId = clientsocket.recv(1024)

    recievingId = recievingId.decode()

    ticketexists = existsTicket(recievingId)

    if ticketexists == True:

        msg = "EXISTS"

        clientsocket.send(msg.encode())

        modifiers = clientsocket.recv(1024)

        data_ticket = clientsocket.recv(1024)

        modifiers = modifiers.decode()

        modifiers_decoded = json.loads(modifiers)

        data_ticket = recvJson(data_ticket.decode())

        params_applied = editionFiltred(recievingId, modifiers_decoded, data_ticket)

        if recievingId in current_ids:

            print(messages.TCKTS_SAME,recievingId)

            event.clear()

        elif recievingId not in current_ids:

            event.set()

            current_ids.append(recievingId)

            print(messages.TCKTS_EDITING, current_ids)

        while event.is_set():

            editTicket(recievingId, params_applied)

            print(messages.TCKT_EDITED, ip)

            event.clear()

        time.sleep(3)

        edited_ticket = getTicketbyId(recievingId)

        clientsocket.send(dumpTicket(edited_ticket).encode())

        try:

            current_ids.remove(recievingId)

        except ValueError:
            pass

    else:

        clientsocket.send(messages.ERR_MSG_NOAVAILABLE.encode())

    generateHistory(ip, client_opt.decode())

def server_exportTicket(clientsocket,ip,client_opt):

    clientsocket.send(messages.OPT_EXPORT_TICK.encode())

    client_filters = clientsocket.recv(1024)

    data_ticket = clientsocket.recv(1024)

    client_filters = client_filters.decode()

    filters_decoded = json.loads(client_filters)

    data_ticket = recvJson(data_ticket.decode())

    result = filterAction(filters_decoded, data_ticket)

    result = str(result)

    clientsocket.send(result.encode())

    print(messages.NEW_PROCESS, ip)

    generateHistory(ip, client_opt.decode())

def server_clear(ip,client_opt):

    print(messages.CLIENT_CLEARED, ip)

    generateHistory(ip, client_opt.decode())
