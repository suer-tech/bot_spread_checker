async def calculate_spread(instrument):
    print('')
    print('calculate_spread')
    print('')
    base = instrument.base
    future = instrument.future

    count_digits = len(str(base).split('.')[0])
    future = round(future, count_digits)
    spread = future - base
    print(spread)

    return spread




