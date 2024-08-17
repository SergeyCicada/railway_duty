import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from tkinterdnd2 import DND_FILES, DND_ALL, TkinterDnD
import time
import re
from ttkbootstrap import Style


class RailwayTrackManager:
    def __init__(self, master):
        self.master = master
        self.master.title("Управление железнодорожными путями")
        self.master.geometry("800x700")  # Задаем размер окна

        # Устанавливаем окно поверх всех других окон
        self.is_topmost = True
        self.master.attributes("-topmost", self.is_topmost)

        # Создаем стиль
        self.style = Style(theme='darkly')  # Устанавливаем начальную тему
        self.current_theme = 'darkly'  # Текущая тема

        # Создаем пользовательский заголовок
        self.title_frame = ttk.Frame(master, padding=(10, 5))
        self.title_frame.pack(fill=tk.X)

        self.title_label = ttk.Label(self.title_frame, text="Управление железнодорожными путями", font=("Arial", 16))
        self.title_label.pack(side=tk.LEFT, padx=5)

        self.toggle_topmost_button = ttk.Button(self.title_frame, text="Открепить", command=self.toggle_topmost)
        self.toggle_topmost_button.pack(side=tk.RIGHT, padx=5)

        self.toggle_theme_button = ttk.Button(self.title_frame, text="Светлая тема", command=self.toggle_theme)
        self.toggle_theme_button.pack(side=tk.RIGHT, padx=5)

        # Добавляем метку для отображения времени с увеличенным шрифтом
        self.time_label = ttk.Label(self.title_frame, font=("Arial", 18, "bold"))  # Увеличенный шрифт
        self.time_label.pack(side=tk.RIGHT, padx=5)

        self.update_time()  # Обновляем время при инициализации

        self.tracks = ["Путь {}".format(i + 1) for i in range(13)]
        self.trains = [None] * 13  # Список для хранения поездов на путях

        self.track_buttons = []
        self.create_track_buttons()

        # Кнопки управления
        button_frame = ttk.Frame(master, padding=(10, 5))
        button_frame.pack(pady=10)

        self.add_train_button = self.create_gradient_button(button_frame, "Добавить поезд", self.open_add_train_dialog)
        self.add_train_button.pack(side=tk.LEFT, padx=5)

        self.remove_train_button = self.create_gradient_button(button_frame, "Удалить поезд", self.remove_train)
        self.remove_train_button.pack(side=tk.LEFT, padx=5)

        self.dialog = None  # Ссылка на диалоговое окно

    def create_gradient_button(self, parent, text, command):
        button = ttk.Button(parent, text=text, command=command, style="Gradient.TButton")
        button.pack_propagate(False)  # Не изменять размер кнопки
        button.place(width=150, height=40)  # Задаем размер кнопки
        return button

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")  # Получаем текущее время
        self.time_label.config(text=current_time)  # Обновляем текст метки
        self.master.after(1000, self.update_time)  # Обновляем время каждую секунду

    def create_track_buttons(self):
        track_frame = ttk.Frame(self.master, padding=(10, 5))
        track_frame.pack(pady=10)

        for i, track in enumerate(self.tracks):
            button = self.create_gradient_button(track_frame, track, lambda index=i: self.show_train_info(index))
            button.pack(pady=5, fill=tk.X)  # Заполнение по горизонтали
            self.track_buttons.append(button)

    def show_train_info(self, track_index):
        train_info = self.trains[track_index]
        if train_info:
            messagebox.showinfo("Информация о поезде", f"На {self.tracks[track_index]}:\n{train_info}")
        else:
            messagebox.showinfo("Информация о поезде", f"{self.tracks[track_index]} свободен.")

    def open_add_train_dialog(self):
        # Проверяем, открыт ли диалог уже
        if self.dialog is not None and self.dialog.winfo_exists():
            messagebox.showwarning("Ошибка", "Диалоговое окно уже открыто.")
            return

        # Создаем новое окно для ввода данных о поезде
        self.dialog = tk.Toplevel(self.master)
        self.dialog.title("Добавить поезд")
        self.dialog.geometry("400x500")  # Задаем размер окна

        ttk.Label(self.dialog, text="Введите номер поезда:", font=("Arial", 14)).pack(pady=5)
        train_number_entry = ttk.Entry(self.dialog, font=("Arial", 14), width=30)  # Увеличенный шрифт и ширина
        train_number_entry.pack(pady=5)

        ttk.Label(self.dialog, text="Введите название груза (только на русском):", font=("Arial", 14)).pack(pady=5)
        cargo_name_entry = ttk.Entry(self.dialog, font=("Arial", 14), width=30)  # Увеличенный шрифт и ширина
        cargo_name_entry.pack(pady=5)

        ttk.Label(self.dialog, text="Введите время прибытия (чч:мм):", font=("Arial", 14)).pack(pady=5)
        arrival_time_entry = ttk.Entry(self.dialog, font=("Arial", 14), width=30)  # Увеличенный шрифт и ширина
        arrival_time_entry.pack(pady=5)

        ttk.Label(self.dialog, text="Введите время убытия (чч:мм):", font=("Arial", 14)).pack(pady=5)
        departure_time_entry = ttk.Entry(self.dialog, font=("Arial", 14), width=30)  # Увеличенный шрифт и ширина
        departure_time_entry.pack(pady=5)

        # Добавляем выпадающий список для выбора пути
        ttk.Label(self.dialog, text="Выберите путь:", font=("Arial", 14)).pack(pady=5)
        self.track_combobox = ttk.Combobox(self.dialog, values=self.get_available_tracks(), font=("Arial", 14), state="readonly")
        self.track_combobox.pack(pady=5)

        # Определяем функцию add_train
        def add_train():
            train_number = train_number_entry.get()
            cargo_name = cargo_name_entry.get()
            arrival_time = arrival_time_entry.get()
            departure_time = departure_time_entry.get()
            selected_track = self.track_combobox.get()

            # Валидация
            if not self.validate_cargo_name(cargo_name):
                messagebox.showwarning("Ошибка", "Название груза должно содержать только русские буквы.")
                return

            if not self.validate_time_format(arrival_time) or not self.validate_time_format(departure_time):
                messagebox.showwarning("Ошибка", "Время должно быть в формате чч:мм.")
                return

            # Находим индекс выбранного пути
            track_index = self.tracks.index(selected_track)

            if self.trains[track_index] is None:
                self.trains[track_index] = f"Номер: {train_number}, Груз: {cargo_name}, Прибытие: {arrival_time}, Убытие: {departure_time}"
                messagebox.showinfo("Успех", f"Поезд '{train_number}' добавлен на {selected_track}.")

                # Изменяем цвет кнопки пути на занятый
                self.track_buttons[track_index].config(style="danger.TButton")  # Пример стиля для занятых путей

                # Обновляем выпадающий список
                self.update_track_combobox()

                self.dialog.destroy()  # Закрываем диалог после успешного добавления
            else:
                messagebox.showwarning("Ошибка", f"{selected_track} уже занят.")

        # Теперь создаем кнопку, передавая ссылку на add_train
        add_button = ttk.Button(self.dialog, text="Добавить поезд", command=add_train)
        add_button.pack(pady=10)

    def validate_cargo_name(self, cargo_name):
        # Проверяем, что название груза состоит только из русских букв
        return bool(re.match(r'^[А-Яа-яЁё\s]+$', cargo_name))

    def validate_time_format(self, time_str):
        # Проверяем, что время соответствует формату чч:мм
        return bool(re.match(r'^\d{2}:\d{2}$', time_str))

    def remove_train(self):
        track_index = self.select_track()
        if track_index is not None:
            if self.trains[track_index] is not None:
                train_info = self.trains[track_index]
                self.trains[track_index] = None
                messagebox.showinfo("Успех", f"Поезд '{train_info}' удален с {self.tracks[track_index]}.")

                # Изменяем цвет кнопки пути на свободный
                self.track_buttons[track_index].config(style="Gradient.TButton")  # Возвращаем стиль кнопки

                # Обновляем выпадающий список
                self.update_track_combobox()

            else:
                messagebox.showwarning("Ошибка", f"{self.tracks[track_index]} свободен.")

    def update_track_combobox(self):
        # Обновляем значения в выпадающем списке
        if self.track_combobox and self.track_combobox.winfo_exists():  # Проверяем, существует ли combobox
            available_tracks = self.get_available_tracks()
            self.track_combobox['values'] = available_tracks
            if available_tracks:
                self.track_combobox.current(0)  # Устанавливаем первый элемент как выбранный

    def get_available_tracks(self):
        # Возвращаем список доступных путей (свободных)
        return [track for i, track in enumerate(self.tracks) if self.trains[i] is None]

    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        self.master.attributes("-topmost", self.is_topmost)
        # Изменяем текст кнопки в зависимости от состояния
        if self.is_topmost:
            self.toggle_topmost_button.config(text="Открепить")
        else:
            self.toggle_topmost_button.config(text="Закрепить")

    def toggle_theme(self):
        if self.current_theme == 'darkly':
            self.current_theme = 'flatly'
            self.style.theme_use('flatly')
            self.master.configure(bg="#ffffff")  # Устанавливаем светлый фон
            for i, button in enumerate(self.track_buttons):
                if button.winfo_exists():  # Проверяем, существует ли кнопка
                    if self.trains[i] is not None:  # Если путь занят
                        button.config(style="danger.TButton")  # Сохраняем красный цвет для занятых путей
                    else:
                        button.config(style="primary.TButton")  # Стандартный стиль для свободных путей
            if self.toggle_theme_button.winfo_exists():  # Проверяем, существует ли кнопка
                self.toggle_theme_button.config(text="Темная тема")
        else:
            self.current_theme = 'darkly'
            self.style.theme_use('darkly')
            self.master.configure(bg="#1c1c1c")  # Устанавливаем темный фон
            for i, button in enumerate(self.track_buttons):
                if button.winfo_exists():  # Проверяем, существует ли кнопка
                    if self.trains[i] is not None:  # Если путь занят
                        button.config(style="danger.TButton")  # Сохраняем красный цвет для занятых путей
                    else:
                        button.config(style="primary.TButton")  # Стандартный стиль для свободных путей
            if self.toggle_theme_button.winfo_exists():  # Проверяем, существует ли кнопка
                self.toggle_theme_button.config(text="Светлая тема")

    def select_track(self):
        track_names = [f"{track} (введите {i + 1})" for i, track in enumerate(self.tracks)]
        track_name = simpledialog.askstring("Выбор пути", "Введите номер пути (1-13):\n" + "\n".join(track_names))
        if track_name is not None and track_name.isdigit():
            track_index = int(track_name) - 1  # Преобразуем номер пути в индекс
            if 0 <= track_index < len(self.tracks):
                return track_index
            else:
                messagebox.showwarning("Ошибка", "Некорректный номер пути.")
        return None


if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Используем TkinterDnD вместо tk.Tk
    app = RailwayTrackManager(root)
    root.mainloop()
