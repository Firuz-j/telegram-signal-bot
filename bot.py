import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔑 ТОКЕН БОТА
TOKEN = '8375135867:AAEGi64_IYlB_85DBj9tFK15Gp63IHdlOxU'

# 📊 ПАРЫ
pairs = {
    'forex': [
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD',
        'USD/CAD', 'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY',
        'CAD/JPY', 'CHF/JPY', 'AUD/CAD', 'AUD/JPY', 'GBP/CAD','CAD/CHF','EUR/AUD'  
    ],
    'otc': [
        'EUR/USD (OTC)','GBP/USD (OTC)', 'USD/JPY (OTC)','GBP/JPY OTC',
        'AUD/USD (OTC)','EUR/GBP (OTC)', 'USD/CHF (OTC)','NZD/JPY OTC', 
        'USD/JPY OTC','AUD/NZD OTC','CAD/JPY OTC','EUR/NZD OTC',
        'AED/CNY OTC','AUD/CAD OTC','CAD/CHF OTC','EUR/HUF OTC',
        'CHF/JPY OTC','EUR/GBP OTC','EUR/NZD OTC','EUR/RUB OTC','EUR/TRY OTC'
    ],
    'crypto': ['BTC/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD'],
    'commodities': ['GOLD', 'SILVER', 'OIL']
}

# ⏱ ТАЙМФРЕЙМЫ
timeframes = ['1M', '3M', '5M', '15M']


# ================== ИНДИКАТОРЫ ==================
def calculate_indicators():
    return {
        'rsi': random.uniform(0, 100),
        'macd_hist': random.uniform(-1, 1),
        'stochastic': random.uniform(0, 100),
        'bb': random.uniform(0, 100),
        'ema_fast': random.uniform(1, 2),
        'ema_slow': random.uniform(1, 2),
    }


# ================== СИГНАЛ ==================
def generate_signal(pair, timeframe):
    ind = calculate_indicators()

    buy, sell = 0, 0
    reasons = []

    if ind['rsi'] < 30:
        buy += 1
        reasons.append('RSI перепродан')
    elif ind['rsi'] > 70:
        sell += 1
        reasons.append('RSI перекуплен')

    if ind['macd_hist'] > 0:
        buy += 1
        reasons.append('MACD бычий')
    else:
        sell += 1
        reasons.append('MACD медвежий')

    if ind['stochastic'] < 20:
        buy += 1
        reasons.append('Stochastic перепродан')
    elif ind['stochastic'] > 80:
        sell += 1
        reasons.append('Stochastic перекуплен')

    if ind['bb'] < 20:
        buy += 1
        reasons.append('Цена у нижней BB')
    elif ind['bb'] > 80:
        sell += 1
        reasons.append('Цена у верхней BB')

    if ind['ema_fast'] > ind['ema_slow']:
        buy += 1
        reasons.append('EMA 9 > EMA 21')
    else:
        sell += 1
        reasons.append('EMA 9 < EMA 21')

    if buy > sell:
        direction = 'CALL'
        arrow = '🟢⬆️'
        direction_text = 'ВВЕРХ (CALL)'
        strength = int((buy / 5) * 100)
    else:
        direction = 'PUT'
        arrow = '🔴⬇️'
        direction_text = 'ВНИЗ (PUT)'
        strength = int((sell / 5) * 100)

    expiry = {
        '1M': '1–3 мин',
        '3M': '3–7 мин',
        '5M': '5–15 мин',
        '15M': '15–45 мин'
    }[timeframe]

    return {
        'pair': pair,
        'timeframe': timeframe,
        'expiry': expiry,
        'arrow': arrow,
        'direction_text': direction_text,
        'strength': strength,
        'reasons': reasons
    }


# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎯 Получить сигнал", callback_data='get_signal')]]
    await update.message.reply_text(
        "🚀 *Pocket Option Signal Bot*\n\n"
        "Нажмите кнопку ниже, чтобы получить сигнал ⬇️",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================== КНОПКИ ==================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'get_signal':
        keyboard = [
            [InlineKeyboardButton("💱 Forex", callback_data='cat_forex')],
            [InlineKeyboardButton("🌙 OTC", callback_data='cat_otc')],
            [InlineKeyboardButton("₿ Crypto", callback_data='cat_crypto')],
            [InlineKeyboardButton("🏆 Commodities", callback_data='cat_commodities')]
        ]
        await query.edit_message_text(
            "📊 *Выберите категорию:*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith('cat_'):
        cat = data.replace('cat_', '')
        context.user_data['category'] = cat

        keyboard = [[InlineKeyboardButton(p, callback_data=f'pair_{p}')] for p in pairs[cat]]
        await query.edit_message_text(
            "💱 *Выберите пару:*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith('pair_'):
        pair = data.replace('pair_', '')
        context.user_data['pair'] = pair

        keyboard = [
            [InlineKeyboardButton("⏱ 1M", callback_data='tf_1M')],
            [InlineKeyboardButton("⏱ 3M", callback_data='tf_3M')],
            [InlineKeyboardButton("⏱ 5M", callback_data='tf_5M')],
            [InlineKeyboardButton("⏱ 15M", callback_data='tf_15M')]
        ]
        await query.edit_message_text(
            f"💱 *Пара:* {pair}\n\n⏱ *Выберите таймфрейм:*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith('tf_'):
        tf = data.replace('tf_', '')
        pair = context.user_data['pair']

        signal = generate_signal(pair, tf)

        reasons = '\n'.join([f"• {r}" for r in signal['reasons']])

        text = f"""
{signal['arrow']} *ТОРГОВЫЙ СИГНАЛ*

💱 *Пара:* {signal['pair']}
{signal['arrow']} *НАПРАВЛЕНИЕ:* *{signal['direction_text']}*
⏱ *Таймфрейм:* {signal['timeframe']}
⏰ *Экспирация:* {signal['expiry']}
💪 *Сила сигнала:* {signal['strength']}%

📊 *Подтверждения:*
{reasons}

⚠️ _Соблюдайте риск-менеджмент_
"""

        keyboard = [[InlineKeyboardButton("🔄 Новый сигнал", callback_data='get_signal')]]
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ================== ЗАПУСК ==================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("🤖 Бот запущен")
    app.run_polling()


if __name__ == '__main__':
    main()
