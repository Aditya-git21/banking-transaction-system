import os
import psycopg2
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Credit Lambda file loaded")

def get_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=int(os.environ["DB_PORT"])
    )

def lambda_handler(event, context):
    logger.info(f"Event received: {event}")

    txn_id = event.get("txn_id")
    to_acc = event["to_account"]
    amount = event["amount"]

    conn = None
    cur = None

    try:
        conn = get_connection()
        conn.autocommit = False
        cur = conn.cursor()

        # Credit account
        cur.execute(
            """
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_id = %s
            RETURNING balance
            """,
            (amount, to_acc)
        )

        if cur.rowcount == 0:
            raise Exception("Destination account not found")

        new_balance = cur.fetchone()[0]
        logger.info(f"Credit successful. New balance: {new_balance}")

        # Update transaction status
        cur.execute(
            """
            UPDATE transactions
            SET status = %s
            WHERE txn_id = %s
            """,
            ("CREDIT_SUCCESS", txn_id)
        )

        conn.commit()
        logger.info(f"Credit committed for TXN_ID={txn_id}")

        return {
            "status": "CREDIT_SUCCESS",
            "txn_id": txn_id
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Credit failed: {str(e)}")

        return {
            "status": "FAILED",
            "reason": str(e)
        }

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        logger.info("DB connection closed")

