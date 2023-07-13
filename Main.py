import logging
from datetime import time

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
from telegram.ext import Application, CommandHandler

# Import Conversation Handler
from Login import conv_login_handler
from Logout import conv_logout_handler, program_restart
from Assign import mechanic_assign, mechanic_accept, conv_reject_handler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5916879980:AAG_pQ9Qy-d4K6wV0nCKCf33uS2OTj0P9Fc").build()
    job_queue = application.job_queue

    # Add conversation login handler
    application.add_handler(conv_login_handler())
    # Add conversation logout handler 
    application.add_handler(conv_logout_handler())
    # Add mechanic accept handler
    application.add_handler(CommandHandler("accept", mechanic_accept))
    # Add conversation reject handler
    application.add_handler(conv_reject_handler())

    # Add Assign Pool Mechanic handler (Job Queue)
    job_queue.run_repeating(mechanic_assign, interval=2)
    # Run Once When program is start running with 10s delay (Job Queue)
    job_queue.run_once(program_restart, 10)
    # Run Every Shift Changes
    # S1
    job_queue.run_daily(program_restart, time(22, 40, 0))
    # S2
    job_queue.run_daily(program_restart, time(15, 40, 0))
    # S3
    job_queue.run_daily(program_restart, time(7, 10, 0))


    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()