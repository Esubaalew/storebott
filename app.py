from flask import Flask, request, Response
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, InlineQueryHandler, MessageHandler,
    filters, ConversationHandler
)
from telegram.constants import ChatAction
import os, asyncio, logging, re
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv

from api import (
    get_categories, get_subcategories, get_brands,
    get_models, get_products, get_product_details,
    check_stock_availability, search_items, fetch_item_details,
    create_request, create_message,
    get_all_requests, get_request_details, get_all_messages
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

# ── Flask ─────────────────────────────
flask_app = Flask(__name__)

# ── Bot ───────────────────────────────
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = "https://storebot.betegbarpms.com/webhook"

ptb_app = ApplicationBuilder().token(TOKEN).build()

ADMINS = [1648265210]

REQUEST, PHONE, ADDRESS = range(3)
LIVE_REQUEST, LIVE_PHONE, LIVE_ADDRESS, LIVE_ADDITIONAL_TEXT = range(3, 7)
RESPOND_TO_REQUEST, RESPONSE_MESSAGE = range(2)


# ── SAFE TELEGRAM CALL WRAPPER ────────
async def safe_send_action(chat):
    try:
        await chat.send_action(ChatAction.TYPING)
    except Exception as e:
        logging.warning(f"send_action failed: {e}")


# ── Async runner ───────────────────────
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# ── START ──────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_send_action(update.message.chat)

    categories = get_categories()
    if not categories:
        await update.message.reply_text("No categories available.")
        return

    keyboard = [
        [InlineKeyboardButton(c["name"], callback_data=f"category_{c['id']}")]
        for c in categories
    ]

    await update.message.reply_text(
        "Choose category:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ── BUTTON HANDLER ─────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("category_"):
        cid = data.split("_")[1]
        subs = get_subcategories(cid)

        keyboard = [
            [InlineKeyboardButton(s["name"], callback_data=f"subcategory_{s['id']}")]
            for s in subs
        ]
        await query.edit_message_text("Choose subcategory:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("subcategory_"):
        sid = data.split("_")[1]
        brands = get_brands(sid)

        keyboard = [
            [InlineKeyboardButton(b["name"], callback_data=f"brand_{b['id']}")]
            for b in brands
        ]
        await query.edit_message_text("Choose brand:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("brand_"):
        bid = data.split("_")[1]
        models = get_models(bid)

        keyboard = [
            [InlineKeyboardButton(m["name"], callback_data=f"model_{m['id']}")]
            for m in models
        ]
        await query.edit_message_text("Choose model:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("model_"):
        mid = data.split("_")[1]
        items = get_products(mid)

        keyboard = [
            [InlineKeyboardButton(i["name"], callback_data=f"item_{i['id']}")]
            for i in items
        ]
        await query.edit_message_text("Choose item:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("item_"):
        iid = data.split("_")[1]

        product = get_product_details(iid)
        stock = check_stock_availability(iid)

        msg = (
            f"📱 {product['name']}\n"
            f"Brand: {product['brand']}\n"
            f"Model: {product['model']}\n"
            f"In stock: {stock.get('is_available', False) if stock else False}"
        )

        await query.edit_message_text(msg)


# ── LIVE REQUEST (simplified) ──────────
async def live_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your name:")
    return LIVE_REQUEST


# ── MESSAGE HANDLER ────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in ADMINS:
        await update.message.reply_text("Admin mode.")
        return

    await update.message.reply_text("Use /start or /live_agent")


# ── FLASK WEBHOOK ───────────────────────
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, ptb_app.bot)
    run_async(ptb_app.process_update(update))
    return Response("ok", status=200)


@flask_app.route("/")
def index():
    return "Bot running", 200


# ── INIT BOT ───────────────────────────
async def init():
    await ptb_app.initialize()
    await ptb_app.start()
    await ptb_app.bot.set_webhook(WEBHOOK_URL)


run_async(init())

application = flask_app
