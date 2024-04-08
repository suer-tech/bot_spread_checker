from decimal import Decimal


def calculate_spread(instrument):
    print('')
    print('calculate_spread')
    print('')
    base = str(instrument.base)
    future = str(instrument.future)

    # Определяем количество знаков до запятой в base и future
    base_digits_before_dot = base.index('.') if '.' in base else len(base)
    future_digits_before_dot = future.index('.') if '.' in future else len(future)

    # Если количество знаков до запятой не равно, производим выравнивание
    if base_digits_before_dot != future_digits_before_dot:
        # Получаем позицию разделителя в base
        base_dot_position = base.index('.') if '.' in base else len(base)
        # Удаляем разделитель в future
        future = future.replace('.', '')
        # Вставляем разделитель в future на позицию, где он находится в base
        future = future[:base_dot_position] + '.' + future[base_dot_position:]

    print("Spread:", base, future)
    spread = Decimal(base) - Decimal(future)

    return float(spread)




