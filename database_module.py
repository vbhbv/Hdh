# database_module.py

import os
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer 
import numpy as np

# ************** تم تعديل هذا السطر خصيصاً للفهرسة المحلية المؤقتة **************
# عند الانتهاء من الفهرسة والدفع إلى GitHub، يجب إعادته إلى: DB_URL = os.environ.get("DATABASE_URL")
DB_URL = "postgresql://postgres:EwUGqTGEqNMIZEGVApfkTpjLEwpbYRPR@postgres.railway.internal:5432/railway" 
# ********************************************************************************

# نموذج لغوي بسيط وفعّال لإنشاء المتجهات (الحجم 384)
model = SentenceTransformer('all-MiniLM-L6-v2') 

def get_db_connection():
    """إنشاء اتصال بقاعدة بيانات PostgreSQL وتفعيل دعم المتجهات"""
    try:
        conn = psycopg2.connect(DB_URL)
        register_vector(conn)
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

def embed_text(text: str) -> list:
    """تحويل النص إلى متجه رقمي (Vector) للبحث الدلالي"""
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()

def get_book_by_semantic_search(query: str, limit: int = 5):
    """تنفيذ البحث الدلالي (Vector Search)"""
    conn = get_db_connection()
    if conn is None:
        return []
        
    query_vector = embed_text(query) # متجه استعلام البحث
    cur = conn.cursor()

    query_sql = f"""
    SELECT title, author, telegram_message_id, summary
    FROM library_index
    ORDER BY summary_vector <-> %s
    LIMIT %s;
    """
    
    try:
        cur.execute(query_sql, (str(query_vector), limit))
        results = cur.fetchall()
    except Exception as e:
        print(f"Error executing semantic search: {e}")
        results = []
        
    conn.close()
    
    books = []
    for row in results:
        books.append({
            'title': row[0],
            'author': row[1],
            'telegram_message_id': row[2],
            'summary': row[3]
        })
    return books
