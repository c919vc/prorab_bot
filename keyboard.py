from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_calendar import SimpleCalendar


# ================================================================
#                        INLINE MENUS
# ================================================================
def user_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Xarajat qo‘shish", callback_data="add_expense")],
        [InlineKeyboardButton(text="💳 Kartaga qo‘shish", callback_data="add_card")],
        [InlineKeyboardButton(text="💸 Qarz qo‘shish", callback_data="add_debt")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="today_stats")],
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="search")],
    ])


def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Xarajat qo‘shish", callback_data="add_expense")],
        [InlineKeyboardButton(text="💳 Kartaga qo‘shish", callback_data="add_card")],
        [InlineKeyboardButton(text="💸 Qarz qo‘shish", callback_data="add_debt")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="today_stats")],
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="search")],
    ])



# ================================================================
#                       EXPENSE CATEGORIES
# ================================================================
def expense_categories():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍽 Ovqat", callback_data="cat_ovqat")],
        [InlineKeyboardButton(text="📦 Firma", callback_data="cat_firma")],
        [InlineKeyboardButton(text="Boshqalar", callback_data="cat_other")],
        [InlineKeyboardButton(text="◀ Orqaga", callback_data="back_menu")],
    ])



# ================================================================
#                        CONFIRM BUTTONS
# ================================================================
def confirm_cancel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✔ Tasdiqlash", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm_no"),
        ]
    ])



# ================================================================
#                           BACK
# ================================================================
def back_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="◀ Orqaga", callback_data="back_menu")]]
    )

