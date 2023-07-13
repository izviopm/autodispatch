import Model
import logging
from datetime import datetime, time, timedelta

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
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

MECHANIC_REJECT = range(1)

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


async def mechanic_assign(context: ContextTypes.DEFAULT_TYPE):
    # Get Time
    currentTime = datetime.now()
    currentShift = get_shift()
    dateStamp = datetime.now().strftime("%m/%d/%Y")
    timeStamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    # Condition for WO assign detected
    workOrders = Model.getAllJob()
    if (workOrders != [] or len(workOrders) != 0):
        for workOrder in workOrders:
            # Update Work Order Notified
            Model.putNotifiedAllJob(
                JobID=workOrder.id,
                TimeStamp=timeStamp
            )
            
            await context.bot.send_message(
                chat_id=workOrder.chatid,
                text="*Pemberitahuan Work Order!* \n\n"
                    f"Anda ditugaskan untuk memperbaiki *{workOrder.reason}* pada mesin: *{workOrder.machineid}*"
                    "\nSilahkan kirimkan pesan /accept untuk *MENERIMA* work order atau kirimkan pesan /reject untuk *MENOLAK* work order.",
                parse_mode="Markdown"
            )
    
    # Condition for WO finish detected
    workOrdersDone = Model.getAllJobDone()
    if (workOrdersDone != [] or len(workOrdersDone) != 0):
        for workOrderDone in workOrdersDone:
            # Update Work Order Notified Done
            Model.putNotifiedAllJob(
                JobID=workOrderDone.id,
                TimeStamp=timeStamp,
                isNotified=True
            )

            await context.bot.send_message(
                chat_id=workOrderDone.chatid,
                text=f'*Whale Done!* 🐳 \n'
                    f'Pekerjaan anda memperbaiki mesin *{workOrderDone.machineid}* dengan downtime: *{workOrderDone.reason}* sudah selesai.\n'
                    'Terimakasih banyak atas kontribusinya 😊\n'
                    'Silahkan menunggu update pemberitahuan downtime mesin terbaru berikutnya ⏩ \n\n'
                    'Jika Anda ingin keluar dari sistem, silahkan kirimkan pesan /logout',
                parse_mode="Markdown"
            )
    
    # Condition for user AFK
    workOrdersSent = Model.getAllJob(isNotified=True)
    if (workOrdersSent != [] or len(workOrdersSent) != 0):
        for workOrderSent in workOrdersSent:
            time_limit = workOrderSent.notified + timedelta(seconds=60)
            if currentTime > time_limit and workOrderSent.notified:
                # User AFK
                # Update Reject Reason (Stat 10: Unreachable)
                Model.putReject(
                    Reason=10,
                    JobID=workOrderSent.id,
                    WoStatus=0
                )

                # Update mechanic_realtime (Logout)
                Model.putMechanicRealtime(
                    KPK=workOrderSent.kpk,
                    Date=dateStamp,
                    Shift=currentShift,
                    TS=timeStamp,
                    ChatID=workOrderSent.chatid
                )

                # Update Mechanic Log
                Model.putMechanicLog(
                    Date=timeStamp,
                    KPK=workOrderSent.kpk
                )

                # Update Wo
                Model.putWOReject(
                    MachineID=workOrderSent.machineid,
                    TimeStamp=timeStamp
                )

                # Un Assign Mechanic
                Model.putMechanicStatus(
                    AssignSet=0,
                    KPK=workOrderSent.kpk
                )

                # Send Response to User
                await context.bot.send_message(
                    chat_id=workOrderSent.chatid,
                    text=f'⚠ *Anda tidak Menjawab Work Order!* \n\n'
                        f'Anda tidak menjawab panggilan Work Order pada mesin *{workOrderSent.machineid}* dengan downtime: *{workOrderSent.reason}* dalam 1 menit.\n'
                        'Silahkan mengirimkan pesan /login untuk masuk kembali kedalam System',
                    parse_mode="Markdown"
                )
                

async def mechanic_accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts The Conversation Accept"""
    user = update.message.from_user
    logger.info(f"User {user.full_name} Start Conversation Accept with ChatID: {update.message.chat_id}")

    # Get Time
    timeStamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    # Get Data Mechanic from Chat ID
    mechanic = Model.getMechanicFromChatID(ChatID=update.message.chat_id)

    if mechanic:
        # Get WO
        workOrder = Model.getWOAccept(mechanic.idkpk)

        if workOrder:
            # Update Wo Accept
            Model.putWOAccept(
                TimeStamp=timeStamp,
                MachineID=workOrder.machineid,
                WoStatus=0
            )
            
            # Send Response to User
            await update.message.reply_text(
                text="*Work Order Diterima! \n\n"
                    f"Silahkan mendatangi Mesin: *{workOrder.machineid}*"
                    f"Untuk memberbaiki masalah *{workOrder.reason}* dengan JobID: {workOrder.id}",
                parse_mode="Markdown"
            )
    else:
        # Send Response to User
        await update.message.reply_text(
            "⚠ *Anda belum menerima Work Order!*\n\n"
            "Silahkan menunggu update pemberitahuan downtime mesin terbaru", 
            parse_mode="Markdown"
        )


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts The Conversation Reject"""
    user = update.message.from_user
    logger.info(f"User {user.full_name} Start Conversation Reject with ChatID: {update.message.chat_id}")

    # Get Data Mechanic from Chat ID
    mechanic = Model.getMechanicFromChatID(ChatID=update.message.chat_id)

    if mechanic:
        # Get WO
        workOrder = Model.getWoReject(mechanic.idkpk)

        if workOrder:
            keyboard = [
                [InlineKeyboardButton("1. Heat Fusion", callback_data="1" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}"),],
                [InlineKeyboardButton("2. WO Changeover", callback_data="2" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}"),],
                [InlineKeyboardButton("3. Buy Off Mask", callback_data="3" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}"),],
                [InlineKeyboardButton("4. Issue Curling", callback_data="4" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}"),],
                [InlineKeyboardButton("5. Manual Rooting", callback_data="5" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}"),],
                [InlineKeyboardButton("6. Piloting Job", callback_data="6" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}"),],
                [InlineKeyboardButton("7. Metal Detector", callback_data="7" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}"),],
                [InlineKeyboardButton("8. Mesin Oven", callback_data="8" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}"),],
                [InlineKeyboardButton("9. Trial", callback_data="9" + "," + f"{mechanic.idkpk}" + "," + f"{workOrder.machineid}" + "," + f"{update.message.chat_id}" + "," + f"{workOrder.reason}" + "," + f"{workOrder.id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text="Silahkan pilih alasan penolakan dengan menekan tombol dibawah ini:",
                reply_markup=reply_markup
            )
            return MECHANIC_REJECT
        
    else:
        # Send Response to User
        await update.message.reply_text(
            "⚠ *Anda belum menerima Work Order!*\n\n"
            "Silahkan menunggu update pemberitahuan downtime mesin terbaru", 
            parse_mode="Markdown"
        )
        return ConversationHandler.END


async def mechanic_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    # Get Time
    currentShift = get_shift()
    timeStamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    dateStamp = datetime.now().strftime("%m/%d/%Y")

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    splitData = query.data.split(',')
    userAnswer = splitData[0]
    userKPK = splitData[1]
    machineID = splitData[2]
    userChatID = splitData[3]
    reason = splitData[4]
    woID = splitData[5]

    rejectData = Model.getWoRejectReason(reasonID=userAnswer)
    logger.info(f"User Answer: {userAnswer},"
                f" User KPK: {userKPK},"
                f" MachineID: {machineID},"
                f" ChatID: {userChatID},"
                f" Dt Reason: {reason},"
                f" WoID: {woID},"
                f" Reject Reason: {rejectData.reasonname}")

    # Update Reject Reason
    Model.putReject(
        Reason=userAnswer,
        JobID=woID,
        WoStatus=0
    )

    # Update mechanic_realtime (Logout)
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

    # Update Wo
    Model.putWOReject(
        MachineID=machineID,
        TimeStamp=timeStamp
    )

    # Un Assign Mechanic
    Model.putMechanicStatus(
        AssignSet=0,
        KPK=userKPK
    )

    await query.edit_message_text(
        text="*Penolakan Work Order Berhasil! * \n"
            f"\nPenolakan masalah {reason} untuk mesin {machineID} dengan ID: {woID} berhasil!"
            f"\nAlasan penolakan work order: {rejectData.reasonname}."
            "\n\nSilahkan menekan tombol /login untuk masuk kembali kedalam sistem.",
        parse_mode="Markdown"
    )


def conv_reject_handler():
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("reject", reject)],
        states={
            MECHANIC_REJECT: [CallbackQueryHandler(mechanic_reject)],
        },
        fallbacks=[],
    )

    return conv_handler