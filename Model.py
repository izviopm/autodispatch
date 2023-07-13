from DB import execute_query

def getMechanicData(mechanicIdentity):
    return execute_query(f"""
                            SELECT
                                ms.idoee
                                ,ms.idkpk
                                ,ms.name
                                ,mr.chat_id
                                ,mr.[date]
                                ,mr.shift 
                                ,mr.check_in 
                            FROM [FAR].[dbo].[mechanic_realtime] mr 
                            RIGHT JOIN FAR.dbo.mechanic_status ms ON mr.kpk = ms.idkpk 
                            WHERE mr.kpk = { mechanicIdentity } OR ms.idoee = { mechanicIdentity }
                        """, is_select=True, is_fetch_one=True)

def postMechanicLog(KPK, Date, Shift, TS, ChatID, CheckIn):
    execute_query(f"""
                    INSERT INTO 
                        [FAR].[dbo].[mechanic_log] (kpk,date,shift,ts_login,chat_id,check_in)
                    VALUES ({KPK}, '{Date}', '{Shift}', '{TS}', {ChatID}, {CheckIn})
                  """)

def putMechanicLog(Date, KPK):
    execute_query(f"""
                    UPDATE
                        [FAR].[dbo].[mechanic_log]
                    SET
                        ts_logout = '{Date}',
                        check_in = 0
                    WHERE kpk = {KPK}
                  """)

def postMechanicRealtime(KPK, Date, Shift, TS, ChatID, CheckIn):
    execute_query(f"""
                    INSERT INTO 
                        [FAR].[dbo].[mechanic_realtime] (kpk,date,shift,ts_login,chat_id,check_in)
                    VALUES ({KPK}, '{Date}', '{Shift}', '{TS}', {ChatID}, {CheckIn})
                  """)
    
def putMechanicRealtime(KPK, Date, Shift, TS, ChatID, isLogin=False):
    if isLogin:
        execute_query(f"""
                        UPDATE 
                            [FAR].[dbo].[mechanic_realtime] 
                        SET
                                date = '{Date}',
                                shift = '{Shift}',
                                ts_login = '{TS}',
                                ts_logout = NULL,
                                chat_id = {ChatID},
                                check_in = 1
                        WHERE kpk = {KPK}
                    """)
    else:
        execute_query(f"""
                        UPDATE 
                            [FAR].[dbo].[mechanic_realtime]
                        SET 
                            ts_login = NULL,
                            ts_logout = '{TS}',
                            check_in = 0
                        WHERE kpk = {KPK}
                      """)

def getMechanicFromChatID(ChatID):
    return execute_query(f"""
                            SELECT 
                                ms.idkpk
                                ,ms.name
                                ,mr.chat_id 
                                ,mr.check_in 
                            FROM [FAR].[dbo].[mechanic_realtime] mr
                            JOIN [FAR].[dbo].[mechanic_status] ms ON mr.kpk = ms.idkpk  
                            WHERE mr.chat_id = {ChatID}
                        """, is_select=True, is_fetch_one=True)

def putMechanicStatus(AssignSet, KPK):
    # Update Mechanic Available
    execute_query(f"""
        UPDATE 
            [FAR].[dbo].[mechanic_status]
        SET is_assign={AssignSet} WHERE idkpk={KPK}""")    

def getAllJob(isNotified=False):
    if isNotified:
        return execute_query("""
                                SELECT 
                                    * 
                                FROM [FAR].[dbo].[mechanic_wo]
                                WHERE wo_status = 0 AND notified IS NOT NULL
                            """, is_select=True)
    else:
        return execute_query("""
                                SELECT 
                                    * 
                                FROM [FAR].[dbo].[mechanic_wo]
                                WHERE wo_status = 0 AND notified IS NULL
                            """, is_select=True)

def getAllJobDone():
    return execute_query("""
                            SELECT 
                                * 
                            FROM [FAR].[dbo].[mechanic_wo]  
                            WHERE wo_status = 3 AND notified_done IS NULL
                        """, is_select=True)

def putNotifiedAllJob(JobID, TimeStamp, isNotified=False):
    if isNotified:
        execute_query(f"""
                        UPDATE 
                            [FAR].[dbo].[mechanic_wo] 
                        SET notified_done = '{TimeStamp}' 
                        WHERE id = {JobID}
                    """)
    else:
        execute_query(f"""
                    UPDATE [FAR].[dbo].[mechanic_wo] 
                    SET notified = '{TimeStamp}'
                    WHERE id = {JobID}""")
        
def getWOAccept(KPK):
    # Get WO for user accept the offer
    return execute_query(f"""
                            SELECT 
                                * 
                            FROM [FAR].[dbo].[mechanic_wo]
                            WHERE wo_status = 0 and notified_done IS NULL and kpk = {KPK}
                        """, is_select=True, is_fetch_one=True)

def putWOAccept(TimeStamp, MachineID, WoStatus):
    # Update WO for user accept the offer
    execute_query(f"""
                    UPDATE 
                        [FAR].[dbo].[mechanic_wo]
                    SET accept_datetime = '{TimeStamp}', wo_status = 1
                    WHERE machineid = '{MachineID}' AND wo_status = {WoStatus}
                """)
    
def putReject(Reason,JobID,WoStatus):
    # Update WO for user reject the offer
    execute_query(f"""
                    UPDATE
                        [FAR].[dbo].[mechanic_wo]
                    SET reject_reason = {Reason}
                    WHERE id = {JobID} AND wo_status = {WoStatus}
                """)

def putWOReject(MachineID, TimeStamp):
    # Update WO when user reject sucess
    execute_query(f"""
                    UPDATE 
                        [FAR].[dbo].[mechanic_wo]
                    SET accept_datetime = '{TimeStamp}', wo_status = 4 
                    WHERE machineid = '{MachineID}' AND wo_status = 0""")
    
def getWoReject(KPK):
    # Get WO for user reject the offer
    return execute_query(f"""
                            SELECT * FROM [FAR].[dbo].[mechanic_wo] 
                            WHERE wo_status = 0 AND reject_reason IS NULL and kpk = {KPK}
                        """, is_select=True, is_fetch_one=True) 
    
def getWoRejectReason(reasonID):
    # Get user reject reason
    return execute_query(f"""
                            SELECT * FROM [FAR].[dbo].[mechanic_reject]
                            WHERE reasonstatus = {reasonID}
                        """, is_select=True, is_fetch_one=True)

def getRemainUserLogin():
    # Get remaining user login on current shift
    return execute_query("""
                    SELECT ms.[idkpk], ms.[name],ms.[is_assign],mr.[check_in], mr.[chat_id]
                    FROM [FAR].[dbo].[mechanic_status] as ms
                    JOIN [FAR].[dbo].[mechanic_realtime] as mr
                    ON ms.idkpk = mr.kpk
                    WHERE mr.check_in = 1 and ms.is_assign = 0 
                """, is_select=True)

def getRemainUserWo():
    # Get remaining user login on current shift
    return execute_query("""
                    SELECT ms.[idkpk], ms.[name],ms.[is_assign],mr.[check_in], mr.[chat_id]
                    FROM [FAR].[dbo].[mechanic_status] as ms
                    JOIN [FAR].[dbo].[mechanic_realtime] as mr
                    ON ms.idkpk = mr.kpk
                    WHERE mr.check_in = 1 and ms.is_assign = 1 
                """, is_select=True)