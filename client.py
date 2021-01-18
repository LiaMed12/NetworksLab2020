import re
import socket
import json
from threading import Thread
import sys

try:
    IP = sys.argv[1]
except IndexError:
    IP = 'localhost'
try:
    PORT = int(sys.argv[2])
except IndexError:
    PORT = 7777

all_request = {}
CODE = 'utf-8'
BLOCK_LENGTH = 512

OPCODE = {
    '+': 0,
    '-': 1,
    '*': 2,
    '/': 3,
    '!': 4,
    'sqrt': 5,
    'answer': 6
}


def get_answer(recv_request):
    if recv_request['type'] == 0:
        answer = recv_request['answer']
        ident = recv_request['id']
        return answer, ident


def send_recv_request(sock, request):
    try:
        json_request = json.dumps(request).encode(CODE)
        sock.send(json_request)
        recv_message = sock.recv(BLOCK_LENGTH).decode(CODE)
        if recv_message:
            recv_message = json.loads(recv_message)
            answer, ident = get_answer(recv_message)
            if all_request[ident]["operation"] in [0, 1, 2, 3]:
                print(f'{all_request[ident]["arg"][0]} '
                      f'{list(OPCODE.keys())[list(OPCODE.values()).index(all_request[ident]["operation"])]}'
                      f' {all_request[ident]["arg"][1]} = {answer}')
            if all_request[ident]["operation"] == 4:
                print(f'{all_request[ident]["arg"][0]}! = {answer}')
            elif all_request[ident]["operation"] == 5:
                print(f'sqrt({all_request[ident]["arg"][0]}) = {answer}')
            del all_request[ident]
            return answer
        else:
            print('Server is closed')
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            print("Connection closed by the server")
            sys.exit(0)
    except ConnectionResetError:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        print("Connection closed by the server")
        sys.exit(0)


def main():
    i = 0
    print("Calculator client started.")
    try:
        address = (IP, PORT)
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(address)
    except ConnectionRefusedError:
        print('Server is closed')
        return
    while True:
        print("Enter \"0\" - for quick operation(+,-,*,/);\n"
              "Enter \"1\" - for long operation(arg!, sqrt(arg))\n"
              "Enter \"!exit\" - for exit from calculator")
        input_operation = input().replace(" ", "")
        if input_operation:
            if input_operation == '0' or input_operation == "1" or input_operation == "!exit":
                if input_operation == "!exit":
                    print("Goodbye!")
                    return
                elif input_operation == "0":
                    while True:
                        input_message = input("Enter: arg1 +|-|*|/ arg2\n"
                                              "Enter \"!back\" - for back to choose operation.\n")
                        if input_message:
                            if input_message == "!exit":
                                print("Goodbye!")
                                return
                            elif input_message == "!back":
                                break
                            for_check = input_message.replace(" ", "")
                            match_1 = re.match(r"-?(\d+\.)?\d+[+\-*/]-?(\d+\.)?\d+", for_check)
                            if match_1 and len(match_1.group()) == len(for_check):
                                if re.match(r"(\d+\.)?\d+-(\d+\.)?\d+", for_check):
                                    example = for_check.replace('-', ' - ')
                                elif re.match(r"-(\d+\.)?\d+-(\d+\.)?\d+", for_check):
                                    example = '-' + for_check.split('-')[1] + ' - ' + for_check.split('-')[2]
                                elif re.match(r"(\d+\.)?\d+--(\d+\.)?\d+", for_check):
                                    example = for_check.split('-')[0] + ' - ' + '-' + for_check.split('-')[2]
                                elif re.match(r"-(\d+\.)?\d+--(\d+\.)?\d+", for_check):
                                    example = '-' + for_check.split('-')[1] + ' - ' + '-' + for_check.split('-')[3]
                                else:
                                    example = input_message.replace(" ", "").replace('+', ' + ') \
                                        .replace('*', ' * ').replace('/', ' / ')
                            else:
                                print('Your command is wrong')
                                continue
                            ex_arguments = example.split(" ")
                            try:
                                arg1 = float(ex_arguments[0])
                                arg2 = float(ex_arguments[2])
                            except ValueError:
                                print('Arg must be number')
                                continue
                            op = ex_arguments[1]
                            if op not in OPCODE:
                                print('Operation must be +|-|*|/')
                                continue
                            if OPCODE[op] == 3 and arg2 == 0:
                                print('Сan`t be divided by 0')
                                continue
                            request = {'type': int(input_operation), 'operation': OPCODE[op], 'arg': [arg1, arg2],
                                       'id': i}
                            all_request[i] = request
                            i += 1
                            Thread(target=send_recv_request, args=(client_sock, request),
                                   daemon=True).start()
                elif input_operation == "1":
                    while True:
                        input_message = input("Enter: arg! or sqrt(arg)\n"
                                              "Enter \"!back\" - for back to choose operation.\n").replace(' ', '')
                        if input_message:
                            if input_message == "!exit":
                                print("Goodbye!")
                                return
                            elif input_message == "!back":
                                break
                            elif input_message[-1] == '!':
                                try:
                                    arg = int(input_message[:-1])
                                except ValueError:
                                    print('Arg must be integer')
                                    continue
                                op = input_message[-1]
                            elif input_message[-1] == ')':
                                try:
                                    arg = float(input_message[5:-1])
                                except ValueError:
                                    print('Arg must be number')
                                    continue
                                op = input_message[:4]
                            else:
                                print('Your command is wrong\n')
                                continue
                            if arg < 0:
                                print('Arg must be positive')
                                continue
                            request = {'type': int(input_operation), 'operation': OPCODE[op], 'arg': [arg], 'id': i}
                            all_request[i] = request
                            i += 1
                            print('You will get your answer when it is calculated')
                            Thread(target=send_recv_request, args=(client_sock, request),
                                   daemon=True).start()

            else:
                print('Your command is wrong')
                continue


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Client is closed')
