from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, InlineQueryHandler, MessageHandler, filters, ConversationHandler
from api import get_categories, get_subcategories, get_brands, get_models, get_products, get_product_details, check_stock_availability, search_items, fetch_item_details
from uuid import uuid4
from dotenv import load_dotenv
from telegram.constants import ChatAction
import os
import re
from datetime import datetime

# Conversation states
REQUEST, PHONE, ADDRESS = range(3)

# Command handler to show categories
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command to show categories."""
    await update.message.chat.send_action(ChatAction.TYPING)
    categories = get_categories()
    if categories:
        keyboard = [
            [InlineKeyboardButton(cat['name'], callback_data=f"category_{cat['id']}")] for cat in categories
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please choose a category:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No categories available.")

# Button handler for category, subcategory, brand, model navigation
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button clicks to build hierarchical inline keyboards."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith('category_'):
        category_id = data.split('_')[1]
        subcategories = get_subcategories(category_id)
        if subcategories:
            keyboard = [
                [InlineKeyboardButton(sub['name'], callback_data=f"subcategory_{sub['id']}")] for sub in subcategories
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Please choose a subcategory:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("No subcategories available.")

    elif data.startswith('subcategory_'):
        subcategory_id = data.split('_')[1]
        brands = get_brands(subcategory_id)
        if brands:
            keyboard = [
                [InlineKeyboardButton(brand['name'], callback_data=f"brand_{brand['id']}")] for brand in brands
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Please choose a brand:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("No brands available.")

    elif data.startswith('brand_'):
        brand_id = data.split('_')[1]
        models = get_models(brand_id)
        if models:
            keyboard = [
                [InlineKeyboardButton(model['name'], callback_data=f"model_{model['id']}")] for model in models
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Please choose a model:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("No models available.")

    elif data.startswith('model_'):
        model_id = data.split('_')[1]
        items = get_products(model_id)
        if items:
            keyboard = [
                [InlineKeyboardButton(item['name'], callback_data=f"item_{item['id']}")] for item in items
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Please choose an item:", reply_markup=reply_markup)
        else:
            await query.edit_message_text("No items available.")

    elif data.startswith('item_'):
        item_id = data.split('_')[1]
        product_details = get_product_details(item_id)
        if product_details:
            # Check stock availability and include it in the product details
            stock_details = check_stock_availability(item_id)
            is_available = "Yes" if stock_details and stock_details['is_available'] else "No"
            formatted_details = re.escape(
                f"📱 *{product_details['name']}*\n\n"
                f"*Brand:* {product_details['brand']}\n"
                f"*Model:* {product_details['model']}\n"
                f"*Subcategory:* {product_details['subcategory']}\n"
                f"*Stock Available:* {is_available}\n"
            )
            # Add a button for making a request
            keyboard = [
                [InlineKeyboardButton("Make Request", callback_data=f"make_request_{item_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(formatted_details, reply_markup=reply_markup, parse_mode='MarkdownV2')
        else:
            await query.edit_message_text("No product details available.")

    elif data.startswith('make_request_'):
        # Save the item_id to context for further use
        context.user_data['item_id'] = data.split('_')[2]
        await query.edit_message_text("Please provide your name:")
        return REQUEST

# Conversation handler for request flow
async def request_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle name input."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Please provide your phone number:")
    return PHONE

async def request_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle phone number input."""
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Please provide your address:")
    return ADDRESS

async def request_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle address input and send the request to the admin."""
    context.user_data['address'] = update.message.text
    item_id = context.user_data.get('item_id')
    name = context.user_data.get('name')
    phone = context.user_data.get('phone')
    address = context.user_data.get('address')

    # Fetch product details
    product_details = get_product_details(item_id)
    if product_details:
        product_info = (
            f"*Product Name:* {product_details['name']}\n"
            f"*Brand:* {product_details['brand']}\n"
            f"*Model:* {product_details['model']}\n"
        )
    else:
        product_info = "Product details not available."

    
    current_date = datetime.now().strftime('%A, %b %d, %Y')

    
    username = update.message.from_user.username or "No username"

    
    request_details = (
        f"📨 *New Request*\n\n"
        f"*Date:* {current_date}\n"
        f"*Username:* {username}\n"
        f"*Name:* {name}\n"
        f"*Phone:* {phone}\n"
        f"*Address:* {address}\n\n"
        f"🛍️ *Product Information*\n"
        f"{product_info}"
    )

    
    admin_id = 1648265210
    await context.bot.send_message(chat_id=admin_id, text=request_details, parse_mode='MarkdownV2')

    
    await update.message.reply_text("Your request has been sent to the admin. We will get back to you soon.")
    
    return ConversationHandler.END

# Inline search handler
async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries for searching items."""
    query = update.inline_query.query
    if not query:
        return

    try:
        results = search_items(query)
        articles = []
        for item in results:
            item_details = fetch_item_details(item['id'])
            if item_details:
                articles.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title=item_details['name'],
                        input_message_content=InputTextMessageContent(
                            f"Product details for {item_details['name']}:\n"
                            f"Brand: {item_details['brand']}\n"
                            f"Model: {item_details['model']}\n"
                            f"Subcategory: {item_details['subcategory']}\n"
                        ),
                        description=f"Brand: {item_details['brand']}, Model: {item_details['model']}, Subcategory: {item_details['subcategory']}"
                    )
                )
            else:
                articles.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title=item['name'],
                        input_message_content=InputTextMessageContent(
                            f"Details for {item['name']} could not be retrieved."
                        ),
                        description="Details unavailable."
                    )
                )
        await update.inline_query.answer(articles, cache_time=1)

    except Exception as e:
        await update.inline_query.answer([], switch_pm_text="An error occurred, please try again.", switch_pm_parameter="error")

# Text search handler
async def text_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages for searching items."""
    query = update.message.text
    await update.message.chat.send_action(ChatAction.TYPING)
    results = search_items(query)

    if results:
        message = "Search results:\n\n"
        for item in results:
            message += (
                f"*Name:* {item['name']}\n"
                f"*Brand:* {item.get('brand', 'Unknown')}\n"
                f"*Model:* {item.get('model', 'Unknown')}\n"
                f"*Subcategory:* {item.get('subcategory', 'Unknown')}\n\n"
            )
        await update.message.reply_text(message, parse_mode='MarkdownV2')
    else:
        await update.message.reply_text("No products found.")

if __name__ == '__main__':
    load_dotenv()

    
    app = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    
    app.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_address)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    app.add_handler(InlineQueryHandler(inline_search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_search))

    
    app.run_polling()
