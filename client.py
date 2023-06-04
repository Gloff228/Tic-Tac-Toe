import socket
import tkinter as tk
from tkinter import messagebox
import threading

player = ''


def connect_to_server():
    try:
        global host
        global port
        global s
        host = "127.0.0.1"  # IP-адрес сервера
        port = 12345  # Порт сервера
        s = socket.socket()
        s.connect((host, port))

        while True:
            response = s.recv(1024).decode()
            if not response:
                break
            global player
            player = response

            start_data_thread()
            break

    except socket.error as msg:
        print("Ошибка при подключении к серверу: " + str(msg))


def send_data(button):
    try:
        message = str(button.row) + ',' + str(button.col)  # Преобразуем координаты кнопки в строку
        s.send(str.encode(message))

    except socket.error as msg:
        print("Ошибка при отправке данных: " + str(msg))


def start_data_thread():
    server_thread = threading.Thread(target=get_data)
    server_thread.start()


def get_data():
    while True:
        response = s.recv(1024).decode()
        if not response:
            break

        data = response.split(',')

        result = data[0]  # принимает информацию о состоянии игры
        board_state = data[1:]  # принимает состояние доски

        if result == "valid":
            # Обновление игрового поля на основе полученного состояния
            update_board(board_state)
        elif result == "invalid":
            messagebox.showerror("Недопустимый ход", "Это поле уже занято. Выберите другое поле.")
        elif result[:7] == "Победил":
            messagebox.showinfo("Игра завершена", result)
            reset_game()
        elif result == "draw":
            messagebox.showinfo("Игра завершена", "Ничья!")
            reset_game()
    s.close()


def update_board(board_state):
    for i, row in enumerate(board_state):
        for j, value in enumerate(row):
            button = buttons[i][j]
            button['text'] = value
            button['state'] = 'disabled' if value != ' ' else 'normal'


def reset_game():
    for row in buttons:
        for button in row:
            button['text'] = ' '
            button['state'] = 'normal'


def handle_button_click(button):
    if button['text'] == ' ':
        send_data(button)


def main():
    connect_to_server()

    # Создаем графическое окно игры
    window = tk.Tk()
    window.title("Игрок " + player)

    # Создаем кнопки для игрового поля
    global buttons
    buttons = []
    for i in range(3):
        row = []
        for j in range(3):
            button = tk.Button(window, text=' ', width=10, height=5)
            button.row = i  # Добавляем атрибуты row и col для хранения координат кнопки
            button.col = j
            button.configure(
                command=lambda b=button: handle_button_click(b))  # Передаем кнопку в функцию handle_button_click
            button.grid(row=i, column=j)
            row.append(button)
        buttons.append(row)

    # Запускаем главный цикл событий
    window.mainloop()


if __name__ == "__main__":
    main()
