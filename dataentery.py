import scham



def select_user(phone, password):
    conn, cursor = scham.connection()

    cursor.execute("SELECT * FROM PersonalInfo WHERE phone = %s AND password = %s", (phone, password))
    user = cursor.fetchone()

    cursor.execute("""
		    SELECT entry_data_date, result_id FROM CalculationResults
		    WHERE phone = %s
		    ORDER BY entry_data_date ASC
		""", (phone,))
    calculations = cursor.fetchall()
    

    conn.close()
    return user, calculations

def select_result(phone, entry_id):
    conn, cursor = scham.connection()

    cursor.execute("""
		    SELECT * FROM CalculationResults
		    WHERE phone = %s and result_id = %s
		""", (phone, entry_id))
    result = cursor.fetchall()
    

    conn.close()
    return result