import os
import psycopg2
import uuid

def get_connection():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ['DB_PORT']
    )

def lambda_handler(event, context):
    txn_id = str(uuid.uuid4())
    from_acc = event['from_account']
    to_acc = event['to_account']
    amount = event['amount']
    idem_key = event['idempotency_key']

    conn = get_connection()
    cur = conn.cursor()

    try:
        conn.autocommit = False

        # Idempotency check
        cur.execute(
            "SELECT status FROM transactions WHERE idempotency_key=%s",
            (idem_key,)
        )
        if cur.fetchone():
            return {"status": "DUPLICATE"}

        # Debit account
        cur.execute("""
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_id = %s AND balance >= %s
            RETURNING balance
        """, (amount, from_acc, amount))

        if cur.rowcount == 0:
            raise Exception("Insufficient balance")

        # Record transaction
        cur.execute("""
            INSERT INTO transactions
            (txn_id, from_account, to_account, amount, status, idempotency_key)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (txn_id, from_acc, to_acc, amount, "DEBIT_SUCCESS", idem_key))

        conn.commit()
        return {"status": "DEBIT_SUCCESS", "txn_id": txn_id}

    except Exception as e:
        conn.rollback()
        return {"status": "FAILED", "reason": str(e)}

    finally:
        cur.close()
        conn.close()

