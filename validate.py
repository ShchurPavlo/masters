import re

def check_cron(cron_expression):
    #Перевіряє, чи є вираз у форматі CRON.
    cron_regex = re.compile(
        r'^([0-5]?\d|\*|\*/[1-5]?\d) '                # Хвилини
        r'([01]?\d|2[0-3]|\*|\*/[1-9]\d*) '          # Години
        r'([01]?\d|2[0-9]|3[01]|\*|\*/[1-9]\d*) '    # День місяця
        r'(0?[1-9]|1[0-2]|\*|\*/[1-9]\d*) '          # Місяць
        r'([0-7]{1,1}|[0-7](?:,[0-7]+)+|\*|\*/[1-7])$' # День тижня (враховує коми)
    )
    return bool(cron_regex.match(cron_expression))

def validate_numeric(value):
    """Функція для перевірки, чи є значення числом і чи є воно позитивним."""
    try:
        num_value = float(value)  # Перевіряє, чи є значення числовим (може бути дробовим)
        return num_value > 0  # Перевіряє, чи є число позитивним
    except ValueError:
        return False

def check_servers_data(servers_data):
    errors = []
    for server in servers_data:
        if not validate_numeric(server['size']):
            errors.append(
                f"Error in server parameters '{server['name']}'")
        if not validate_numeric(server['daily_increase']):
            errors.append(
                f"Error in server parameters '{server['name']}'")
    if errors:
        return "\n".join(errors)
    return True

def check_storages_data(storages_data):
    errors = []
    for storage in storages_data:
        if not validate_numeric(storage['cost']):
            errors.append(
                f"Error in storage parameters '{storage['name']}'")
        if not validate_numeric(storage['save_speed']):
            errors.append(
                f"Error in storage parameters '{storage['name']}'")
        if not validate_numeric(storage['restore_speed']):
            errors.append(
                f"Error in storage parameters '{storage['name']}'")
    if errors:
        return "\n".join(errors)
    return True

def check_plans_data(plans_data):
    errors = []
    for plan in plans_data:
        # Перевіряємо поле 'retention' на числове значення
        if not validate_numeric(plan['retention']):
            errors.append(f"Error in backup plan '{plan['name']}'")
        if not plan['server']:
            errors.append(f"Error in backup plan '{plan['name']}': No server selected.")

        if not plan['storage']:
            errors.append(f"Error in backup plan '{plan['name']}': No storage selected.")

        if not plan['type']:
            errors.append(f"Error in backup plan '{plan['name']}': No type selected.")

        if not plan['tool']:
            errors.append(f"Error in backup plan '{plan['name']}': No backup tool selected.")
        # Перевіряємо, чи cron-вираз правильний
        if not check_cron(plan['schedule']):
            errors.append(f"Error in backup plan '{plan['name']}'")
            print('CRON:',check_cron(plan['schedule']))
    # Якщо є помилки, повертаємо їх список
    if errors:
        return "\n".join(errors)
    return True

def convert_to_float(data):
    if isinstance(data, dict):
        return {key: convert_to_float(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_float(item) for item in data]
    else:
        try:
            return float(data)
        except (ValueError, TypeError):
            return data
