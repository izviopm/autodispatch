import Model
import logging
from datetime import datetime, time

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

MECHANIC_LOGOUT = range(1)

# Function Get Shift Now
def get_shift():
    now = datetime.now()
    current_time = now.time()

    if current_time > time(7, 10, 0) and current_time < time(15, 40, 0):
        return "S2"
    elif current_time > time(15, 40, 0) and current_time < time(22, 40, 0):
        return "S3"
    else:
        return "S1"


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation Logout"""
    user = update.message.from_user
    logger.info(f"User {user.full_name} Start Conversation Logout with ChatID: {update.message.chat_id}")

    # Get Mechanic Data From ChatID
    mechanic = Model.getMechanicFromChatID(ChatID=update.message.chat_id)

    # Has the Mechanic Logged In?
    if mechanic and mechanic.check_in == 1:
        # Send Logger Info
        logger.info(f"User {user.full_name} with KPK: {mechanic.idkpk} Request to Logout")

        # Setup Inline Keyboard
        keyboard = [
            [ 
                InlineKeyboardButton("✅ YES!", callback_data="YES" + "," + f"{mechanic.idkpk}" + "," + f"{mechanic.name}" + "," + f"{mechanic.chat_id}"), 
                InlineKeyboardButton("❎ NO!", callback_data="NO" + "," + f"{mechanic.idkpk}" + "," + f"{mechanic.name}" + "," + f"{mechanic.chat_id}"), 
            ], 
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send Response to User
        await update.message.reply_text(
            "⚠ *Peringatan Logout!* \n\n"
            "Apakah Anda yakin ingin keluar dari system?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return MECHANIC_LOGOUT
    
    # The Mechanic is not Logged In
    else:
        # Send Logger Info
        logger.info(f"User {user.full_name} is not Login")

        # Send Response to User
        await update.message.reply_text(
            "⚠ *Anda belum terhubung di System Autodispatch FAR bot!*\n\n"
            "Silahkan Login terlebih dahulu untuk masuk kedalam System dengan mengirimkan pesan /start atau /login", 
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    

async def mechanic_logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User Send the Answer"""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    splitData = query.data.split(',')
    userAnswer = splitData[0]
    userKPK = splitData[1]
    userName = splitData[2]
    userChatID = splitData[3]
    
    # Mechanic Choose "YES"
    if userAnswer == "YES":
        currentShift = get_shift()
        dateStamp = datetime.now().strftime("%m/%d/%Y")
        timeStamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

        # Update Mechanic Realtime
        Model.putMechanicRealtime(
            KPK=userKPK,
            Date=dateStamp,
            Shift=currentShift,
            TS=timeStamp,
            ChatID=userChatID
        )

        # Update Mechanic Log
        Model.putMechanicLog(
            Date=timeStamp,
            KPK=userKPK
        )

        # Un Assign Mechanic
        Model.putMechanicStatus(
            AssignSet=0,
            KPK=userKPK
        )

        logger.info(f"User Success Logout")
        await query.edit_message_text(
            text=f"*Hi {userName}!* Anda berhasil logout dari System! \n\n"
            "Terimakasih telah menggunakan Autodispatch Bot! 😊\n\n"
            "Apabila anda ingin kembali kedalam System, Silahkan Login kembali dengan mengirimkan pesan /start atau /login",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    
    # Mechanic Choose "NO"
    else:
        await query.edit_message_text(
            text=f"*Logout Dibatalkan! * \n"
            "\nAnda masih di dalam System, jika anda ingin keluar dari System, kirimkan pesan /logout",
            parse_mode="Markdown"
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the logout conversation.", user.first_name)
    await update.message.reply_text(
        "Logout Dibatalkan!\n\n"
        "Anda membatalkan proses logout!", 
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def program_restart(context: ContextTypes.DEFAULT_TYPE):
    # Get Time
    currentShift = get_shift()
    dateStamp = datetime.now().strftime("%m/%d/%Y")
    timeStamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    usersLogin = Model.getRemainUserLogin()
    usersWoLogin = Model.getRemainUserWo()

    # User on waiting (Login)
    if usersLogin != [] or len(usersLogin) != 0:
        for userLogin in usersLogin:
            # Update Mechanic Log
            Model.putMechanicLog(
                Date=timeStamp, 
                KPK=userLogin.idkpk
            )

            # Update Mechanic Realtime
            Model.putMechanicRealtime(
                KPK=userLogin.idkpk,
                Date=dateStamp,
                Shift=currentShift,
                TS=timeStamp,
                ChatID=userLogin.chat_id
            )

            # Send Response to Mechanic
            await context.bot.send_message(
                chat_id=userLogin.chat_id,
                text="*Program Restart!* \n\n"
                    f"Mohon maaf, program baru saja direset oleh developer/pergantian shift."
                    "\nSilahkan kirimkan pesan /start atau /login untuk masuk kembali kedalam sistem.",
                parse_mode="Markdown"
            )

    # User on WorkOrder (Login)
    if usersWoLogin != [] or len(usersWoLogin) != 0:
        for userWoLogin in usersWoLogin:
            # Update Mechanic Log
            Model.putMechanicLog(
                Date=timeStamp, 
                KPK=userWoLogin.idkpk
            )

            # Update Mechanic Realtime
            Model.putMechanicRealtime(
                KPK=userWoLogin.idkpk,
                Date=dateStamp,
                Shift=currentShift,
                TS=timeStamp,
                ChatID=userWoLogin.chat_id
            )

            # Send Response to Mechanic
            await context.bot.send_message(
                chat_id=userWoLogin.chat_id,
                text="*Program Restart!* \n\n"
                    f"Mohon maaf, program baru saja direset oleh developer/pergantian shift."
                    "\nSilahkan menyelesaikan WO yang sedang berlangsung saat ini. Untuk menerima WO berikutnya, silahkan menekan tombol /start atau /login untuk masuk kembali kedalam sistem.",
                parse_mode="Markdown"
            )

    
def conv_logout_handler():
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("logout", logout)],
        states={
            MECHANIC_LOGOUT: [CallbackQueryHandler(mechanic_logout)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    return conv_handler