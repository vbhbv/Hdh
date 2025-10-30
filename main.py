# main.py

import os
import telegram
from telegram.ext import Updater, CommandHandler
from database_module import get_book_by_semantic_search 

# يتم سحب القيم من متغيرات بيئة Railway
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") 
# نستخدم اسم القناة (@lovekotob) لإعادة التوجيه
CHANNEL_USERNAME = os.environ.get("MASTER_CHANNEL_USERNAME") 

def start(update, context):
    """الرد على أمر /start"""
    update.message.reply_text('مرحباً بك في المكتبة النوعية! ابحث بموضوع الكتاب أو اسمه باستخدام /بحث.')

def semantic_search(update, context):
    """وظيفة البحث الدلالي وإعادة توجيه الملفات"""
    if not context.args:
        update.message.reply_text("الرجاء كتابة استعلام البحث بعد الأمر. مثال: /بحث قوة الإرادة")
        return

    query = " ".join(context.args)
    
    # استدعاء دالة البحث الدلالي
    results = get_book_by_semantic_search(query, limit=3)
    
    if not results:
        update.message.reply_text(f"عفواً، لم نجد نتائج تتطابق دلالياً مع طلبك: {query}")
        return

    update.message.reply_text(f"وجدنا {len(results)} نتيجة ذات صلة دلالياً. يتم إرسال الملفات...")
    
    # معالجة النتائج وإرسالها
    for book in results:
        message_id = book.get('telegram_message_id')
        
        # النقلة النوعية: إعادة توجيه الملف باستخدام Message ID
        if message_id and CHANNEL_USERNAME:
            try:
                context.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=CHANNEL_USERNAME, # نستخدم اسم المستخدم @lovekotob
                    message_id=message_id
                )
            except Exception as e:
                 # إرسال رسالة خطأ إذا لم يتمكن البوت من الوصول للملف (مثلاً، إذا لم يكن البوت مديراً في القناة)
                 print(f"Error forwarding message: {e}") 
                 update.message.reply_text(f"لم نتمكن من الوصول إلى ملف: {book['title']}. (قد تحتاج صلاحيات وصول).")
        else:
             update.message.reply_text(f"بيانات الملف {book['title']} غير مكتملة.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("بحث", semantic_search))
    
    # بدء تشغيل البوت 
    updater.start_polling() 
    updater.idle()

if __name__ == '__main__':
    main()
