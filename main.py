"""
Трубомер - полная версия с голосовым вводом для APK
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from datetime import datetime
import json
import re
import threading

# Импорт speech_recognition (будет работать в APK)
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False

# ============= ПАРСИНГ =============
def parse_length(text):
    text = text.lower().strip()
    
    words = {
        'ноль': '0', 'один': '1', 'два': '2', 'три': '3', 'четыре': '4',
        'пять': '5', 'шесть': '6', 'семь': '7', 'восемь': '8', 'девять': '9',
        'десять': '10', 'одиннадцать': '11', 'двенадцать': '12', 'тринадцать': '13',
        'четырнадцать': '14', 'пятнадцать': '15', 'шестнадцать': '16', 'семнадцать': '17',
        'восемнадцать': '18', 'девятнадцать': '19', 'двадцать': '20', 'тридцать': '30',
        'сорок': '40', 'пятьдесят': '50', 'шестьдесят': '60', 'семьдесят': '70',
        'восемьдесят': '80', 'девяносто': '90', 'сто': '100', 'двести': '200',
        'триста': '300', 'четыреста': '400', 'пятьсот': '500', 'шестьсот': '600',
        'семьсот': '700', 'восемьсот': '800', 'девятьсот': '900'
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
        after = text[pos + len(num_str):pos + len(num_str) + 20]
        
        if 'километр' in after or 'км' in after:
            total += num * 1000
        elif 'метр' in after or 'м ' in after:
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

# ============= ПРИЛОЖЕНИЕ =============
class PipeApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.measurements = []
        self.load()
        self.recognizer = sr.Recognizer() if SPEECH_AVAILABLE else None
    
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
        
        # Заголовок
        title = Label(text="ТРУБОМЕР", font_size='24sp', size_hint_y=0.08)
        root.add_widget(title)
        
        # Поле ввода
        self.input = TextInput(
            hint_text="Введите длину\nПример: 2 метра 50 см",
            multiline=False,
            size_hint_y=0.15
        )
        root.add_widget(self.input)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.12, spacing=10)
        
        if SPEECH_AVAILABLE:
            self.voice_btn = Button(text="🎤 Голосом")
            self.voice_btn.bind(on_press=self.voice_input)
            btn_layout.add_widget(self.voice_btn)
        
        save_btn = Button(text="📝 Сохранить")
        save_btn.bind(on_press=self.save_measurement)
        
        show_btn = Button(text="📋 Показать")
        show_btn.bind(on_press=self.show_measurements)
        
        clear_btn = Button(text="🗑️ Очистить")
        clear_btn.bind(on_press=self.clear_all)
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(show_btn)
        btn_layout.add_widget(clear_btn)
        root.add_widget(btn_layout)
        
        # Статистика
        self.stats = Label(text=self.get_stats(), size_hint_y=0.08)
        root.add_widget(self.stats)
        
        # Область вывода
        scroll = ScrollView(size_hint_y=0.45)
        self.output = Label(text="Готов к работе", size_hint_y=None, font_size='14sp')
        self.output.bind(texture_size=self.output.setter('size'))
        scroll.add_widget(self.output)
        root.add_widget(scroll)
        
        return root
    
    def get_stats(self):
        if not self.measurements:
            return "📊 Нет замеров"
        total = sum(m['length'] for m in self.measurements)
        return f"📊 Замеров: {len(self.measurements)} | Всего: {format_length(total)}"
    
    def save_measurement(self, instance):
        text = self.input.text.strip()
        if not text:
            self.output.text = "❌ Введите значение"
            return
        
        length = parse_length(text)
        
        if length == 0:
            self.output.text = "❌ Не распознано\nПример: 2 метра 50 см"
            return
        
        self.add_measurement(text, length)
    
    def voice_input(self, instance):
        if not SPEECH_AVAILABLE:
            self.output.text = "❌ Голосовой ввод недоступен"
            return
        
        self.voice_btn.disabled = True
        self.output.text = "🎤 Слушаю... Говорите чётко"
        
        def record():
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio, language="ru-RU")
                    Clock.schedule_once(lambda dt: self.process_voice(text))
            except sr.WaitTimeoutError:
                Clock.schedule_once(lambda dt: self.set_output("⏰ Время истекло"))
            except sr.UnknownValueError:
                Clock.schedule_once(lambda dt: self.set_output("🔇 Речь не распознана"))
            except sr.RequestError:
                Clock.schedule_once(lambda dt: self.set_output("🌐 Ошибка интернета"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.set_output(f"❌ Ошибка: {e}"))
            finally:
                Clock.schedule_once(lambda dt: self.enable_voice_btn())
        
        threading.Thread(target=record, daemon=True).start()
    
    def process_voice(self, text):
        self.output.text = f"📝 Распознано: {text}"
        length = parse_length(text)
        
        if length > 0:
            self.add_measurement(text, length)
        else:
            self.output.text = f"❌ Не распознано: {text}\n\nПример: два метра пятьдесят сантиметров"
    
    def add_measurement(self, text, length):
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
        self.output.text = f"✅ Добавлено: {format_length(length)}"
    
    def set_output(self, text):
        self.output.text = text
    
    def enable_voice_btn(self):
        self.voice_btn.disabled = False
    
    def show_measurements(self, instance):
        if not self.measurements:
            self.output.text = "📭 Нет замеров"
            return
        
        total = sum(m['length'] for m in self.measurements)
        text = f"📋 ВСЕГО: {len(self.measurements)} замеров\n"
        text += f"📏 Общая длина: {format_length(total)}\n"
        text += "═" * 30 + "\n\n"
        
        for i, m in enumerate(self.measurements[-10:], 1):
            text += f"{i}. {m['formatted']} - {m['date']} {m['time']}\n"
            text += f"   {m['text'][:35]}\n\n"
        
        self.output.text = text
    
    def clear_all(self, instance):
        self.measurements = []
        self.save()
        self.stats.text = self.get_stats()
        self.output.text = "✅ Все замеры удалены"

if __name__ == '__main__':
    PipeApp().run()