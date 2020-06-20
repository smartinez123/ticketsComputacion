import sys

import cliController
import multiprocessing
import messages
from jsonService import *
import time

from utils import *


def exportTickets(socket,filtersapplied,ticketData):

    socket.send(filtersapplied.encode())

    socket.send(ticketData.encode())

    ticket_search = socket.recv(1024)

    ticket_search = ticket_search.decode()

    list_tickets = eval(ticket_search)

    generateCSV(list_tickets)

    print(messages.CLIENT_EXPORT_SUCCESS)

def main_execution(client):

    while True:

        try:

            destination = cliController.mainClientCLI()

            if destination == "INSERT":

                clearTerminal()

                client.send(destination.encode())

                print(client.recv(1024).decode())

                cliTick = cliController.clientAddCLI()

                try:

                    ticket = {'title': cliTick[0], 'author': cliTick[1], 'description': cliTick[2]}

                    client.send(sendJson(ticket).encode())

                    print(client.recv(1024).decode())

                except IndexError:

                    print(messages.ERR_MSG_INPUT)

                    break


            elif destination == "LIST":

                client.send(destination.encode())

                clearTerminal()

                print(client.recv(1024).decode())

                filtersapplied, ticketData = cliController.clientListCLI()

                filtersapplied = sendJson(filtersapplied)

                ticketData = sendJson(ticketData)

                client.send(filtersapplied.encode())

                client.send(ticketData.encode())

                ticket_search = client.recv(1024)

                ticket_search = ticket_search.decode()

                list_tickets = eval(ticket_search)

                printableTicket(list_tickets)

            elif destination == "EDIT":

                clearTerminal()

                client.send(destination.encode())

                print(client.recv(1024).decode())

                modifiers, ticket_toedit = cliController.cliientEditCLI()

                correct_input_id = idValidator(ticket_toedit['id'])

                if correct_input_id:

                    id = ticket_toedit['id']

                    modifiers = sendJson(modifiers)

                    ticket_toedit = sendJson(ticket_toedit)

                    client.send(str(id).encode())

                    if client.recv(1024).decode("utf-8") == "EXISTS":

                        client.send(modifiers.encode())

                        client.send(ticket_toedit.encode())

                        editedTicket = client.recv(1024)

                        print(recvJson(editedTicket.decode()))

                    else:
                        print(messages.ERR_MSG_NOAVAILABLE)
                else:
                    break



            elif destination == "EXPORT":

                client.send(destination.encode())

                clearTerminal()

                print(client.recv(1024).decode())

                filtersapplied, ticketData = cliController.clientListCLI()

                filtersapplied = sendJson(filtersapplied)

                ticketData = sendJson(ticketData)

                paralell_p = multiprocessing.Process(target=exportTickets, args=(client, filtersapplied, ticketData,))

                paralell_p.start()

                time.sleep(2)

                paralell_p.join()

            elif destination == "CLEAR":

                clearTerminal()

                client.send(destination.encode())

            elif destination == "EXIT":

                clearTerminal()

                client.send(destination.encode())

                break
            else:

                print(messages.OPT_WRONG)

        except KeyboardInterrupt or EOFError or BrokenPipeError:

            if KeyboardInterrupt:

                print("\n", messages.KYBRD_INTERRUPT)

            elif EOFError:

                print("\n", messages.EOFE)

            elif BrokenPipeError:
                print("\n",messages.ERR_MSG_BP)

            sys.exit()



    """ client.settimeout(0.5)

           try:

               message = client.recv(1024).decode()
               if not message: break
           except socket.timeout:
               pass
           """

