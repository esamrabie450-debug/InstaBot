# -- coding: utf-8 --

import os
import time
import traceback
import requests
import sys
from instagrapi import Client
from telebot import TeleBot, types
import re # ⬅️ تم إضافة مكتبة التعبير النمطي (Regular Expressions)

# --------- تكوين ----------
TOKEN = "8159588526:AAGRcV4VXlKWUz6am_dPJ6G9T9pEQjdmhkM" 
SESSION_FILE = "session-No0or.M0.json"
TMP_DIR = "tmp_insta"
USERS_FILE = "users.txt"
OWNER_ID = 7370498239 

os.makedirs(TMP_DIR, exist_ok=True)

bot = TeleBot(TOKEN)
cl = Client()

# --------- حالة البوت والـ Broadcast ---------
BOT_ACTIVE = True 
awaiting_broadcast = False 

# --------- حاول تحميل الجلسة ----------
try:
    cl.load_settings(SESSION_FILE)
    print("✅ loaded session:", SESSION_FILE)
except Exception as e:
    print("⚠️ could not load session:", e)

# ---------- مساعدة لتحميل ثم إرسال ----------
def download_and_send(chat_id, url, is_video=False, timeout=30):
    try:
        r = requests.get(url, stream=True, timeout=timeout)
        r.raise_for_status()
        ext = ".mp4" if is_video else ".jpg"
        fname = os.path.join(TMP_DIR, f"insta_{int(time.time()*1000)}{ext}")
        with open(fname, "wb") as f:
            for chunk in r.iter_content(1024*64):
                if chunk:
                    f.write(chunk)
        with open(fname, "rb") as f:
            if is_video:
                bot.send_video(chat_id, f)
            else:
                bot.send_photo(chat_id, f)
        os.remove(fname)
        return True
    except Exception as e:
        print("download_and_send error:", e)
        return False

# --------- تخزين المستخدمين ---------
def save_user(chat_id):
    try:
        if not os.path.exists(USERS_FILE):
            open(USERS_FILE, "w").close()
        with open(USERS_FILE, "r") as f:
            ids = f.read().splitlines()
        if str(chat_id) not in ids:
            with open(USERS_FILE, "a") as f:
                f.write(str(chat_id) + "\n")
            print(f"[+] Saved new user: {chat_id}")
    except Exception as e:
        print("save_user error:", e)

# ----------------- دالة مساعدة لتوليد محتوى لوحة التحكم -----------------
def get_panel_content(active_status, user_count):
    status = "✅ شغال" if active_status else "❌ مقفول"

    caption = (
        f"⚙️ لوحة التحكم\n\n"
        f"👥 عدد المستخدمين الحالي: {user_count}\n\n"
        f"🚦 **حالة البوت**: {status}"
    )

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📢 بث جماعي", callback_data="dev:broadcast"))
    kb.add(types.InlineKeyboardButton("👥 عدد المستخدمين", callback_data="dev:users"))
    kb.add(types.InlineKeyboardButton("🆔 عرض ID", callback_data="dev:myid"))
    kb.add(types.InlineKeyboardButton("🚦 تبديل حالة البوت", callback_data="dev:toggle"))
    kb.add(types.InlineKeyboardButton("♻️ إعادة تشغيل", callback_data="dev:restart"))

    return caption, kb

# ---------- /start ----------
@bot.message_handler(commands=['start'])
def cmd_start(m):
    if not BOT_ACTIVE and m.chat.id != OWNER_ID:
        bot.send_message(m.chat.id, "🚫 البوت مقفول مؤقتاً من المطور.")
        return
    
    save_user(m.chat.id)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📌 ارسل يوزر انستجرام")
    
    bot.send_message(
        m.chat.id,
        "👋 أهلاً بك يا بطل! أنا هنا لمساعدتك في تحميل محتوى إنستجرام بكل سهولة.\n\n"
        "ابعت يوزر انستا (مثال: @username) أو **رابط البروفايل** علشان أعرضلك البيانات.\n\n"
        "/help لمزيد من المساعدة.\n\n"
        "🚀 **Powered by Rabi3** 🚀",
        reply_markup=kb
    )

# ---------- /myid ----------
@bot.message_handler(commands=['myid'])
def cmd_myid(m):
    bot.reply_to(m, f"🆔 الـ Chat ID بتاعك هو:\n`{m.chat.id}`", parse_mode="Markdown")

# ---------- /help ----------
@bot.message_handler(commands=['help'])
def cmd_help(m):
    help_message = (
        "❓ **طريقة استخدام البوت:**\n\n"
        "1. **إرسال البيانات:** أرسل **اسم المستخدم** (مثال: `@username`) أو **رابط البروفايل** (مثال: `https://www.instagram.com/username/`) في الشات.\n"
        "2. **الواجهة:** ستظهر لك معلومات الحساب مع أزرار الإجراءات.\n"
        "3. **الإجراءات المتاحة:**\n"
        "   - **📸 ستوري:** لتحميل آخر الستوريات النشطة.\n"
        "   - **🎞️ هايلايت:** لعرض قائمة الهايلايتس واختيار ما تريد تحميله.\n"
        "   - **🖼️ عرض آخر المنشورات:** لعرض قائمة بآخر 6 منشورات (صورة، فيديو، ألبوم).\n"
        "   - **🖼️ تحميل صورة البروفايل (HD):** لتحميل الصورة الرمزية بدقة عالية.\n\n"
        "**ملاحظة**: البوت قد يواجه صعوبة في تحميل محتوى الحسابات الخاصة. استخدم /rules للاطلاع على شروط الاستخدام."
    )
    bot.send_message(m.chat.id, help_message, parse_mode="Markdown")

# ---------- /rules ----------
@bot.message_handler(commands=['rules', 'terms'])
def cmd_rules(m):
    rules_message = (
        "📜 **شروط وأحكام استخدام البوت:**\n\n"
        "1. **الاستخدام الشخصي:** هذا البوت مخصص للاستخدام الشخصي وغير التجاري فقط.\n"
        "2. **المسؤولية:** أنت تتحمل المسؤولية الكاملة عن أي محتوى تقوم بتحميله واستخدامه.\n"
        "3. **الامتثال:** يجب عليك احترام حقوق الملكية الفكرية وخصوصية المستخدمين.\n"
        "4. **إخلاء مسؤولية:** لا يتحمل المطور أي مسؤولية عن أي استخدام غير قانوني أو ضار للبوت."
    )
    bot.send_message(m.chat.id, rules_message, parse_mode="Markdown")

# ---------- استقبال اليوزر ومعالجة البث (إصلاح الرابط النهائي) ----------
@bot.message_handler(func=lambda msg: msg.content_type == 'text' and not msg.text.startswith('/'))
def handle_username(msg):
    global awaiting_broadcast
    save_user(msg.chat.id)

    # معالجة رسالة البث
    if msg.chat.id == OWNER_ID and awaiting_broadcast:
        awaiting_broadcast = False
        msg_to_send = msg.text.strip()
        try:
            with open(USERS_FILE, "r") as f:
                ids = f.read().splitlines()
            for uid in ids:
                try:
                    bot.send_message(int(uid), msg_to_send)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"send failed to {uid} : {e}")
            bot.send_message(msg.chat.id, "✅ تم إرسال الرسالة للجميع.")
        except Exception as e:
            bot.send_message(msg.chat.id, f"⚠️ خطأ أثناء الإرسال: {e}")
        return

    # مراجعة لحالة البوت
    if not BOT_ACTIVE and msg.chat.id != OWNER_ID:
        bot.send_message(msg.chat.id, "🚫 البوت مقفول مؤقتاً من المطور.")
        return
        
    input_text = msg.text.strip()
    chat_id = msg.chat.id
    
    username = None # تهيئة المتغير
    
    # 🆕 التحقق من الرابط وتنظيفه باستخدام Regular Expressions
    if input_text.startswith("http") and "instagram.com" in input_text:
        
        try:
            # 1. إزالة أي شيء قبل اسم المستخدم بعد instagram.com/
            path = re.split(r'instagram\.com/', input_text, flags=re.IGNORECASE)[-1]
            
            # 2. إزالة أي علامات استفهام (?) أو سلاش زائدة (/) بعد اسم المستخدم
            cleaned_path = re.split(r'[\?\/]', path, maxsplit=1)[0]
            
            username = cleaned_path.strip()

            if username:
                bot.send_message(chat_id, f"✅ تم التعرف على اليوزر: **@{username}**، جاري جلب البيانات...")
            else:
                bot.send_message(chat_id, "⚠️ لم أتمكن من استخراج اسم المستخدم من الرابط. تأكد أنه رابط بروفايل فقط.")
                return
        except Exception:
            bot.send_message(chat_id, "⚠️ فشل في معالجة الرابط. يرجى التأكد من أن التنسيق صحيح.")
            return
    else:
        # إذا لم يكن رابطاً، يُعامل كنص عادي
        username = input_text.lstrip('@')
        bot.send_message(chat_id, "⏳ جاري جلب البيانات من انستجرام...")

    # باقي العملية لا تتغير، تستخدم 'username'
    try:
        uid = cl.user_id_from_username(username)
        info = cl.user_info(uid)
        
        caption = (  
            f"👤 @{info.username}\n"  
            f"📛 الاسم: {info.full_name or '—'}\n"  
            f"📝 البايو: {info.biography or '—'}\n"  
            f"👥 المتابعون: {info.follower_count}\n"  
            f"➡️ المتابعين: {info.following_count}\n"  
            f"📸 المنشورات: {info.media_count}\n"  
        )  

        markup = types.InlineKeyboardMarkup()  
        markup.add(types.InlineKeyboardButton("📸 ستوري", callback_data=f"story:{uid}"),
                   types.InlineKeyboardButton("🎞️ هايلايت", callback_data=f"highlights:{uid}"))  
        markup.add(types.InlineKeyboardButton("🖼️ تحميل صورة البروفايل (HD)", callback_data=f"pfp:{uid}")) 
        markup.add(types.InlineKeyboardButton("🖼️ عرض آخر المنشورات", callback_data=f"feed:{uid}")) 

        pic = getattr(info, "profile_pic_url_hd", None) or getattr(info, "profile_pic_url", None)  
        if pic:  
            bot.send_photo(chat_id, pic, caption=caption, reply_markup=markup)  
        else:  
            bot.send_message(chat_id, caption, reply_markup=markup)  

    except Exception as e:  
        traceback.print_exc()  
        bot.send_message(chat_id, f"⚠️ خطأ: {e}")

# ---------- دالة مساعدة لاستخراج أفضل رابط ----------
def get_best_url(item, is_video):
    url = None
    if is_video:
        url = getattr(item, 'video_url', None)
    else:
        # 1. أعلى دقة (image_versions2)
        if getattr(item, 'image_versions2', None) and item.image_versions2:
            url = item.image_versions2[0].url
        
        # 2. الخطة البديلة: display_url (دقة جيدة)
        if not url:
            url = getattr(item, 'display_url', None)
            
        # 3. الخطة البديلة الأخيرة: thumbnail_url (دقة أقل لكن مضمون)
        if not url:
            url = getattr(item, 'thumbnail_url', None)
    return url

# ---------- handlers للأزرار (الستوري، الهايلايت، الفيد، ولوحة التحكم) ----------
@bot.callback_query_handler(func=lambda c: True)
def on_callback(c):
    global BOT_ACTIVE, awaiting_broadcast
    data = c.data or ""
    chat_id = c.message.chat.id
    message_id = c.message.message_id

    # 🚫 فحص حالة البوت لغير المطورين
    if not BOT_ACTIVE and chat_id != OWNER_ID:
        bot.answer_callback_query(c.id, "🚫 البوت مقفول حالياً.")
        return

    # ------------------ لوحة تحكم المطور (dev:) ------------------
    if data.startswith("dev:"):
        if chat_id != OWNER_ID:
            bot.answer_callback_query(c.id, "🚫 مش مسموحلك")
            return

        action_data = data.split(":", 1)[1]

        if action_data == "broadcast":
            awaiting_broadcast = True
            bot.answer_callback_query(c.id, "✍️ اكتب الرسالة الآن في الشات.", show_alert=True)
            bot.send_message(chat_id, "✍️ اكتب الرسالة اللي عاوز تبعتها لكل المستخدمين:")
        
        elif action_data == "users":
            users_count = 0
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, "r") as f:
                    users_count = len(f.read().splitlines())
            bot.answer_callback_query(c.id, f"👥 عدد المستخدمين: {users_count}", show_alert=True)

        elif action_data == "myid":
            bot.answer_callback_query(c.id, f"🆔 الـ ID بتاعك: {chat_id}", show_alert=True)

        elif action_data == "toggle":
            BOT_ACTIVE = not BOT_ACTIVE
            
            users_count = 0
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, "r") as f:
                    users_count = len(f.read().splitlines())
                    
            new_caption, new_kb = get_panel_content(BOT_ACTIVE, users_count)
            status = "✅ شغال" if BOT_ACTIVE else "❌ مقفول"
            
            bot.edit_message_text(
                new_caption,
                chat_id,
                message_id,
                reply_markup=new_kb
            )
            
            bot.answer_callback_query(c.id, f"🚦 تم تغيير حالة البوت إلى: {status}", show_alert=True)
            return

        elif action_data == "restart":
            bot.answer_callback_query(c.id, "♻️ جاري إعادة تشغيل البوت...", show_alert=True)
            bot.send_message(chat_id, "♻️ جاري إعادة تشغيل البوت...")
            os.execv(sys.executable, ['python'] + sys.argv)
            return

        return 

    # ------------------ تحميل صورة البروفايل (PFP:) ------------------
    elif data.startswith("pfp:"):
        uid = data.split(":", 1)[1]
        try:
            bot.answer_callback_query(c.id, "⏳ جاري جلب صورة البروفايل...")
            info = cl.user_info(uid)
            
            # محاولة جلب الرابط بأعلى جودة
            url = getattr(info, "profile_pic_url_hd", None) or getattr(info, "profile_pic_url", None)
            
            if url:
                download_and_send(chat_id, url, is_video=False)
                bot.send_message(chat_id, "✅ تم إرسال صورة البروفايل بدقة عالية.")
            else:
                bot.send_message(chat_id, "⚠️ تعذر العثور على رابط صورة البروفايل.")
                
        except Exception as e:
            traceback.print_exc()
            bot.send_message(chat_id, f"⚠️ خطأ في جلب صورة البروفايل: {e}")
        return

    # ------------------ الـ Callbacks الأخرى ------------------
    bot.answer_callback_query(c.id, "⏳ جاري التنفيذ...") 
    
    if data.startswith("story:"):  
        uid = data.split(":", 1)[1]  
        try:  
            stories = cl.user_stories(uid)  
            if not stories:  
                bot.send_message(chat_id, "🚫 لا توجد ستوريات حالياً.")  
                return  
            
            for s in stories[:5]:  
                video_url = getattr(s, "video_url", None)  
                photo_url = getattr(s, "display_url", None) or getattr(s, "thumbnail_url", None)  
                url = video_url or photo_url  
                if url:
                    download_and_send(chat_id, url, is_video=bool(video_url))  
                else:
                    bot.send_message(chat_id, "⚠️ تعذّر إرسال هذه الستوري")
                    
                time.sleep(0.6)  
            bot.send_message(chat_id, "✅ انتهت الستوريات.")  
        except Exception as e:  
            traceback.print_exc()  
            bot.send_message(chat_id, f"⚠️ خطأ في جلب الستوري: {e}")  

    elif data.startswith("highlights:"):  
        uid = data.split(":", 1)[1]  
        try:  
            highlights = cl.user_highlights(uid)  
            if not highlights:  
                bot.send_message(chat_id, "🚫 لا توجد هايلايتس.")  
                return  
            kb = types.InlineKeyboardMarkup()  
            for h in highlights:  
                title = h.title or "بدون اسم"  
                hl_pk = getattr(h, "pk", None) or getattr(h, "id", None)  
                kb.add(types.InlineKeyboardButton(f"⭐ {title}", callback_data=f"highlight:{hl_pk}"))  
            bot.send_message(chat_id, "📌 اختار هايلايت:", reply_markup=kb)  
        except Exception as e:  
            traceback.print_exc()  
            bot.send_message(chat_id, f"⚠️ خطأ في جلب الهايلايت: {e}")  

    elif data.startswith("highlight:"):  
        hl_id = data.split(":", 1)[1]  
        try:  
            hl_pk = int(hl_id) 
            highlight = cl.highlight_info(hl_pk)  
            items = getattr(highlight, "items", None) or getattr(highlight, "stories", None) or getattr(highlight, "media_ids", None)  
            
            if not items:  
                bot.send_message(chat_id, "🚫 هذا الهايلايت فاضي أو لا يمكن الوصول لمحتواه.")  
                return  

            for it in items[:5]: 
                video_url = getattr(it, "video_url", None)  
                photo_url = getattr(it, "display_url", None) or getattr(it, "thumbnail_url", None)  
                url = video_url or photo_url 
                
                if url:
                    download_and_send(chat_id, url, is_video=bool(video_url))
                else:
                    bot.send_message(chat_id, "⚠️ لم أتمكن من إرسال هذا العنصر.")
                    
                time.sleep(0.6)  

            bot.send_message(chat_id, "✅ انتهيت من إرسال محتويات الهايلايت.")  
        except Exception as e:  
            traceback.print_exc()  
            bot.send_message(chat_id, f"⚠️ خطأ في جلب محتوى الهايلايت: {e}")

    # ------------------ منشورات (FEED:) عرض القائمة ------------------
    elif data.startswith("feed:"):
        uid = data.split(":", 1)[1]
        user_id_int = int(uid)
        
        try:
            # بنجيب آخر 6 منشورات عشان نطلع عددهم وأرقامهم للمستخدم
            media_list = cl.user_medias(user_id_int, amount=6)

            if not media_list:
                bot.send_message(chat_id, "❌ مفيش منشورات في الحساب ده.")
                return
            
            caption = f"✅ تم إيجاد {len(media_list)} منشور.\n\n"
            caption += "📌 **اختر رقم المنشور اللي محتاجه:**"
            
            kb = types.InlineKeyboardMarkup(row_width=3)
            buttons = []
            
            for i in range(len(media_list)):
                post_number = i + 1 
                media_pk = media_list[i].pk
                media_type = media_list[i].media_type
                
                # تحديد الرمز التعبيري بناءً على نوع المنشور
                if media_type == 1:
                    emoji = "📸" # صورة
                elif media_type == 2:
                    emoji = "🎥" # فيديو
                elif media_type == 8:
                    emoji = "🖼️" # ألبوم (Carousel)
                else:
                    emoji = "✨" # نوع آخر
                
                button_text = f"{post_number} {emoji}"
                
                buttons.append(types.InlineKeyboardButton(button_text, callback_data=f"post:{media_pk}"))
                
            kb.add(*buttons)
            
            bot.send_message(chat_id, caption, reply_markup=kb)
            
        except Exception as e:
            traceback.print_exc()
            bot.send_message(chat_id, f"⚠️ خطأ في جلب المنشورات: {e}")

    # ------------------ منشور مُختار بالرقم (POST:) ------------------
    elif data.startswith("post:"):
        media_pk = data.split(":", 1)[1]
        
        try:
            bot.send_message(chat_id, "⏳ جاري تحميل المنشور المُختار...")
            
            media = cl.media_info(media_pk) 
            
            # 💡 حالة المنشور الألبوم (Carousel)
            if media.media_type == 8:
                bot.send_message(chat_id, f"🖼️ تم إيجاد ألبوم/منشور متعدد به {len(media.resources)} عنصر. جاري الإرسال...")
                
                # إرسال كل العناصر داخل الألبوم
                for resource in media.resources:
                    is_video = resource.media_type == 2
                    url = get_best_url(resource, is_video)
                    
                    if url:
                        download_and_send(chat_id, url, is_video=is_video)
                        time.sleep(0.6)
                    else:
                        bot.send_message(chat_id, "⚠️ تعذر العثور على رابط لأحد عناصر الألبوم.")
                
                bot.send_message(chat_id, "✅ انتهيت من إرسال الألبوم بنجاح.")
                return 

            # 💡 حالة المنشور الفردي (صورة أو فيديو)
            is_video = media.media_type == 2
            
            caption = media.caption_text[:100] + "..." if media.caption_text and len(media.caption_text) > 100 else media.caption_text or "—"
            
            url = get_best_url(media, is_video)


            if url:
                download_and_send(chat_id, url, is_video=is_video)
                bot.send_message(chat_id, "✅ تم إرسال المنشور بنجاح.")
            else:
                bot.send_message(chat_id, "⚠️ تعذر العثور على رابط المنشور للتحميل.")
                
        except Exception as e:
            traceback.print_exc()
            bot.send_message(chat_id, f"⚠️ خطأ في جلب المنشور المُختار: {e}")


# ---------- /panel (لوحة التحكم للمطور) ----------
@bot.message_handler(commands=['panel'])
def cmd_panel(m):
    if m.chat.id != OWNER_ID:
        bot.reply_to(m, "🚫 هذا الأمر خاص بالمطور فقط.")
        return

    users_count = 0
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users_count = len(f.read().splitlines())

    caption, kb = get_panel_content(BOT_ACTIVE, users_count)

    bot.send_message(m.chat.id, caption, reply_markup=kb)

# ---------- شغّل البوت ----------
if __name__ == "__main__":
    print("Bot started — using session file:", SESSION_FILE)
    bot.remove_webhook() 
    bot.infinity_polling()
