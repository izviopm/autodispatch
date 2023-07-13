import Model

from datetime import datetime, timedelta, time

# # Get Shift Today
# def get_shift():
#     now = datetime.now()
#     current_time = now.time()

#     if current_time > time(7, 10, 0) and current_time < time(15, 40, 0):
#         return "S2"
#     elif current_time > time(15, 40, 0) and current_time < time(22, 40, 0):
#         return "S3"
#     else:
#         return "S1"

# # Get Mechanic Data
# mechanic = Model.getMechanicData(mechanicIdentity=29)
# date_stamp = datetime.now().strftime("%m/%d/%Y")
# date_tomorrow = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
# shift_now = get_shift()

# if mechanic:
#     print(f"Selamat Datang Kembali {mechanic.name}")
#     print(f"{mechanic.chat_id}")
# else:
#     print("Tidak ada")

# test = Model.getMechanicFromChatID(728782)
# print(test)

# workOrders = Model.getAllJob()
# for workOrder in workOrders:
#     print(workOrder.chatid)

# rejectData = Model.getWoRejectReason(reasonID="1")
# print(rejectData.reasonname)

s3 = time(22, 40, 0)
print(type(s3))