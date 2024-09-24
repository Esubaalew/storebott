from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, InlineQueryHandler, MessageHandler, filters
from api import get_categories, get_subcategories, get_brands, get_models, get_products, get_product_details, check_stock_availability, search_items, fetch_item_details
from uuid import uuid4
from dotenv import load_dotenv
from telegram.constants import ChatAction

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
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            formatted_details = (
                f"📱 *{product_details['name']}*\n\n"
                f"*Brand:* {product_details['brand']}\n"
                f"*Model:* {product_details['model']}\n"
                f"*Subcategory:* {product_details['subcategory']}\n"
            )
            # Add a button for checking stock availability
            keyboard = [
                [InlineKeyboardButton("Check Availability", callback_data=f"check_stock_{item_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(formatted_details, reply_markup=reply_markup, parse_mode='MarkdownV2')
        else:
            await query.edit_message_text("No product details available.")

    elif data.startswith('check_stock_'):
        item_id = data.split('_')[2]
        stock_details = check_stock_availability(item_id)
        if stock_details:
            is_available = "Yes" if stock_details['is_available'] else "No"
            await query.edit_message_text(f"Stock availability:\n"
                                          f"Item: {stock_details['item']}\n"
                                          f"Quantity: {stock_details['quantity']}\n"
                                          f"Available: {is_available}")
        else:
            await query.edit_message_text("Stock details not available.")

async def inline_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries for searching items."""
    query = update.inline_query.query
    if not query:
        return

    try:
        # Perform search using your API
        results = search_items(query)
        print(f"Search results for '{query}': {results}")

        
        articles = []
        for item in results:
            
            item_details = fetch_item_details(item['id']) 
            print(f"Details for item '{item['name']}': {item_details}")
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
                print(f"Could not fetch details for item ID: {item['id']}")
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
        print("Inline query answered with articles.")

    except Exception as e:
        print(f"Error processing inline query: {e}")
        await update.inline_query.answer([], switch_pm_text="An error occurred, please try again.", switch_pm_parameter="error")


    except Exception as e:
        print(f"Error processing inline query: {e}")
        await update.inline_query.answer([], switch_pm_text="An error occurred, please try again.", switch_pm_parameter="error")




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
    import os
    load_dotenv()

    # Create the application
    app = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    # Add command and query handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(InlineQueryHandler(inline_search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_search))  # Handle text messages

    # Run the bot
    app.run_polling()
