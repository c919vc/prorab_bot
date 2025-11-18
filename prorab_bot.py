import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from utils import cleanup_old_data   # ⬅️ TO‘G‘RI JOYI
from db import *
from keyboard import *
from utils import format_summa

logging.basicConfig(level=logging.INFO)

TOKEN = "8415232645:AAH4HhvSh5jk6a2APm6JX-dQyGaIcFZ2iK8"
ADMIN_USERNAME = "s703sc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔥 BOT ISHGA TUSHGANDА ESKI MA’LUMOTLARNI TOZALAYMIZ
cleanup_old_data()


# ================================================================
#   REPLY KEYBOARD (Asosiy menyu)
# ================================================================
def main_reply():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 Xarajat qo‘shish")],
            [KeyboardButton(text="💳 Kartaga qo‘shish")],
            [KeyboardButton(text="💸 Qarz qo‘shish")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="🔍 Qidirish")],
        ],
        resize_keyboard=True
    )


# ========================= STATES ================================
class ExpenseForm(StatesGroup):
    category = State()
    amount = State()
    note = State()
    confirm = State()


class CardForm(StatesGroup):
    amount = State()
    item = State()
    photo = State()
    confirm = State()


class DebtForm(StatesGroup):
    name = State()
    phone = State()
    amount = State()
    item = State()
    deadline = State()
    confirm = State()


class DebtEditForm(StatesGroup):
    name = State()
    phone = State()
    amount = State()
    item = State()
    deadline = State()
    confirm = State()



# ================================================================
#                              START
# ================================================================
@dp.message(CommandStart())
async def start_cmd(msg: Message, state: FSMContext):

    add_user(
        uid=msg.from_user.id,
        name=msg.from_user.full_name,
        username=msg.from_user.username or ""
    )

    welcome = """
🏗 *PRORAB WORKERS BOT*

📌 Xarajatlar yozish
💳 Kartaga tushganlar
💸 Qarzlar
📊 Statistika
🔍 Qidiruv

Xush kelibsiz!
"""
    await msg.answer(welcome, reply_markup=main_reply(), parse_mode="Markdown")

    if msg.from_user.username == ADMIN_USERNAME:
        await msg.answer("🔐 Admin panel", reply_markup=admin_menu())



# ================================================================
#                REPLY CONTROL (Bosilganda ishga tushadi)
# ================================================================
@dp.message(F.text == "📌 Xarajat qo‘shish")
async def reply_expense(msg, state):
    await add_expense_start(msg, state)


@dp.message(F.text == "💳 Kartaga qo‘shish")
async def reply_card(msg, state):
    await add_card_start(msg, state)


@dp.message(F.text == "💸 Qarz qo‘shish")
async def reply_debt(msg, state):
    await start_debt(msg, state)


@dp.message(F.text == "📊 Statistika")
async def reply_stats(msg):
    await today_stats_msg(msg)


@dp.message(F.text == "🔍 Qidirish")
async def reply_search(msg):
    await search_all_debts(msg)



# ================================================================
#                       X A R A J A T L A R
# ================================================================
async def add_expense_start(source, state):
    await state.set_state(ExpenseForm.category)
    await source.answer("🗂 Kategoriya tanlang:", reply_markup=expense_categories())


@dp.callback_query(F.data.startswith("cat_"))
async def choose_cat(q, state):
    mapping = {
        "cat_ovqat": "Ovqat",
        "cat_firma": "Firma",
        "cat_other": "Boshqalar"
    }
    await state.update_data(category=mapping[q.data])
    await state.set_state(ExpenseForm.amount)
    await q.message.edit_text("💰 Summani kiriting (masalan: 30 000):", reply_markup=back_button())


@dp.message(ExpenseForm.amount)
async def exp_amount(msg, state):
    if not msg.text.replace(" ", "").isdigit():
        return await msg.answer("❌ Raqamda kiriting!")

    await state.update_data(amount=int(msg.text.replace(" ", "")))
    await state.set_state(ExpenseForm.note)
    await msg.answer("📝 Izoh (0 bo‘lsa tashlanadi):")


@dp.message(ExpenseForm.note)
async def exp_note(msg, state):
    await state.update_data(note="" if msg.text == "0" else msg.text)
    d = await state.get_data()

    text = f"""
📌 *Xarajat:*

Kategoriya: {d['category']}
Summa: {format_summa(d['amount'])}
Izoh: {d['note']}
"""
    await state.set_state(ExpenseForm.confirm)
    await msg.answer(text, reply_markup=confirm_cancel(), parse_mode="Markdown")


@dp.callback_query(ExpenseForm.confirm)
async def exp_done(q, state):
    if q.data == "confirm_yes":
        d = await state.get_data()
        save_expense(d["category"], d["amount"], d["note"])
        await q.message.edit_text("✔ Saqlandi!", reply_markup=user_menu())
    else:
        await q.message.edit_text("❌ Bekor qilindi.", reply_markup=user_menu())

    await state.clear()



# ================================================================
#                         K A R T A G A
# ================================================================
async def add_card_start(source, state):
    await state.set_state(CardForm.amount)
    await source.answer("💳 Summani kiriting:", reply_markup=back_button())


@dp.message(CardForm.amount)
async def card_amount(msg, state):
    if not msg.text.replace(" ", "").isdigit():
        return await msg.answer("❌ Raqam bo‘lsin!")

    await state.update_data(amount=int(msg.text.replace(" ", "")))
    await state.set_state(CardForm.item)
    await msg.answer("📦 Tovar nomi?")


@dp.message(CardForm.item)
async def card_item(msg, state):
    await state.update_data(item=msg.text)
    await state.set_state(CardForm.photo)
    await msg.answer("📸 Rasm yuboring yoki 0 deb yozing.")


@dp.message(CardForm.photo)
async def card_photo(msg, state):
    photo = msg.photo[-1].file_id if msg.photo else None
    await state.update_data(photo=photo)

    d = await state.get_data()

    text = f"""
💳 *Karta:*

Summa: {format_summa(d['amount'])}
Tovar: {d['item']}
"""

    await state.set_state(CardForm.confirm)
    await msg.answer(text, reply_markup=confirm_cancel(), parse_mode="Markdown")


@dp.callback_query(CardForm.confirm)
async def card_done(q, state):
    if q.data == "confirm_yes":
        d = await state.get_data()
        save_card(d["amount"], d["item"], d["photo"])
        await q.message.edit_text("✔ Saqlandi!", reply_markup=user_menu())
    else:
        await q.message.edit_text("❌ Bekor qilindi.", reply_markup=user_menu())

    await state.clear()



# ================================================================
#                         Q A R Z L A R
# ================================================================
async def start_debt(source, state):
    await state.set_state(DebtForm.name)
    await source.answer("👤 Ism?")


@dp.message(DebtForm.name)
async def debt_name(msg, state):
    await state.update_data(name=msg.text)
    await state.set_state(DebtForm.phone)
    await msg.answer("📞 Telefon? (9 raqam)")


@dp.message(DebtForm.phone)
async def debt_phone(msg, state):
    if not msg.text.isdigit():
        return await msg.answer("❌ Raqam!")

    await state.update_data(phone=msg.text)
    await state.set_state(DebtForm.amount)
    await msg.answer("💰 Summa?")


@dp.message(DebtForm.amount)
async def debt_amt(msg, state):
    if not msg.text.replace(" ", "").isdigit():
        return await msg.answer("❌ Raqam!")

    await state.update_data(amount=int(msg.text.replace(" ", "")))
    await state.set_state(DebtForm.item)
    await msg.answer("📦 Tovar?")


@dp.message(DebtForm.item)
async def debt_item(msg, state):
    await state.update_data(item=msg.text)
    await state.set_state(DebtForm.deadline)
    await msg.answer("📅 Sana:", reply_markup=SimpleCalendar().start_calendar())


@dp.callback_query(SimpleCalendarCallback.filter())
async def debt_deadline(q, state):
    selected, date = await SimpleCalendar().process_selection(q)

    if not selected:
        return

    await state.update_data(deadline=str(date))

    d = await state.get_data()

    text = f"""
📌 *Qarz:*

Ism: {d['name']}
Raqam: {d['phone']}
Summa: {format_summa(d['amount'])}
Tovar: {d['item']}
Muddat: {d['deadline']}
"""

    await state.set_state(DebtForm.confirm)
    await q.message.edit_text(text, reply_markup=confirm_cancel(), parse_mode="Markdown")


@dp.callback_query(DebtForm.confirm)
async def debt_done(q, state):
    if q.data == "confirm_yes":
        d = await state.get_data()
        save_debt(d['name'], d['phone'], d['amount'], d['item'], d['deadline'])
        await q.message.edit_text("✔ Saqlandi!", reply_markup=user_menu())

    else:
        await q.message.edit_text("❌ Bekor qilindi.", reply_markup=user_menu())

    await state.clear()



# ================================================================
#                    QIDIRUV — BARCHA QARZLAR
# ================================================================
async def search_all_debts(source):
    debts = get_debts()

    if not debts:
        return await source.answer("📭 Hozircha qarzdor yo‘q.")

    debts = debts[::-1]

    keyboard = []

    for d in debts:
        keyboard.append([
            InlineKeyboardButton(
                text=f"👤 {d['name']} — 💰 {format_summa(d['amount'])}",
                callback_data=f"debt_{d['id']}"
            )
        ])

    await source.answer(
        "🔍 Qarzdorlar:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )



# ================================================================
#                QARZDOR KARTOCHKASI + O'CHIRISH + TAHRIR
# ================================================================
@dp.callback_query(F.data.startswith("debt_"))
async def debt_card(q):
    did = int(q.data.split("_")[1])
    d = get_debt_by_id(did)

    if not d:
        return await q.message.edit_text("❌ Qarzdor topilmadi.")

    text = f"""
📌 *QARZDOR:* {d['name']}

📞 +998 {d['phone']}
📦 {d['item']}
💰 {format_summa(d['amount'])}
📅 {d['deadline']}
"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✔ To‘landi", callback_data=f"paid_{did}")],
        [InlineKeyboardButton(text="✏ Tahrirlash", callback_data=f"edit_{did}")],
        [InlineKeyboardButton(text="🗑 O‘chirish", callback_data=f"delete_{did}")]
    ])

    await q.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")



# ------------------ TO‘LANDI = O‘CHIRISH ------------------
@dp.callback_query(F.data.startswith("paid_"))
async def debt_paid(q):
    did = int(q.data.split("_")[1])

    delete_debt(did)

    await q.message.edit_text("✔ To‘langan sifatida o‘chirildi.", reply_markup=user_menu())



# ------------------------ O‘CHIRISH ------------------------
@dp.callback_query(F.data.startswith("delete_"))
async def debt_delete(q):
    did = int(q.data.split("_")[1])

    delete_debt(did)

    await q.message.edit_text("🗑 Muvaffaqiyatli o‘chirildi.", reply_markup=user_menu())



# ================================================================
#                            TAHRIRLASH
# ================================================================
@dp.callback_query(F.data.startswith("edit_"))
async def edit_start(q, state):
    did = int(q.data.split("_")[1])
    await state.update_data(edit_id=did)

    await state.set_state(DebtEditForm.name)
    await q.message.edit_text("✏ Yangi ism?")


@dp.message(DebtEditForm.name)
async def edit_name(msg, state):
    await state.update_data(name=msg.text)
    await state.set_state(DebtEditForm.phone)
    await msg.answer("📞 Yangi telefon?")


@dp.message(DebtEditForm.phone)
async def edit_phone(msg, state):
    await state.update_data(phone=msg.text)
    await state.set_state(DebtEditForm.amount)
    await msg.answer("💰 Yangi summa?")


@dp.message(DebtEditForm.amount)
async def edit_amount(msg, state):
    await state.update_data(amount=int(msg.text.replace(" ", "")))
    await state.set_state(DebtEditForm.item)
    await msg.answer("📦 Yangi tovar?")


@dp.message(DebtEditForm.item)
async def edit_item(msg, state):
    await state.update_data(item=msg.text)
    await state.set_state(DebtEditForm.deadline)
    await msg.answer("📅 Yangi sana:", reply_markup=SimpleCalendar().start_calendar())


@dp.callback_query(SimpleCalendarCallback.filter())
async def edit_deadline(q, state):
    selected, date = await SimpleCalendar().process_selection(q)
    if not selected:
        return

    await state.update_data(deadline=str(date))

    d = await state.get_data()

    text = f"""
✏ *Tahrirlash yakuniy:* 

Ism: {d['name']}
Raqam: {d['phone']}
Summa: {format_summa(d['amount'])}
Tovar: {d['item']}
Muddat: {d['deadline']}
"""
    await state.set_state(DebtEditForm.confirm)
    await q.message.edit_text(text, reply_markup=confirm_cancel(), parse_mode="Markdown")


@dp.callback_query(DebtEditForm.confirm)
async def edit_save(q, state):
    d = await state.get_data()
    did = d["edit_id"]

    save_debt_edit(did, d["name"], d["phone"], d["amount"], d["item"], d["deadline"])

    await state.clear()
    await q.message.edit_text("✔ Muvaffaqiyatli yangilandi.", reply_markup=user_menu())



# ================================================================
#                           RUN BOT
# ================================================================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
