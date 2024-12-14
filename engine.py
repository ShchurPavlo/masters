import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import re
import numpy as np
import networkx as nx
from datetime import datetime, timedelta
from croniter import croniter
from sympy import symbols, sympify

import validate

def get_cron_dates(cron_schedule, year_days):
    # Ініціалізуємо CRON-розклад і початкову точку відліку
    cron = croniter(cron_schedule, datetime(datetime.now().year, 1, 1))  # Починаємо з 1 січня
    backup_days = []  # Список для порядкових номерів днів року

    while True:
        next_date = cron.get_next(datetime)  # Отримуємо наступну дату з CRON
        day_of_year = (next_date - datetime(datetime.now().year, 1, 1)).days + 1  # Обчислюємо порядковий номер дня
        if day_of_year > year_days:  # Якщо дата виходить за межі року, зупиняємо
            break
        backup_days.append(day_of_year)  # Додаємо номер дня до списку

    return backup_days
def plot_backup_policy_graph(servers_data, storages_data, plans_data):
    # Створення графа
    graph = nx.DiGraph()  # Орієнтований граф, оскільки резервні копії йдуть у певному напрямку

    # Додаємо вузли для серверів і сховищ
    for server in servers_data:
        graph.add_node(server['name'], type='server', size=int(server['size']))
    for storage in storages_data:
        graph.add_node(storage['name'], type='storage', size=(int(storage['size']) * 0.5))  # Масштабування для сховищ

    # Додаємо ребра на основі планів резервного копіювання
    for plan in plans_data:
        graph.add_edge(plan['server'], plan['storage'], type=plan['type'], retention=plan['retention'])

    # Візуалізація
    pos = {}

    # Розташування серверів вгорі, сховищ внизу
    y_offset = 2  # Відстань між рівнями (сервери та сховища)

    # Визначаємо позиції для серверів
    for i, server in enumerate(servers_data):
        pos[server['name']] = (i, y_offset)  # Позиція серверів вгорі

    # Визначаємо позиції для сховищ
    for i, storage in enumerate(storages_data):
        pos[storage['name']] = (i, -y_offset)  # Позиція сховищ внизу

    # Налаштування кольорів вузлів
    node_colors = [
        '#1f77b4' if graph.nodes[node]['type'] == 'server' else '#2ca02c'
        for node in graph.nodes
    ]

    # Розрахунок розміру вузлів
    node_sizes = [
        graph.nodes[node]['size'] * 20  # Масштабування розміру для графічного відображення
        for node in graph.nodes
    ]

    # Малюємо граф без ребер
    plt.figure(figsize=(8, 6))
    nx.draw(
        graph, pos, with_labels=True, node_color=node_colors, edge_color='gray',
        node_size=node_sizes, font_size=10
    )

    # Розділяємо ребра за типом резервної копії
    edge_labels = {}  # Список для міток на ребрах

    full_edges = []
    incremental_edges = []

    for u, v, data in graph.edges(data=True):
        tool = data['type']
        if tool == 'Full':
            full_edges.append((u, v))  # Додаємо ребра для повної резервної копії
            edge_labels[(u, v)] = 'Full'
        elif tool == 'Incremental':
            incremental_edges.append((u, v))  # Додаємо ребра для інкрементної резервної копії
            edge_labels[(u, v)] = 'Incremental'

    # Малюємо ребра з різними типами стрілок
    nx.draw_networkx_edges(graph, pos, edgelist=full_edges, edge_color='blue', arrows=True, arrowsize=20, style='solid')
    nx.draw_networkx_edges(graph, pos, edgelist=incremental_edges, edge_color='green', arrows=True, arrowsize=20, style='dashed')

    # Додаємо мітки для ребер
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Backup Policy Graph")
    plt.show()

def get_most_frequent_full_plan(full_plans, year_days):
    #Знаходить план резервного копіювання з найбільшою частотою (найбільша кількість дат).

    if not full_plans:
        return None  # Якщо список порожній, повертаємо None

    # Рахуємо кількість дат резервного копіювання для кожного плану
    plan_dates_count = {
        plan['name']: len(get_cron_dates(plan['schedule'], year_days))
        for plan in full_plans
    }

    # Знаходимо план з найбільшою кількістю дат
    most_frequent_plan_name = max(plan_dates_count, key=plan_dates_count.get)

    # Повертаємо план з найбільшою частотою
    return next(plan for plan in full_plans if plan['name'] == most_frequent_plan_name)
def calculate_storage_usage(time, servers_data, plans_data):
    all_plans = []
    for plan in plans_data:
        plan_name, plan_type, server_name, storage_name, retention, cron_schedule = plan['name'], plan['type'], plan['server'], plan['storage'], int(plan['retention']), plan['schedule']
        server = next(s for s in servers_data if s['name'] == server_name)
        if plan_type == "Incremental":
            # Шукаємо повні плани для цього сервера і цього сховища
            full_plans = [p for p in plans_data if p['type'] == "Full" and p['server'] == server_name and p['storage'] == storage_name]

            if not full_plans:
                messagebox.showinfo("No full backups for objets:",server_name)
                continue  # Пропустити обробку цього інкрементного плану якщо для нього нема інкрементних значень

            for full_plan in full_plans:
                full_plan_days = get_cron_dates(full_plan['schedule'], time)
                print("Full:", full_plan_days)
                incremental_plan_days = get_cron_dates(cron_schedule, time)
                print("Incremental:", incremental_plan_days)

                incremental_backups_number = get_incremental_count(time, full_plan_days, incremental_plan_days)
                full_backup_sizes = get_full_storage(time, server, full_plan)

                all_plans.append(get_incremental_storage(time, server, plan, full_backup_sizes, incremental_backups_number))

        else:
            all_plans.append(get_full_storage(time, server, plan))

    return all_plans

def calculate_backup_size(size,type):
    return size * 0.3

def calculate_new_size(formula, current_size):

    # Задаємо змінні
    k = symbols('k')  # Поточний розмір сервера
    n = symbols('n')  # Новий розмір сервера

    # Перетворюємо рядок у математичний вираз
    expression = sympify(formula)

    # Замінюємо k на поточний розмір
    new_size = expression.subs(k, current_size)

    # Повертаємо значення n
    return float(new_size)

def get_full_storage(time,server, plan):
    plan_name, type,tool, server_name, storage_name, retention, cron_schedule = plan['name'], plan['type'],plan['tool'], plan['server'], plan['storage'], int(plan['retention']), plan['schedule']
    growth,size = server['growth'],server['size']

    storage_day_info = np.zeros((time, 2), dtype=object)
    for i in range(time):
        storage_day_info[i, 0] = []  # Ініціалізація списку для розмірів копій
        storage_day_info[i, 1] = 0  # Ініціалізація суми

    cron_dates = get_cron_dates(cron_schedule,time)  # Отримуємо дати резервного копіювання

    #print('Full:', cron_dates)

    current_backups = []  # Поточний список копій для сервера


    for day in range(1, time + 1):
        size=calculate_new_size(growth,size)
        if day in cron_dates:  # Додаємо копію, якщо день входить у розклад
            backup_size = calculate_backup_size(int(size),tool)
            current_backups.append(backup_size)  # Видаляємо старі копії, якщо їх більше, ніж retention
            if len(current_backups) > retention:
                current_backups.pop(0)  # Оновлюємо масив для цього дня

        storage_day_info[day - 1, 0] = current_backups.copy()  # Копії для дня
        storage_day_info[day - 1, 1] = round(sum(current_backups))  # Сумарний розмір

    # Створюємо масив із назвою сховища та списком сум за рік для поточного плану
    return [
        plan_name,  # Назва плану
        type,  # Назва плану
        storage_name,  # Сховище
        server_name,  # Назва об'єкта (сервер)
        [storage_day_info[i, 1] for i in range(time)],  # Суми по дням
        [storage_day_info[i, 0] for i in range(time)]  # Розмір останнього
    ]

def сalculate_storage(time, servers_data, plans_data):
    all_plans=[]
    for plan in plans_data:
        plan_name,type, server_name, storage_name, retention, cron_schedule = plan['name'],plan['type'], plan['server'], plan['storage'], int(plan['retention']), plan['schedule']
        server = next(s for s in servers_data if s['name'] == server_name)
        if type == "Incremental":
            # Шукаємо повні плани для цього сервера і цього сховища
            full_plans = [p for p in plans_data if p['type'] == "Full" and p['server'] == server_name and p['storage'] == storage_name]
            most_frequent_plan=get_most_frequent_full_plan(full_plans,time)
            if not full_plans:
                print(f"Немає повного плану для сервера {server_name} на сховищі {storage_name}.")
                continue  # Пропустити обробку цього інкрементного плану
            else:
                full_plan_days=get_cron_dates(most_frequent_plan['schedule'],time)
                print("Full:",full_plan_days)
                incremental_plan_days=get_cron_dates(cron_schedule,time)
                print("Incremental:", incremental_plan_days)
                incremental_backups_number=get_incremental_count(time,full_plan_days,incremental_plan_days)
                full_backup_sizes=get_full_storage(time, server, full_plan)
                all_plans.append(get_incremental_storage(time,server, plan,full_backup_sizes,incremental_backups_number))
        else:
            all_plans.append(get_full_storage(time,server,plan))
    return all_plans

def show_storage_usage_plots(servers_data, storages_data, plans_data, all_plans):
    #Відображає графіки використання сховищ для кожного типу сховища.
    # Групуємо плани за сховищами
    storage_groups = {}
    for plan in all_plans:
        storage_name = plan[2]
        storage_groups.setdefault(storage_name, []).append(plan)

    # Побудова графіків для кожного сховища
    for storage_name, plans in storage_groups.items():
        # Отримуємо дані про сховище
        storage = next((s for s in storages_data if s['name'] == storage_name), None)
        if not storage:
            print(f"Warning: Storage {storage_name} not found in storages_data.")
            continue

        total_size = storage['size']

        # Розрахунок сумарного використання для всіх днів
        max_days = max(len(plan[4]) for plan in plans if plan[4])
        total_usage_per_day = [0] * max_days
        for plan in plans:
            for day, usage in enumerate(plan[4]):
                total_usage_per_day[day] += usage

        # Створення графіка
        plt.figure()
        plt.axhline(y=total_size, color='red', linestyle='-', linewidth=2, label="Storage Capacity")  # Лінія максимальної вмістимості

        # Побудова графіків для кожного плану
        for plan in plans:
            if not plan[4]:  # Пропускаємо плани без даних
                continue
            plan_name = plan[0]
            days = list(range(1, len(plan[4]) + 1))  # Список днів
            linestyle = '--' if plan[1] == "Incremental" else '-'  # Тип лінії залежно від типу плану
            plt.plot(days, plan[4], label=f"{plan_name} ({plan[3]})", linestyle=linestyle, marker='o')

        # Додаємо сумарне використання
        plt.plot( list(range(1, max_days + 1)),  total_usage_per_day,  label="Total Usage",  color='black',  linestyle='-', linewidth=3 )

        # Налаштування графіка
        plt.title(f"Storage Usage for {storage_name}")
        plt.xlabel("Days")
        plt.ylabel("Storage Size (GB)")
        plt.legend()
        plt.grid(True)
        plt.show()

def calculate_backup_size(size,type):
    return size/ 1.7

def show_storage_costs_plot(servers_data, storages_data, plans_data, all_plans):

    #Відображає графік витрат на сховище для кожного типу сховища.
    # Групуємо плани за назвою сховища
    storage_groups = {}
    for plan in all_plans:
        storage_name = plan[2]
        storage_groups.setdefault(storage_name, []).append(plan)

    # Ініціалізуємо графік
    plt.figure()
    plt.title("Storage Costs")
    plt.xlabel("Days")
    plt.ylabel("Storage Cost ($)")

    # Обробка кожного сховища
    for storage_name, plans in storage_groups.items():
        # Отримуємо вартість сховища
        storage = next((s for s in storages_data if s['name'] == storage_name), None)
        if not storage:
            print(f"Warning: Storage {storage_name} not found in storages_data.")
            continue

        storage_cost_per_gb_day = storage['cost']

        # Знаходимо максимальну кількість днів серед планів
        max_days = max(len(plan[4]) for plan in plans)

        # Розраховуємо сумарне використання
        total_usage = [0] * max_days
        for plan in plans:
            for day, size in enumerate(plan[4]):
                total_usage[day] += size

        # Розраховуємо витрати на сховище
        total_storage_cost = [usage / storage_cost_per_gb_day for usage in total_usage]

        # Виводимо графік для сховища
        plt.plot(  range(1, len(total_storage_cost) + 1), total_storage_cost, label=storage_name, linestyle='-', linewidth=2)


    # Додаткові налаштування графіка
    plt.legend()
    plt.grid(True)
    plt.show()

def get_incremental_storage(time, server, plan, full_backup_size, save_number):
    # Розпаковка даних з плану та сервера
    plan_name, backup_type, server_name, storage_name, retention, cron_schedule = (
        plan['name'], plan['type'], plan['server'], plan['storage'], int(plan['retention']), plan['schedule']
    )
    daily_increase, size = server['daily_increase'], server['size']

    # Ініціалізація масиву для інформації про копії по днях
    storage_day_info = np.zeros((time, 2), dtype=object)
    for i in range(time):
        storage_day_info[i, 0] = []  # Список розмірів копій
        storage_day_info[i, 1] = 0  # Сума розмірів

    # Отримання дат резервного копіювання на основі розкладу
    cron_dates = get_cron_dates(cron_schedule, time)

    # Ініціалізація списку поточних копій
    current_backups = []

    # Обробка кожного дня
    for day in range(0, time + 1):
        # Розрахунок розміру на основі збільшення та останньої повної копії
        print("Опа",full_backup_size[5])
        try:
            size = int(full_backup_size[5][day - 1][-1])
        except:
            size=0

        if day in cron_dates:  # Якщо день входить у розклад
            backup_size = round((size * daily_increase) / 100)
            current_backups.append(backup_size)

            # Видалення старих копій, якщо їх кількість перевищує ту яка поміщається між двома повними копіями
            while len(current_backups) > save_number[day - 2]:
                current_backups.pop(0)

        # Оновлення інформації про копії для поточного дня
        storage_day_info[day - 1, 0] = current_backups.copy()
        storage_day_info[day - 1, 1] = round(sum(current_backups))

    # Повернення масиву з інформацією про резервний план
    return [
        plan_name,  # Назва плану
        backup_type,  # Тип резервного копіювання
        storage_name,  # Назва сховища
        server_name,  # Назва сервера
        [storage_day_info[i, 1] for i in range(time)],  # Сумарні розміри по днях
        [storage_day_info[i, 0] for i in range(time)]  # Розміри копій для кожного дня
    ]

def get_incremental_count(time,full_backup_days,incremental_backup_days):
    result = []
    for day in range(1, time):  # Діапазон днів (1-30)
        # Знаходимо останній день повної копії до поточного дня
        last_full_backup = max([backup_day for backup_day in full_backup_days if backup_day <= day], default=None)

        # Якщо це повний бекап, то зберігаємо лише сам цей день
        if day in full_backup_days:
            result.append(1) # У день повної копії зберігаються лише нові інкрементні копії
            continue

        # Зберігаємо всі інкрементні копії між останньою повною і поточним днем
        incrementals_to_keep = [
            backup_day for backup_day in incremental_backup_days
            if last_full_backup is not None and last_full_backup <= backup_day <= day
        ]
        result.append(len(incrementals_to_keep))
    #print("Backup_count:",result)
    return(result)

def show_RTO_plots(servers_data, storages_data, plans_data,all_RTOs):
    #print(all_RPOs)
    servers_groups = {}
    for rtos in all_RTOs:
        server_name = rtos[3]
        if server_name not in servers_groups:
            servers_groups[server_name] = []
        servers_groups[server_name].append(rtos)
    print(servers_groups)
    # Створюємо графіки
    for server_name, plans in servers_groups.items():
        if not plans:  # Пропускаємо, якщо немає даних
            continue
        plt.figure()  # Створюємо нову фігуру
        for plan in plans:
            if not plan[4]:  # Пропускаємо порожні масиви даних
                continue
            plan_name = plan[0]
            days = list(range(1, len(plan[4]) + 1))  # Дні
            linestyle = '--' if plan[1] == "Incremental" else '-'  # Пунктирна для Incremental
            plt.plot(days, plan[4], label=f"{plan_name} ({plan[2]})",linestyle=linestyle,marker='o')  # Додаємо графік

        # Налаштування графіка для сховища
        plt.title(f"RTO value for {server_name}")
        plt.xlabel("Days")
        plt.ylabel("Seconds")
        plt.legend()
        plt.grid(True)
        plt.show()

def get_full_plan_RTO(plan, speed):
    #Розрахунок RTO (Recovery Time Objective) для кожного дня відповідно до плану резервного копіювання.

    # Розпаковка параметрів плану
    plan_name, plan_type, storage, server_name, days_size, daily_size = plan

    # Ініціалізація списку для збереження RTO
    current_rto = []

    # Розрахунок RTO для кожного дня
    for day in range(len(days_size)):
        day_rto = daily_size[day][-1] / speed if daily_size[day] else 0
        current_rto.append(day_rto)
    print(current_rto)
    # Повертаємо результати
    return [plan_name, plan_type, storage, server_name, current_rto]

def get_incremental_plan_RTO(plan,speed):
    #Розрахунок RTO (Recovery Time Objective) для кожного дня відповідно до плану резервного копіювання.
    #print("bababsda",plan)
    # Розпаковка параметрів плану
    plan_name, plan_type, storage, server_name, days_size, daily_size = plan

    # Ініціалізація списку для збереження RTO
    current_rto = []

    # Розрахунок RTO для кожного дня
    for day in range(len(days_size)):
        day_rto = days_size[day] / speed if days_size[day] else 0
        current_rto.append(day_rto)
    print(current_rto)
    # Повертаємо результати
    return [plan_name, plan_type, storage, server_name, current_rto]

def calculate_RTO(servers_data, storages_data, plans_data, time):
    # Розрахунок RTO (Recovery Time Objective) для всіх планів резервного копіювання.
    storage_usage_by_plan = calculate_storage_usage(time, servers_data, plans_data)  # Розраховуємо використання сховища кожним з планів копіювання
    all_RTOs = []

    # Функція для пошуку відповідного сховища за назвою
    def get_storage_by_name(storage_name):
        return next((s for s in storages_data if s['name'] == storage_name), None)

    # Функція для пошуку найбільш частого повного плану
    def get_matching_full_plan(full_plans, server_name, storage_name):
        most_frequent_plan = get_most_frequent_full_plan(full_plans, time)
        return next((p for p in storage_usage_by_plan if p[2] == most_frequent_plan['storage']
                     and p[3] == most_frequent_plan['server'] and p[0] == most_frequent_plan['name']), None)

    for plan in storage_usage_by_plan:
        storage_name = plan[2]
        server_name = plan[3]
        plan_type = plan[1]

        # Отримуємо сховище та швидкість відновлення
        storage = get_storage_by_name(storage_name)
        restore_speed = storage.get('restore_speed')

        if plan_type == 'Full':
            rto = get_full_plan_RTO(plan, restore_speed)
            all_RTOs.append(rto)
        else:
            full_plans = [p for p in plans_data if p['type'] == "Full" and p['server'] == server_name and p['storage'] == storage_name]
            matching_plan = get_matching_full_plan(full_plans, server_name, storage_name)

            if matching_plan:
                rto_full = get_full_plan_RTO(matching_plan, restore_speed)
                rto_incremental = get_incremental_plan_RTO(plan, restore_speed)

                # Сумуємо значення для повного і інкрементного планів
                rto_incremental[-1] = [round(full + incr, 2) for full, incr in zip(rto_full[-1], rto_incremental[-1])]
                all_RTOs.append(rto_incremental)

    print(all_RTOs)
    return all_RTOs


def show_RPO_plots(servers_data, storages_data, plans_data, all_RPOs):
    # Групуємо по серверах
    server_groups = {}
    for rpos in all_RPOs:
        server_name = rpos[1]  # Отримуємо ім'я сервера з даних RPO
        server_groups.setdefault(server_name, []).append(rpos)  # Групуємо по серверу

    # Створюємо графіки для кожного сервера
    for server_name, plans in server_groups.items():
        if not plans:  # Якщо для сервера немає планів, пропускаємо
            continue

        plt.figure()  # Створюємо нову фігуру для кожного сервера
        for plan in plans:
            plan_name, server, storage, rpo_values = plan
            if not rpo_values:  # Пропускаємо плани без значень RPO
                continue

            days = list(range(1, len(rpo_values) + 1))  # Створюємо список днів
            linestyle = '--' if plan[1] == "Incremental" else '-'  # Пунктир для Incremental, суцільний для інших

            # Додаємо графік для плану
            plt.plot(days, rpo_values, label=f"{plan_name} ({storage})", linestyle=linestyle, marker='o')

            # Налаштування графіка
        plt.title(f"RPO value for {server_name}")
        plt.xlabel("Days")
        plt.ylabel("Hours")
        plt.legend()
        plt.grid(True)
        plt.show()


def calculate_RPO(servers_data, storages_data, plans_data, time):
    # Розрахунок RPO (Recovery Point Objective) для всіх планів резервного копіювання.

    all_RPOs = []

    for plan in plans_data:
        plan_name = plan['name']
        plan_type = plan['type']
        tool = plan['tool']
        server_name = plan['server']
        storage_name = plan['storage']
        retention = int(plan['retention'])
        cron_schedule = plan['schedule']

        cron_dates = get_cron_dates(cron_schedule, time)  # Отримуємо список дат резервного копіювання
        plan_RPOs = []

        last_rpo = 0  # Початкове значення RPO для першого дня

        for day in range(1, time + 1):  # Перебір усіх днів до 'time'
            if day in cron_dates:
                # Якщо день є в cron_dates, то RPO для цього дня буде 0 (резервна копія є)
                plan_RPOs.append(0)
                last_rpo = 0  # Оновлюємо останнє значення RPO
            else:
                # Якщо копія не була зроблена в цей день, збільшуємо RPO на 24 години
                plan_RPOs.append(last_rpo + 24)
                last_rpo += 24  # Оновлюємо останнє значення RPO для наступних днів

        # Додаємо результат в загальний список
        all_RPOs.append([plan_name, server_name, storage_name, plan_RPOs])

    print(all_RPOs)
    return all_RPOs




