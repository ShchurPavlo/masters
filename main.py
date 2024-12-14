import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

import engine
import validate


class BackupCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Calculator")

        # Дані для серверів, сховищ та планів
        self.servers_data = []
        self.storages_data = []
        self.plans_data = []

        self.init_common_widgets()

        # Створення вкладок
        self.tab_control = ttk.Notebook(self.root)

        # Вкладка 1: Налаштування серверів
        self.server_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.server_tab, text="Server Settings")

        # Вкладка 2: Налаштування сховища
        self.storage_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.storage_tab, text="Storage Settings")

        # Вкладка 3: Налаштування плану
        self.plan_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.plan_tab, text="Backup settings")

        # Запуск вкладок
        self.tab_control.pack(expand=1, fill="both")

        # Створення серверної форми
        self.init_server_tab()

        # Створення форми сховища
        self.init_storage_tab()

        # Створення форми плану
        self.init_plan_tab()

    def init_tabs(self):
        self.tab_control = ttk.Notebook(self.root)

        # Вкладка серверів
        self.server_tab = ttk.Frame(self.tab_control)
        self.init_server_tab()
        self.tab_control.add(self.server_tab, text="Server Settings")

        # Вкладка сховищ
        self.storage_tab = ttk.Frame(self.tab_control)
        self.init_storage_tab()
        self.tab_control.add(self.storage_tab, text="Storage Settings")

        # Вкладка планів
        self.plan_tab = ttk.Frame(self.tab_control)
        self.init_plan_tab()
        self.tab_control.add(self.plan_tab, text="Backup Settings")

    def init_server_tab(self):
        self.servers_frame = tk.Frame(self.server_tab)
        self.servers_frame.pack(fill='both', expand=True, pady=10)

        # Підписи
        labels_frame = tk.Frame(self.servers_frame)
        labels_frame.pack(fill='x', pady=5)

        tk.Label(labels_frame, text="Server Name:").grid(row=0, column=0, padx=30, pady=5, sticky="w")
        tk.Label(labels_frame, text="Server Size (GB):").grid(row=0, column=1, padx=30, pady=5, sticky="w")
        tk.Label(labels_frame, text="Growth Rate:").grid(row=0, column=2, padx=30, pady=5, sticky="w")
        tk.Label(labels_frame, text="Daily Increase (%):").grid(row=0, column=3, padx=10, pady=5, sticky="w")

        tk.Button(self.server_tab, text="+ Add Server", command=self.add_server).pack(pady=10)

    def init_storage_tab(self):
        self.storages_frame = tk.Frame(self.storage_tab)
        self.storages_frame.pack(fill='both', expand=True, pady=10)

        # Підписи
        labels_frame = tk.Frame(self.storages_frame)
        labels_frame.pack(fill='x', pady=5)

        tk.Label(labels_frame, text="Name:").grid(row=0, column=0, padx=30, pady=5, sticky="w")
        tk.Label(labels_frame, text="Cost per GB($):").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        tk.Label(labels_frame, text="Size (GB):").grid(row=0, column=2, padx=8, pady=5, sticky="w")
        tk.Label(labels_frame, text="Save Speed(GB/s):").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        tk.Label(labels_frame, text="Restore Speed(GB/s):").grid(row=0, column=4, padx=10, pady=5, sticky="w")

        tk.Button(self.storage_tab, text="+ Add Storage", command=self.add_storage).pack(pady=10)

    def init_plan_tab(self):
        self.plans_frame = tk.Frame(self.plan_tab)
        self.plans_frame.pack(fill='both', expand=True, pady=10)

        # Підписи
        labels_frame = tk.Frame(self.plans_frame)
        labels_frame.pack(fill='x', pady=5)

        tk.Label(labels_frame, text="Name:").grid(row=0, column=0, padx=50, pady=5, sticky="w")
        tk.Label(labels_frame, text="Server:").grid(row=0, column=1, padx=30, pady=5, sticky="w")
        tk.Label(labels_frame, text="Storage:").grid(row=0, column=2, padx=30, pady=5, sticky="w")
        tk.Label(labels_frame, text="Tool:").grid(row=0, column=3, padx=30, pady=5, sticky="w")
        tk.Label(labels_frame, text="Type:").grid(row=0, column=4, padx=50, pady=5, sticky="w")
        tk.Label(labels_frame, text="Schedule:").grid(row=0, column=5, padx=20, pady=5, sticky="w")
        tk.Label(labels_frame, text="Retention:").grid(row=0, column=6, padx=2, pady=5, sticky="ew")

        tk.Button(self.plan_tab, text="+ Add Plan", command=self.add_plan).pack(pady=10)

    def init_common_widgets(self):
        tk.Label(self.root, text="Period (days):").pack(padx=5)
        self.period_entry = tk.Entry(self.root, width=10)
        self.period_entry.pack(padx=5)
        tk.Button(self.root, text="Calculate", command=self.calculate).pack(pady=20)

    def create_label(self, parent, text, row, column):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=column, padx=10, pady=5, sticky="w")

    def add_storage(self):
        # Створюємо нові віджети для нового сховища
        storage_frame = tk.Frame(self.storages_frame)
        storage_frame.pack(fill='x', pady=5)

        # Поля для налаштувань сховища
        storage_name_entry = tk.Entry(storage_frame, width=15)
        storage_name_entry.insert(0, "NAS")  # Стандартне значення
        storage_name_entry.grid(row=1, column=0, padx=10, pady=5)

        storage_cost_entry = tk.Entry(storage_frame, width=10)
        storage_cost_entry.insert(0, "2")  # Стандартне значення
        storage_cost_entry.grid(row=1, column=1, padx=10, pady=5)

        storage_size_entry = tk.Entry(storage_frame, width=10)
        storage_size_entry.insert(0, "2")  # Стандартне значення
        storage_size_entry.grid(row=1, column=2, padx=10, pady=5)

        save_speed_entry = tk.Entry(storage_frame, width=10)
        save_speed_entry.insert(0, "1")  # Стандартне значення
        save_speed_entry.grid(row=1, column=3, padx=20, pady=5)

        restore_speed_entry = tk.Entry(storage_frame, width=10)
        restore_speed_entry.insert(0, "2")  # Стандартне значення
        restore_speed_entry.grid(row=1, column=4, padx=25, pady=5)

        # Кнопка для видалення сховища
        delete_button = tk.Button(storage_frame, text="X", command=lambda: self.delete_frame(self.storages_data, storage_frame),
                                  fg="red", font=("Arial", 12, "bold"))
        delete_button.grid(row=1, column=5, padx=15, pady=5, sticky="w")

        # Додавання даних сховища в список
        storage_data = {
            'frame': storage_frame,
            'name': storage_name_entry.get(),
            'cost': storage_cost_entry.get(),
            'size': storage_size_entry.get(),
            'save_speed': save_speed_entry.get(),
            'restore_speed': restore_speed_entry.get(),
        }

        self.storages_data.append(storage_data)

        def update_storage_data(event):
            # Оновлюємо значення в масиві 'storage_data' для конкретного сервера
            for storage_data in self.storages_data:
                if storage_data['frame'] == storage_frame:  # Знаходимо поточний сервер
                    storage_data['name'] = storage_name_entry.get()
                    storage_data['cost'] = storage_cost_entry.get()
                    storage_data['size'] = storage_size_entry.get()
                    storage_data['save_speed'] = save_speed_entry.get()
                    storage_data['restore_speed'] = restore_speed_entry.get()
                    break  # Виходимо після того, як оновили потрібні дані

        # Прив'язуємо події для кожного поля вводу
        storage_name_entry.bind("<KeyRelease>", update_storage_data)
        storage_cost_entry.bind("<KeyRelease>", update_storage_data)
        save_speed_entry.bind("<KeyRelease>", update_storage_data)
        restore_speed_entry.bind("<KeyRelease>", update_storage_data)
        storage_size_entry.bind("<KeyRelease>", update_storage_data)

    def add_plan(self):
        #global id  # Використовуємо глобальну змінну id для унікальності кожного плану
        # Створюємо нові віджети для нового плану
        plan_frame = tk.Frame(self.plans_frame)
        plan_frame.pack(fill='x', pady=5)

        # Поля для налаштувань плану
        name_entry = tk.Entry(plan_frame, width=20)
        name_entry.insert(0, f"Name")  # Стандартне значення
        name_entry.grid(row=0, column=0, padx=10, pady=5)

        # Випадаючий список для вибору сервера
        server_combobox = ttk.Combobox(plan_frame, values=[server['name'] for server in self.servers_data],
                                       state="readonly", width=10)
        server_combobox.grid(row=0, column=1, padx=10, pady=5)
        server_combobox.plan_id = id
        #id = id + 1

        # Випадаючий список для вибору сховища
        storage_combobox = ttk.Combobox(plan_frame, values=[storage['name'] for storage in self.storages_data],
                                        state="readonly", width=10)
        storage_combobox.grid(row=0, column=2, padx=10, pady=5)
        storage_combobox.plan_id = id
        #id = id + 1

        # Випадаючий список для вибору інструменту резервного копіювання
        backup_tool_combobox = ttk.Combobox(plan_frame, values=["VZDump", "Acronis", "Veeam"], state="readonly",
                                            width=10)
        backup_tool_combobox.grid(row=0, column=3, padx=10, pady=5)

        # Випадаючий список для вибору типу резервної копії
        type_combobox = ttk.Combobox(plan_frame, values=["Full", "Incremental", "Differential"], state="readonly",
                                     width=13)
        type_combobox.grid(row=0, column=4, padx=10, pady=5)

        # Введення розкладу в форматі CRON
        schedule_entry = tk.Entry(plan_frame, width=13)
        schedule_entry.insert(0, f"30 11 * * 1,3,4")  # Стандартне значення
        schedule_entry.grid(row=0, column=5, padx=10, pady=5)

        # Введення кількості збережених копій
        retention_entry = tk.Entry(plan_frame, width=3)
        retention_entry.insert(0, f"3")  # Стандартне значення
        retention_entry.grid(row=0, column=6, padx=10, pady=5)

        # Кнопка для видалення плану
        delete_button = tk.Button(plan_frame, text="X",
                                  command=lambda: self.delete_frame(self.plans_data, plan_frame), fg="red",
                                  font=("Arial", 12, "bold"))
        delete_button.grid(row=0, column=7, padx=10, pady=5, sticky="w")

        # Збереження даних плану
        plan_data = {
            'frame': plan_frame,
            'name': name_entry.get(),
            'server': server_combobox.get(),
            'storage': storage_combobox.get(),
            'tool': backup_tool_combobox.get(),
            'type': type_combobox.get(),
            'schedule': schedule_entry.get(),
            'retention': retention_entry.get(),
        }

        # Додавання даних плану до списку планів
        self.plans_data.append(plan_data)

        def update_plan_data(event):
            # Оновлюємо значення в масиві 'servers_data' для конкретного сервера
            for plan_data in self.plans_data:
                if plan_data['frame'] == plan_frame:  # Знаходимо поточний сервер
                    plan_data['name'] = name_entry.get()
                    plan_data['server'] = server_combobox.get()
                    plan_data['storage'] = storage_combobox.get()
                    plan_data['type'] = type_combobox.get()
                    plan_data['tool'] = backup_tool_combobox.get()
                    plan_data['retention'] = retention_entry.get()
                    plan_data['schedule'] = schedule_entry.get()
                    break  # Виходимо після того, як оновили потрібні дані


        # Прив'язуємо події для кожного поля вводу
        name_entry.bind("<KeyRelease>", update_plan_data)
        server_combobox.bind("<<ComboboxSelected>>", update_plan_data)
        storage_combobox.bind("<<ComboboxSelected>>", update_plan_data)
        type_combobox.bind("<<ComboboxSelected>>", update_plan_data)
        backup_tool_combobox.bind("<<ComboboxSelected>>", update_plan_data)
        schedule_entry.bind("<KeyRelease>", update_plan_data)
        retention_entry.bind("<KeyRelease>", update_plan_data)

        # Після додавання, оновлюємо список вибору для сервера і сховища
        server_combobox.set('')
        storage_combobox.set('')
        backup_tool_combobox.set('')
        type_combobox.set('')

    def add_server(self):
        # Створюємо нові віджети для нового сховища
        server_frame = tk.Frame(self.servers_frame)
        server_frame.pack(fill='x', pady=5)

        # Поля вводу для нового сервера
        server_name_entry = tk.Entry(server_frame)
        server_name_entry.insert(0, f"1C")  # Стандартне значення
        server_name_entry.grid(row=1, column=0, padx=10, pady=3)

        server_size_entry = tk.Entry(server_frame)
        server_size_entry.insert(0, "100")  # Стандартне значення
        server_size_entry.grid(row=1, column=1, padx=10, pady=3)

        growth_rate_entry = tk.Entry(server_frame)
        growth_rate_entry.insert(0, "5")  # Стандартне значення
        growth_rate_entry.grid(row=1, column=2, padx=10, pady=3)

        daily_increase_entry = tk.Entry(server_frame)
        daily_increase_entry.insert(0, "10")  # Стандартне значення
        daily_increase_entry.grid(row=1, column=3, padx=10, pady=3)

        # Кнопка для видалення сховища
        delete_button = tk.Button(server_frame, text="X",
                                  command=lambda: self.delete_frame(self.servers_data, server_frame),
                                  fg="red", font=("Arial", 12, "bold"))
        delete_button.grid(row=1, column=4, padx=10, pady=5, sticky="w")

        # Додавання даних сховища в список
        server_data = {
            'frame': server_frame,
            'name': server_name_entry.get(),
            'size': server_size_entry.get(),
            'growth': growth_rate_entry.get(),
            'daily_increase': daily_increase_entry.get(),
        }
        self.servers_data.append(server_data)

        def update_server_data(event):
            # Оновлюємо значення в масиві 'servers_data' для конкретного сервера
            for server_data in self.servers_data:
                if server_data['frame'] == server_frame:  # Знаходимо поточний сервер
                    server_data['name'] = server_name_entry.get()  # Оновлюємо ім'я
                    server_data['size'] = server_size_entry.get()  # Оновлюємо розмір
                    server_data['growth'] = growth_rate_entry.get()  # Оновлюємо коефіцієнт росту
                    server_data['daily_increase'] = daily_increase_entry.get()  # Оновлюємо добовий приріст
                    break  # Виходимо після того, як оновили потрібні дані

        # Прив'язуємо події для кожного поля вводу
        server_name_entry.bind("<KeyRelease>", update_server_data)
        server_size_entry.bind("<KeyRelease>", update_server_data)
        growth_rate_entry.bind("<KeyRelease>", update_server_data)
        daily_increase_entry.bind("<KeyRelease>", update_server_data)

    def calculate(self):
        checks = [
            ("servers", validate.check_servers_data, self.servers_data),
            ("storages", validate.check_storages_data, self.storages_data),
            ("plans", validate.check_plans_data, self.plans_data)
        ]

        for check_name, check_func, data in checks:
            result = check_func(data)
            if result != True:
                messagebox.showerror("Error", result)  # Виводимо вікно помилки
                return  # Завершуємо метод, якщо є помилка
        period = int(self.period_entry.get())
        messagebox.showinfo("Success", "All is ok")  # Якщо всі перевірки пройдені
        print(self.servers_data)
        print(self.storages_data)
        print(self.plans_data)
        self.servers_data = validate.convert_to_float(self.servers_data)
        self.storages_data = validate.convert_to_float(self.storages_data)
        self.plans_data = validate.convert_to_float(self.plans_data)
        engine.show_storage_usage_plots(self.servers_data,self.storages_data,self.plans_data,engine.calculate_storage_usage(period,self.servers_data,self.plans_data))
        engine.show_storage_costs_plot(self.servers_data,self.storages_data,self.plans_data,engine.calculate_storage_usage(period,self.servers_data,self.plans_data))
        engine.show_RPO_plots(self.servers_data, self.storages_data, self.plans_data,engine.calculate_RPO(self.servers_data, self.storages_data, self.plans_data, period))
        engine.show_RTO_plots(self.servers_data, self.storages_data, self.plans_data, engine.calculate_RTO(self.servers_data, self.storages_data, self.plans_data, period))
    def show_graph(self):
        checks = [
            ("servers", validate.check_servers_data, self.servers_data),
            ("storages", validate.check_storages_data, self.storages_data),
            ("plans", validate.check_plans_data, self.plans_data)
        ]

        for check_name, check_func, data in checks:
            result = check_func(data)
            if result != True:
                messagebox.showerror("Error", result)  # Виводимо вікно помилки
                return  # Завершуємо метод, якщо є помилка


        engine.plot_backup_policy_graph(self.servers_data,self.storages_data,self.plans_data)  # Якщо всі перевірки пройдені

    def init_common_widgets(self):
        tk.Label(self.root, text="Period (days):").grid(row=0, column=0, padx=5, pady=5)
        self.period_entry = tk.Entry(self.root, width=10)
        self.period_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Calculate", command=self.calculate).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(self.root, text="Graph", command=self.calculate).grid(row=0, column=3, padx=5, pady=5)

    def init_common_widgets(self):
        # Створюємо контейнер для елементів
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=5)  # Розташовуємо контейнер у головному вікні

        # Додаємо елементи в контейнер
        tk.Label(frame, text="Period (days):").pack(side="left", padx=5)
        self.period_entry = tk.Entry(frame, width=10)
        self.period_entry.pack(side="left", padx=5)
        tk.Button(frame, text="Calculate", command=self.calculate).pack(side="left", padx=5)
        tk.Button(frame, text="Graph", command=self.show_graph).pack(side="left", padx=5)

    def delete_frame(self, data_list, frame):
        # Знаходимо словник, який відповідає цьому frame у списку даних
        for data in data_list:
            if data['frame'] == frame:
                data_list.remove(data)  # Видаляємо словник зі списку
                break
        frame.destroy()  # Знищуємо сам frame після його видалення зі списку

# Створення основного вікна
root = tk.Tk()
root.iconbitmap("icon.ico")
app = BackupCalculatorApp(root)

# Запуск основного циклу Tkinter
root.mainloop()
