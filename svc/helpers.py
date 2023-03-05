import psycopg2

def insert_ip(dsn, ip_adress):
    """ insert multiple vendors into the vendors table  """
    sql = "INSERT INTO ip_test VALUES(%s, NOW())"
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(dsn)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (ip_adress,))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except Exception as error:
        raise error
    finally:
        if conn is not None:
            conn.close()