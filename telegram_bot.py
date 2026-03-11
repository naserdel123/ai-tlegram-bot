import logging
import os
import re
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode

# ==================== إعدادات البوت ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")          # ← ضع توكن البوت هنا
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "YOUR_CLAUDE_API_KEY_HERE")  # ← ضع مفتاح Claude API هنا
DEVELOPER = "@N_Naser11"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== رسالة الترحيب ====================
WELCOME_MESSAGE = """
╔══════════════════════════════╗
║   🤖 أهلاً بك في بوت الذكاء الاصطناعي   ║
╚══════════════════════════════╝

✨ *مرحباً بك أيها المميز!* ✨

أنا بوتك الذكي المتكامل، جاهز لخدمتك على مدار الساعة 🌙

━━━━━━━━━━━━━━━━━━━━━━━━

🎵 *أبحث لك عن أي أغنية تريدها*
🧠 *أجاوب على أسئلتك بذكاء اصطناعي متقدم*
⚡ *أعمل بسرعة البرق وكفاءة عالية*

━━━━━━━━━━━━━━━━━━━━━━━━

📌 *كيف تستخدمني؟*
• اكتب `/search اسم الأغنية` للبحث عن أغنية
• اكتب `/ask سؤالك` للحصول على إجابة ذكية
• اكتب `/help` لرؤية جميع الأوامر

━━━━━━━━━━━━━━━━━━━━━━━━

🔥 *أضفني في مجموعتك وأمتع أصدقاءك!*

```
[زر الإضافة للمجموعة أدناه 👇]
```

━━━━━━━━━━━━━━━━━━━━━━━━
💎 *المطور:* {}
""".format(DEVELOPER)

# ==================== دالة Claude AI ====================
async def ask_claude(prompt: str, system_prompt: str = "") -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    messages = [{"role": "user", "content": prompt}]
    
    body = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "messages": messages
    }
    
    if system_prompt:
        body["system"] = system_prompt
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["content"][0]["text"]
                else:
                    error = await resp.text()
                    logger.error(f"Claude API error: {error}")
                    return "❌ حدث خطأ في الاتصال بالذكاء الاصطناعي."
    except Exception as e:
        logger.error(f"Claude error: {e}")
        return "❌ تعذر الاتصال بالذكاء الاصطناعي حالياً."

# ==================== البحث عن أغنية ====================
async def search_song_with_ai(song_name: str) -> str:
    system = """أنت مساعد موسيقي متخصص. عندما يطلب المستخدم البحث عن أغنية، 
    قدّم معلومات عنها بشكل جميل ومنظم باللغة العربية. اذكر:
    - اسم الأغنية والفنان
    - سنة الإصدار إن كانت معروفة
    - وصف مختصر وجميل عن الأغنية
    - رابط يوتيوب أو سبوتيفاي إن أمكن (اذكر أنه للبحث فقط)
    استخدم إيموجي جميلة لتنسيق الرد."""
    
    prompt = f"ابحث عن الأغنية التالية وقدم معلومات عنها: {song_name}"
    return await ask_claude(prompt, system)

# ==================== أوامر البوت ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /start - رسالة ترحيبية"""
    bot_username = context.bot.username
    
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ أضفني لمجموعتك",
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("🎵 بحث أغنية", callback_data="help_search"),
            InlineKeyboardButton("🧠 اسأل AI", callback_data="help_ask")
        ],
        [
            InlineKeyboardButton(f"👨‍💻 المطور {DEVELOPER}", url=f"https://t.me/N_Naser11")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /help"""
    help_text = f"""
🤖 *دليل استخدام البوت*

━━━━━━━━━━━━━━━━━━━━━━━━

🎵 *البحث عن الأغاني:*
`/search اسم الأغنية`
مثال: `/search فيروز يا أنا`

━━━━━━━━━━━━━━━━━━━━━━━━

🧠 *الذكاء الاصطناعي:*
`/ask سؤالك هنا`
مثال: `/ask ما هو الذكاء الاصطناعي؟`

━━━━━━━━━━━━━━━━━━━━━━━━

💬 *محادثة مباشرة:*
يمكنك كتابة أي شيء مباشرة وسيرد عليك البوت!

━━━━━━━━━━━━━━━━━━━━━━━━

💎 *المطور:* {DEVELOPER}
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /search - البحث عن أغنية"""
    if not context.args:
        await update.message.reply_text(
            "🎵 *كيف تبحث عن أغنية؟*\n\n"
            "اكتب: `/search اسم الأغنية`\n"
            "مثال: `/search ليل الصبر`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    song_name = " ".join(context.args)
    
    # رسالة انتظار
    searching_msg = await update.message.reply_text(
        f"🔍 *جاري البحث عن:* `{song_name}`\n⏳ لحظة من فضلك...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # البحث باستخدام AI
    result = await search_song_with_ai(song_name)
    
    # حذف رسالة الانتظار
    await searching_msg.delete()
    
    # إرسال النتيجة
    response = f"🎵 *نتائج البحث عن:* `{song_name}`\n\n{result}\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n💎 *المطور:* {DEVELOPER}"
    
    await update.message.reply_text(
        response,
        parse_mode=ParseMode.MARKDOWN
    )

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /ask - سؤال الذكاء الاصطناعي"""
    if not context.args:
        await update.message.reply_text(
            "🧠 *كيف تسأل؟*\n\n"
            "اكتب: `/ask سؤالك`\n"
            "مثال: `/ask ما هي عاصمة المملكة العربية السعودية؟`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    question = " ".join(context.args)
    
    thinking_msg = await update.message.reply_text(
        "🧠 *الذكاء الاصطناعي يفكر...*\n⏳ لحظة من فضلك...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    system = "أنت مساعد ذكي ومفيد. أجب بالعربية بشكل واضح ومنظم وجميل. استخدم إيموجي مناسبة."
    answer = await ask_claude(question, system)
    
    await thinking_msg.delete()
    
    response = f"🧠 *إجابة الذكاء الاصطناعي:*\n\n{answer}\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n💎 *المطور:* {DEVELOPER}"
    
    await update.message.reply_text(
        response,
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل العادية"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    
    # تحقق إذا كان في مجموعة أو خاص
    is_group = update.message.chat.type in ["group", "supergroup"]
    
    # في المجموعة، يرد فقط إذا تم ذكره أو إذا بدأت الرسالة بكلمة معينة
    if is_group:
        bot_username = context.bot.username
        mentioned = f"@{bot_username}" in text
        search_trigger = any(w in text.lower() for w in ["ابحث", "بحث", "search", "اغنية", "أغنية", "موسيقى"])
        
        if not mentioned and not search_trigger:
            return
        
        # إزالة ذكر البوت من النص
        text = text.replace(f"@{bot_username}", "").strip()
    
    # اكتشاف إذا كان طلب بحث أغنية
    song_keywords = ["ابحث عن", "ابحث", "بحث عن", "بحث", "اغنية", "أغنية", "اغنيه", "أغنيه", "موسيقى", "search"]
    is_song_search = any(kw in text.lower() for kw in song_keywords)
    
    if is_song_search:
        # استخراج اسم الأغنية
        song_name = text
        for kw in song_keywords:
            song_name = re.sub(kw, "", song_name, flags=re.IGNORECASE).strip()
        
        if not song_name:
            song_name = text
        
        searching_msg = await update.message.reply_text(
            f"🔍 *جاري البحث عن:* `{song_name}`\n⏳ لحظة من فضلك...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        result = await search_song_with_ai(song_name)
        await searching_msg.delete()
        
        response = f"🎵 *نتائج البحث:*\n\n{result}\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n💎 *المطور:* {DEVELOPER}"
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    else:
        # رسالة عادية - أجب بالذكاء الاصطناعي
        thinking_msg = await update.message.reply_text(
            "🧠 *جاري التفكير...*",
            parse_mode=ParseMode.MARKDOWN
        )
        
        system = "أنت مساعد ذكي ومفيد. أجب بالعربية بشكل واضح ومختصر وجميل. استخدم إيموجي مناسبة."
        answer = await ask_claude(text, system)
        
        await thinking_msg.delete()
        
        response = f"{answer}\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n💎 {DEVELOPER}"
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help_search":
        await query.message.reply_text(
            "🎵 *للبحث عن أغنية:*\n\n"
            "اكتب: `/search اسم الأغنية`\n"
            "أو اكتب مباشرة: `ابحث عن اسم الأغنية`",
            parse_mode=ParseMode.MARKDOWN
        )
    elif query.data == "help_ask":
        await query.message.reply_text(
            "🧠 *للسؤال الذكاء الاصطناعي:*\n\n"
            "اكتب: `/ask سؤالك`\n"
            "أو اكتب سؤالك مباشرة في المحادثة",
            parse_mode=ParseMode.MARKDOWN
        )

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ترحيب بالأعضاء الجدد في المجموعة"""
    for member in update.message.new_chat_members:
        if member.is_bot and member.username == context.bot.username:
            # البوت انضم لمجموعة جديدة
            welcome = f"""
🎉 *شكراً لإضافتي لمجموعتكم!* 🎉

أنا بوت ذكاء اصطناعي متكامل، وسأكون سعيداً بخدمتكم!

🎵 ابحث عن أي أغنية: `/search اسم الأغنية`
🧠 اسألني أي شيء: `/ask سؤالك`
📋 قائمة الأوامر: `/help`

💎 *المطور:* {DEVELOPER}
"""
            await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN)
        else:
            # عضو جديد انضم
            name = member.full_name
            welcome = f"👋 *أهلاً وسهلاً* [{name}](tg://user?id={member.id}) *في المجموعة!* 🎉"
            await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN)

# ==================== تشغيل البوت ====================
def main():
    print("🤖 جاري تشغيل البوت...")
    print(f"💎 المطور: {DEVELOPER}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("ask", ask_command))
    
    # معالجة الأزرار
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # معالجة الأعضاء الجدد
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    
    # معالجة الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ البوت يعمل الآن!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
