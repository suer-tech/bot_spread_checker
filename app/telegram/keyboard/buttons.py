async def main_butts():
    return [
        ("Спреды", "show_spreads"),
        ("Точки входа", "entry_points"),
        ("Сигналы по значению", "value_signals"),
        ("Сигналы по процентам", "percent_signals")
    ]


async def entry_point():
    return [("Новая ТВХ", "new_entry_"),
           ("Сбросить ТВХ", "reset_entry_")]

class Button:
    def __init__(self, asset_name=None):
        self.asset_name = asset_name

    async def static(self):
        return [
            "Главное меню",
        ]

    async def asset(self):
        return [("Спред", "spread_" + self.asset_name),
                ("Точка входа", "entry_point_" + self.asset_name),
                ("Сигналы", "signals_" + self.asset_name)]


    async def signals(self):
        return [("Сигнал по значению", "valuesignals_" + self.asset_name),
                ("Сигнал по процентному отклонению", "current_percent_signal_" + self.asset_name)]

    async def value_signals(self):
        return [("Текущий сигнал по значению", "current_value_signal_" + self.asset_name),
               ("Новый сигнал по значению", "new_value_signal_" + self.asset_name),
               ("Сбросить сигнал по значению", "reset_value_signal_" + self.asset_name)]

    async def percent_signals(self):
        return [("Текущий сигнал по процентам", "current_percent_signal_" + self.asset_name),
               ("Новый сигнал по процентам", "new_percent_signal_" + self.asset_name),
               ("Сбросить сигнал по процентам", "reset_percent_signal_" + self.asset_name)]