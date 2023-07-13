import pyodbc

def execute_query(sql_query, is_select=False, is_fetch_one=False):
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=DCKR00155607A,49170;'
                              'DATABASE=FAR;'
                              'UID=sa;'
                              'PWD=user001')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        if is_select:
            if is_fetch_one:
                row = cursor.fetchone()
                return row
            else:
                rows = cursor.fetchall()
                return rows
        else:
            conn.commit()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
