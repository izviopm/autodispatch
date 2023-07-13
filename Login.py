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
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

MECHANIC_IDENTITY = range(1)

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation"""
    user = update.message.from_user
    logger.info(f"User {user.full_name} Start Conversation Login with ChatID: {update.message.chat_id}")
    
    # Get Time
    currentShift = get_shift()
    dateStamp = datetime.now().strftime("%m/%d/%Y")
    timeStamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    
    # Get Mechanic Data From ChatID
    mechanic = Model.getMechanicFromChatID(ChatID=update.message.chat_id)

    if mechanic and mechanic.check_in == 0:
        # Send Logger INFO
        logger.info(f"{mechanic.idkpk} - Success Re-Login!")

        # Insert mechanic_log table
        Model.postMechanicLog(KPK=mechanic.idkpk,
                              Date=dateStamp,
                              Shift=currentShift,
                              TS=timeStamp,
                              ChatID=update.message.chat_id,
                              CheckIn=1)
        
        # Update mechanic_realtime table
        Model.putMechanicRealtime(KPK=mechanic.idkpk,
                                  Date=dateStamp,
                                  Shift=currentShift,
                                  TS=timeStamp,
                                  ChatID=update.message.chat_id,
                                  isLogin=True)

        # Send Response to User
        await update.message.reply_text(
            f"Selamat Datang Kembali *{ mechanic.name }!* \n\n"
            "Anda sudah terhubung kedalam Sistem ✨ \n"
            "Silahkan menunggu update pemberitahuan downtime mesin terbaru ⏩ \n\n"
            "Jika Anda ingin keluar dari sistem, silahkan kirimkan pesan /logout",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    elif mechanic and mechanic.check_in == 1:
        # Send Logger INFO
        logger.info(f"{mechanic.idkpk} - Request Double Login!")

        # Send Response to User
        await update.message.reply_text(
            f"Hi *{ mechanic.name }!* \n\n"
            "*KPK/OEE ID* Anda masih terhubung kedalam Sistem ✨ \n"
            "Silahkan menunggu update pemberitahuan downtime mesin terbaru ⏩ \n\n"
            "Jika Anda ingin keluar dari sistem, silahkan kirimkan pesan /logout",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    else:    
        await update.message.reply_text(
            "*Selamat Datang di Autodispatch FAR bot!* \n"
            "Silahkan Masukan *KPK* atau *OEE ID* untuk melakukan proses Login, atau kirimkan pesan /cancel untuk membatalkan proses login", 
            parse_mode="Markdown"
        )
        return MECHANIC_IDENTITY


async def mechanic_identity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about Mechanic Identity and Get Mechanic Name"""
    user = update.message.from_user
    logger.info(f"User {user.full_name} Send KPK / OEE ID: {update.message.text}")
    mechanicIdentity = update.message.text

    # Filter Message from User
    if update.message.text.isdigit():
        mechanic = Model.getMechanicData(mechanicIdentity=mechanicIdentity)
        currentShift = get_shift()
        dateStamp = datetime.now().strftime("%m/%d/%Y")
        timeStamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

        # Mekanik dengan ChatID yang sama dan belum Login
        if mechanic and mechanic.chat_id == update.message.chat_id and mechanic.check_in == 0:
            # Send Logger INFO
            logger.info(f"{mechanic.idkpk} - Success Re-Login!")

            # Insert mechanic_log table
            Model.postMechanicLog(KPK=mechanic.idkpk,
                                  Date=dateStamp,
                                  Shift=currentShift,
                                  TS=timeStamp,
                                  ChatID=update.message.chat_id,
                                  CheckIn=1)
            
            # Update mechanic_realtime table
            Model.putMechanicRealtime(KPK=mechanic.idkpk,
                                      Date=dateStamp,
                                      Shift=currentShift,
                                      TS=timeStamp,
                                      ChatID=update.message.chat_id,
                                      isLogin=True)

            # Send Response to User
            await update.message.reply_text(
                f"Selamat Datang Kembali *{ mechanic.name }!* \n\n"
                "Anda sudah terhubung kedalam Sistem ✨ \n"
                "Silahkan menunggu update pemberitahuan downtime mesin terbaru ⏩ \n\n"
                "Jika Anda ingin keluar dari sistem, silahkan kirimkan pesan /logout",
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        
        # Mekanik masih Login
        elif mechanic and mechanic.chat_id == update.message.chat_id and mechanic.check_in == 1:
            # Send Logger INFO
            logger.info(f"{mechanic.idkpk} - Request Double Login!")

            # Send Response to User
            await update.message.reply_text(
                f"Hi *{ mechanic.name }!* \n\n"
                "*KPK/OEE ID* Anda masih terhubung kedalam Sistem ✨ \n"
                "Silahkan menunggu update pemberitahuan downtime mesin terbaru ⏩ \n\n"
                "Jika Anda ingin keluar dari sistem, silahkan kirimkan pesan /logout",
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        
        # Mekanik login dengan perangkat yang berbeda dari yang sebelumnya
        elif mechanic and mechanic.chat_id and mechanic.chat_id != update.message.chat_id:
            # Send Logger INFO
            logger.info(f"{mechanic.idkpk} - Another device request to Login to that Account (REJECT REQUEST)")

            # Send Response to User
            await update.message.reply_text(
                f"⚠ Maaf *KPK/OEE ID* sudah terhubung ke perangkat lain! \n\n"
                "Jika anda adalah pemilik asli *KPK/OEE ID* tersebut harap hubungi Administrator",
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        
        # Mekanik sudah tersedia di table mechanic_status tapi belum tersedia di table mechanic_realtime (Login Pertama Kali)
        elif mechanic and mechanic.idkpk and mechanic.idoee:
            # Send Logger INFO
            logger.info(f"{mechanic.idkpk} - Success First Time Login")

            # Insert mechanic_log table
            Model.postMechanicLog(KPK=mechanic.idkpk,
                                  Date=dateStamp,
                                  Shift=currentShift,
                                  TS=timeStamp,
                                  ChatID=update.message.chat_id,
                                  CheckIn=1)
            
            # Insert mechanic_realtime table
            Model.postMechanicRealtime(KPK=mechanic.idkpk,
                                       Date=dateStamp,
                                       Shift=currentShift,
                                       TS=timeStamp,
                                       ChatID=update.message.chat_id,
                                       CheckIn=1)
            
            # Send Response to User
            await update.message.reply_text(
                f"Selamat Datang *{ mechanic.name }!* \n\n"
                "Anda sudah terhubung kedalam Sistem ✨ \n"
                "Silahkan menunggu update pemberitahuan downtime mesin terbaru ⏩ \n\n"
                "Jika Anda ingin keluar dari sistem, silahkan kirimkan pesan /logout",
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        
        # KPK / ID yang dimasukan tidak terdaftar di table mechanic_status
        else:
            # Send Logger INFO
            logger.info(f"{mechanicIdentity} - Cannot find that KPK or ID OEE (The KPK/OEE ID is not registered in mechanic_status table)")

            # Send Response to User
            await update.message.reply_text(
                "⚠ *KPK/ID* anda tidak terdaftar di System! \n\n" 
                "Silahkan masukan kembali *KPK/ID* anda, atau kirimkan pesan /cancel untuk membatalkan proses login",
                parse_mode="Markdown"
            )
            return MECHANIC_IDENTITY
    else:
        # Send Response to User
        await update.message.reply_text(
            '⚠ *KPK/OEE ID* yang anda masukan bukan angka harap masukan input *KPK/OEE ID* yang benar', 
            parse_mode="Markdown"
        )
        return MECHANIC_IDENTITY


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the login conversation.", user.first_name)
    await update.message.reply_text(
        "Login Dibatalkan!\n\n"
        "Anda membatalkan proses login!", 
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def conv_login_handler():
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("login", start),
        ],
        states={
            MECHANIC_IDENTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, mechanic_identity)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    return conv_handler

    