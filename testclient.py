import sys
import threading
import time
from tkinter import messagebox, Tk

from PyQt5.QtWidgets import *
from PyQt5 import uic
from socket import *
from threading import *
import json

form_class = uic.loadUiType("main_temp.ui")
ip = '10.10.21.108'
port = 9000


class WindowClass(QMainWindow, form_class[0]):
    def __init__(self, sip, sport):
        super().__init__()
        self.setupUi(self)
        self.show()
        # self.변수선언 및 초기화
        self.ip = sip
        self.Client.setCurrentIndex(0)
        # 시그널 - 메서드
        self.make_room.clicked.connect(self.roommake)
        self.set_nickname.clicked.connect(self.nickmake)
        self.room_list.clicked.connect(self.room_move)
        self.member.clicked.connect(self.show_member)
        self.invite.clicked.connect(self.show_guest)
        print('안돼')
        # 서버에 통신 연결
        self.c = socket(AF_INET, SOCK_STREAM)
        self.c.connect((sip, sport))
        print('왜')
        # 스레드 동작
        cth = Thread(target=self.reception, args=(self.c,), daemon=True)
        cth.start()

    def reception(self, c):
        while True:
            try:
                r_msg = c.recv(1024)
                r_msg = json.loads(r_msg.decode())
                print('main', r_msg)
            except:
                break
            if r_msg[0] == '초기닉네임':
                if r_msg == '닉네임을 설정해주세요.':
                    self.nickname.setText(f'{r_msg[1]}')
                else:
                    self.nickname.setText(f'{r_msg[1]}님 환영합니다.')
            elif r_msg[0][0] == '닉네임':
                if r_msg[1] == 'True':
                    self.nickname.setText(f'{r_msg[0][1]}님 환영합니다.')
                    self.nickname_input.clear()
                else:
                    tk_window = Tk()
                    tk_window.geometry("0x0+3000+6000")
                    messagebox.showinfo('닉네임 중복', '이미 존재하는 닉네임입니다.')
                    tk_window.destroy()
                    self.nickname_input.clear()
            elif r_msg[0] == '목록':
                self.accessor_list.clear()
                self.room_list.clear()
                for i in r_msg[1]:
                    self.accessor_list.addItem(f'{i[1]}[{i[0]}, {i[2]}]')
                for i in r_msg[2]:
                    self.room_list.addItem(f'{i[0]}번 방, {i[1]}님의 방입니다.')
            elif r_msg[0] == '방생성':
                if r_msg[1] == 'True':
                    print(f'{r_msg[2]}방 생성')
                    self.Client.setCurrentIndex(1)
                    self.new_port(self.ip, r_msg[2])
                else:
                    tk_window = Tk()
                    tk_window.geometry("0x0+3000+6000")
                    messagebox.showinfo('생성 불가', '이미 생성된 방이 있습니다.')
                    tk_window.destroy()
            elif r_msg[0] == '방이동':
                self.Client.setCurrentIndex(1)
                self.new_port(self.ip, r_msg[1])
            else:
                print('접속 종료')
                break

    def room_move(self):
        room = self.room_list.currentItem().text()
        msg = json.dumps(['방이동', room[0]])
        self.c.sendall(msg.encode())

    def new_port(self, new_ip, new_port):
        self.c = socket(AF_INET, SOCK_STREAM)
        self.c.connect((new_ip, new_port))
        cth = Thread(target=self.sub_reception, args=(self.c,), daemon=True)
        cth.start()


    # 방만들기
    def roommake(self):
        msg = json.dumps(['방만들기'])
        self.c.sendall(msg.encode())

    # 닉네임 설정 하기
    def nickmake(self):
        nick = self.nickname_input.text()
        if nick:
            msg = json.dumps(['닉네임', nick])
            self.c.sendall(msg.encode())

    def sub_reception(self, c):
        while True:
            try:
                r_msg = c.recv(1024)
                r_msg = json.loads(r_msg.decode())
                print('sub', r_msg)
            except:
                break
            if r_msg[0] == '목록':
                self.member_list.clear()
                for i in r_msg[1]:
                    self.member_list.addItem(f'{i[1]}[{i[0]}, {i[2]}]')
            elif r_msg[0] == '초대목록':
                self.member_list.clear()
                for i in r_msg[1]:
                    self.member_list.addItem(f'{i[1]}[{i[0]}, {i[2]}]')

    def show_member(self):
        msg = json.dumps(['목록'])
        self.c.sendall(msg.encode())

    def show_guest(self):
        msg = json.dumps(['초대목록'])
        self.c.sendall(msg.encode())

    def closeEvent(self, e):
        msg = json.dumps(['나감'])
        self.c.sendall(msg.encode())
        self.c.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass(ip, port)
    app.exec_()
