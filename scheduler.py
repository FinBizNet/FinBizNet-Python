import schedule
import time
from controllers.smartapi_controllers import update_ticker_data_to_db

def job():
    print("🔁 Updating ticker data to DB...")
    update_ticker_data_to_db()

# Run the job once on script start (for immediate testing)
print("🔥 Running job manually to test DB update now...")
job()

# Schedule the job every 5 minutes
schedule.every(5).minutes.do(job)

# Keep running and waiting
while True:
    print("⏳ Waiting to run scheduled job...")
    schedule.run_pending()
    time.sleep(10)
