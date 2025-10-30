# telegram_indexer.py - يجب تشغيله محلياً لمرة واحدة لملء قاعدة البيانات

from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument
import os
import hashlib
from database_module import get_db_connection, embed_text 

# *تم التعديل بالقيم الجديدة*
API_ID = 26597373 
API_HASH = '03b65897b8dfe7b9d237fb69d687d61'
# اسم القناة التي تريد فهرسة محتواها (مأخوذ من السياق السابق)
CHANNEL_USERNAME = '@lovekotob'

def generate_file_hash_from_bytes(data):
    """يولد الهاش (البصمة) الثابتة للبيانات الثنائية"""
    return hashlib.sha256(data).hexdigest()

def index_channel_messages():
    """الفهرسة التلقائية لرسائل القناة باستخدام حساب المستخدم"""
    conn = get_db_connection()
    if conn is None: return

    cur = conn.cursor()

    # الاتصال بحساب المستخدم باستخدام الـ API ID والـ API Hash الجديدين
    try:
        with TelegramClient('session_name', API_ID, API_HASH) as client:
            print(f"Connecting to channel {CHANNEL_USERNAME}...")
            
            # جلب جميع الرسائل من القناة
            for message in client.iter_messages(CHANNEL_USERNAME):
                
                # التأكد من أن الرسالة تحتوي على ملف (كتاب PDF/DOC/ePub)
                if message.media and isinstance(message.media, MessageMediaDocument):
                    
                    summary = message.text or message.media.document.mime_type or "كتاب إلكتروني"
                    title = message.file.name if message.file and message.file.name else f"ملف ID: {message.id}"
                    
                    # 1. توليد المتجه (الفيكتور) للبحث الدلالي
                    summary_vector = embed_text(summary)
                    
                    # 2. استخدام Message ID كبصمة مؤقتة فريدة
                    file_hash = f"TG-{message.id}" 

                    # 3. إدراج البيانات
                    insert_query = """
                    INSERT INTO library_index (title, file_hash, summary, telegram_message_id, summary_vector)
                    VALUES (%s, %s, %s, %s, %s::vector)
                    ON CONFLICT (file_hash) DO NOTHING;
                    """
                    
                    cur.execute(insert_query, (
                        title,
                        file_hash,
                        summary,
                        message.id,
                        str(summary_vector) 
                    ))
                    print(f"Indexed: {title} (ID: {message.id})")

        conn.commit()
        conn.close()
        print("Indexing complete.")

    except Exception as e:
        print(f"FATAL ERROR: Could not connect or index the channel. Make sure to run the script locally first.\nError: {e}")
        if conn: conn.close()


if __name__ == '__main__':
    index_channel_messages()
  
