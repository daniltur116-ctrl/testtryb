"""
Трубомер - минимальная версия
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from datetime import datetime
import json
import re

def parse_length(text):
    text = text.lower().strip()
    words = {
        'один': '1', 'два': '2', 'три': '3', 'четыре': '4', 'пять': '5',
        'шесть': '6', 'семь': '7', 'восемь': '8', 'девять': '9', 'десять': '10',
        'сто': '100', 'двести': '200', 'триста': '300', 'четыреста': '400',
        'пятьсот': '500', 'шестьсот': '600', 'семьсот': '700', 'восемьсот': '800', 'девятьсот': '900'
    }
    for word, num in words.items():
        text = text.replace(word, num)
    
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    if not numbers:
        return 0.0
    
    total = 0.0
    for num_str in numbers:
        num = float(num_str)
        pos = text.find(num_str)
        after = text[pos + len(num_str):pos + len(num_str) + 15]
        
        if 'метр' in after:
            total += num
        elif 'сантиметр' in after or 'см' in after:
            total += num / 100
        elif 'миллиметр' in after or 'мм' in after:
            total += num / 1000
        else:
            total += num
    return round(total, 3)

def format_length(m):
    if m >= 1:
        return f"{m:.2f} м"
    elif m >= 0.01:
        return f"{int(m * 100)} см"
    else:
        return f"{int(m * 1000)} мм"

class PipeApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.measurements = []
        self.load()
    
    def load(self):
        try:
            with open('measurements.json', 'r') as f:
                self.measurements = json.load(f)
        except:
            self.measurements = []
    
    def save(self):
        with open('measurements.json', 'w') as f:
            json.dump(self.measurements, f)
    
    def build(self):
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text="ТРУБОМЕР", font_size='24sp', size_hint_y=0.1)
        root.add_widget(title)
        
        self.input = TextInput(hint_text="Введите длину\n2 метра 50 см или 120 мм", multiline=False, size_hint_y=0.2)
        root.add_widget(self.input)
        
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        save_btn = Button(text="Сохранить")
        save_btn.bind(on_press=self.save_measurement)
        show_btn = Button(text="Показать")
        show_btn.bind(on_press=self.show_measurements)
        clear_btn = Button(text="Очистить")
        clear_btn.bind(on_press=self.clear_all)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(show_btn)
        btn_layout.add_widget(clear_btn)
        root.add_widget(btn_layout)
        
        self.stats = Label(text=self.get_stats(), size_hint_y=0.1)
        root.add_widget(self.stats)
        
        self.output = Label(text="Готов", size_hint_y=0.35)
        root.add_widget(self.output)
        
        return root
    
    def get_stats(self):
        if not self.measurements:
            return "Нет замеров"
        total = sum(m['length'] for m in self.measurements)
        return f"Замеров: {len(self.measurements)} | Всего: {format_length(total)}"
    
    def save_measurement(self, instance):
        text = self.input.text.strip()
        if not text:
            self.output.text = "Введите значение"
            return
        
        length = parse_length(text)
        if length == 0:
            self.output.text = "Не распознано"
            return
        
        measurement = {
            'length': length,
            'text': text,
            'formatted': format_length(length),
            'date': datetime.now().strftime('%d.%m.%Y'),
            'time': datetime.now().strftime('%H:%M:%S')
        }
        self.measurements.append(measurement)
        self.save()
        self.input.text = ''
        self.stats.text = self.get_stats()
        self.output.text = f"✅ {format_length(length)}"
    
    def show_measurements(self, instance):
        if not self.measurements:
            self.output.text = "Нет замеров"
            return
        
        text = f"Всего: {len(self.measurements)}\n"
        for m in self.measurements[-10:]:
            text += f"{m['formatted']} - {m['date']}\n"
        self.output.text = text
    
    def clear_all(self, instance):
        self.measurements = []
        self.save()
        self.stats.text = self.get_stats()
        self.output.text = "Удалено"

if __name__ == '__main__':
    PipeApp().run()
