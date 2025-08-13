import schedule
import time
from controllers.smartapi_controllers import update_ticker_data_to_db

def job():
    try:
        print("🔁 Updating ticker data to DB...")
        update_ticker_data_to_db()
        print("✅ DB update successful.")
    except Exception as e:
        print(f"❌ Error updating DB: {e}")


# Run the job once on script start (for immediate testing)
print("🔥 Running job manually to test DB update now...")
job()

# Schedule the job every 5 minutes
schedule.every(30).minutes.do(job)

# Keep running and waiting
while True:
    print("⏳ Waiting to run scheduled job...")
    schedule.run_pending()
    time.sleep(10)
