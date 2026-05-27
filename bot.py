import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from openpyxl import Workbook

TOKEN = "8615157630:AAHLW1-g_Hs1CRwoxzR0L4p7p6KDjEQbjmQ"
DB = "finance.db"


def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        amount INTEGER,
        note TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_transaction(user_id, ttype, amount, note):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO transactions
    (user_id, type, amount, note, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        ttype,
        amount,
        note,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_stats(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    month = datetime.now().strftime("%Y-%m")

    cur.execute("""
    SELECT type, SUM(amount)
    FROM transactions
    WHERE user_id=? AND created_at LIKE ?
    GROUP BY type
    """, (user_id, f"{month}%"))

    rows = cur.fetchall()

    conn.close()

    thu = 0
    chi = 0

    for row in rows:
        if row[0] == "thu":
            thu = row[1] or 0

        if row[0] == "chi":
            chi = row[1] or 0

    return thu, chi


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 BOT QUẢN LÝ THU CHI\n\n"
        "/thu 500000 lương\n"
        "/chi 100000 ăn sáng\n"
        "/thang\n"
        "/sodu\n"
        "/xuatexcel"
    )

    await update.message.reply_text(text)


async def thu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(context.args[0])
        note = " ".join(context.args[1:])

        add_transaction(
            update.effective_user.id,
            "thu",
            amount,
            note
        )

        await update.message.reply_text(
            f"✅ Đã thêm thu {amount:,}đ"
        )

    except:
        await update.message.reply_text(
            "Ví dụ: /thu 500000 lương"
        )


async def chi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(context.args[0])
        note = " ".join(context.args[1:])

        add_transaction(
            update.effective_user.id,
            "chi",
            amount,
            note
        )

        await update.message.reply_text(
            f"💸 Đã thêm chi {amount:,}đ"
        )

    except:
        await update.message.reply_text(
            "Ví dụ: /chi 100000 ăn sáng"
        )


async def thang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thu, chi = get_stats(update.effective_user.id)

    sodu = thu - chi

    text = (
        f"📊 THỐNG KÊ THÁNG\n\n"
        f"💰 Thu: {thu:,}đ\n"
        f"💸 Chi: {chi:,}đ\n"
        f"🏦 Số dư: {sodu:,}đ"
    )

    await update.message.reply_text(text)


async def sodu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thu, chi = get_stats(update.effective_user.id)

    sodu_value = thu - chi

    await update.message.reply_text(
        f"🏦 Số dư: {sodu_value:,}đ"
    )


async def xuatexcel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT type, amount, note, created_at
    FROM transactions
    WHERE user_id=?
    """, (update.effective_user.id,))

    rows = cur.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active

    ws.append([
        "Loai",
        "So tien",
        "Ghi chu",
        "Ngay"
    ])

    for row in rows:
        ws.append(row)

    filename = "thuchi.xlsx"

    wb.save(filename)

    with open(filename, "rb") as file:
        await update.message.reply_document(file)


def main():
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("thu", thu))
    app.add_handler(CommandHandler("chi", chi))
    app.add_handler(CommandHandler("thang", thang))
    app.add_handler(CommandHandler("sodu", sodu))
    app.add_handler(CommandHandler("xuatexcel", xuatexcel))

    print("Bot dang chay...")

    app.run_polling()


if __name__ == "__main__":
    main()
