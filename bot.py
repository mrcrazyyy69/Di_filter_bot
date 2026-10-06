import os
import threading
import requests
from flask import Flask

TOKEN=os.environ["BOT_TOKEN"]
CHAT_ID=int(os.environ["CHAT_ID"])
BASE=f"https://api.telegram.org/bot{TOKEN}"
warnings={}

BAD_WORDS={"ASU", "Asu", "@su", "4su",
          "anjing", "4nj!n9", "@nj!ng", "@nj!n9", "4njing", "@njing",
                        "meki", "m3m3k", "mem3k", "mmk", "memek",
                                          "babi", "b@b!", "b4bi", "b@bi",
                  "jancuk", "Jancuk", "j@ncuk", "j4ncuk", "cuk", "cok",
                                    "Cok", "Cuk", "monyet",
              "Spin", "spin", "wd", "withdraw", "zeus", "kemenangan", "Deposit",
              "Depo", "depo", "slot", "$lot", "vcs", "dana", "ovo",
  "shopepay", "shopeepay", "pembayaran via", "gopay", "payment", "pulsa",
              "Qris", "paypal", "saldo", "transfer", "tf" "bank", "m-banking",
        "Kontol", "kontol", "K0ntol", "k0nt0l", "squird", "pipis", "matamu!",
        "miskin", "kere", "kerek", "tai", "Tai", "eek", "Tempek", "tempek",
      "kissing", "grab", "Grab", "pepek", "ppk", "sange", "sangek", "crot",
                "Payudara", "Tobrut", "tobrut", "Sex", "Money", "money",
                              "binatang", "botak", "Botak"
           }}

app=Flask(name)

@app.route("/")
def home():
    return "DI FILTER BOT AKTIF"

def api(method,data):
    return requests.post(f"{BASE}/{method}",data=data,timeout=30).json()

def is_admin(uid):
    r=api("getChatMember",{"chat_id":CHAT_ID,"user_id":uid})
    return r.get("ok") and r["result"]["status"] in ["creator","administrator"]

def process(m):
    if m.get("chat",{}).get("id")!=CHAT_ID:return
    u=m.get("from",{})
    if u.get("is_bot"):return
    uid=u.get("id")
    if is_admin(uid):return
    text=m.get("text","").lower()
    if not any(w in text for w in BAD_WORDS):return
    api("deleteMessage",{"chat_id":CHAT_ID,"message_id":m["message_id"]})
    key=(CHAT_ID,uid)
    warnings[key]=warnings.get(key,0)+1
    name=u.get("first_name","Anggota")
    if warnings[key]==1:
        api("sendMessage",{"chat_id":CHAT_ID,"text":f"⚠️ {name}, peringatan 1. Pesan kamu dihapus."})
    else:
        api("sendMessage",{"chat_id":CHAT_ID,"text":f"🚫 {name} dikeluarkan karena mengulangi pelanggaran."})
        api("banChatMember",{"chat_id":CHAT_ID,"user_id":uid})

def bot_loop():
    offset=0
    while True:
        try:
            r=requests.get(f"{BASE}/getUpdates",params={"offset":offset,"timeout":20},timeout=30).json()
            for x in r.get("result",[]):
                offset=x["update_id"]+1
                if "message" in x:
                    process(x["message"])
        except Exception:
            pass

threading.Thread(target=bot_loop,daemon=True).start()

app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
