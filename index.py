import keepa
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Keepa API
API_KEY = "YOUR_KEEPA_API_KEY"  # Replace with your Keepa API key
api = keepa.Keepa(API_KEY)

def keepa_to_unix(keepa_minutes):
    """
    Convert Keepa time to Unix timestamp.
    """
    return (keepa_minutes + 21564000) * 60

def fetch_rating_count(asin, domain="US"):
    """
    Fetch ratingCount data for a specific ASIN using the Keepa API.
    """
    try:
        logging.info(f"Fetching data for ASIN: {asin}")
        products = api.query(asin, domain=domain, history=True, rating=1)
        if not products:
            logging.warning(f"No data found for ASIN: {asin}")
            return []

        product = products[0]
        if "ratingCount" not in product["data"]:
            logging.warning(f"No ratingCount data found for ASIN: {asin}")
            return []

        # Extract ratingCount data
        rating_count = product["data"]["ratingCount"]
        return rating_count
    except Exception as e:
        logging.error(f"Error fetching data for ASIN {asin}: {e}")
        return []

def process_rating_count(rating_count):
    """
    Process ratingCount data into time-count pairs.
    """
    if not rating_count:
        return []

    # Convert to list of tuples: [(keepaTime, count), ...]
    time_count_pairs = []
    for i in range(0, len(rating_count) - 1, 2):
        keepa_time = rating_count[i]
        count = rating_count[i + 1]
        time_count_pairs.append((keepa_time, count))

    return time_count_pairs

def convert_to_unix_timestamps(time_count_pairs):
    """
    Convert Keepa time to Unix timestamps.
    """
    processed_data = []
    for keepa_time, count in time_count_pairs:
        unix_time = keepa_to_unix(keepa_time)
        processed_data.append((unix_time, count))
    return processed_data

def filter_last_90_days(processed_data):
    """
    Filter data for the last 90 days.
    """
    cutoff_timestamp = int((datetime.now() - timedelta(days=90)).timestamp())
    filtered_data = [
        (unix_time, count) 
        for unix_time, count in processed_data 
        if unix_time >= cutoff_timestamp
    ]
    return filtered_data

def calculate_rise(filtered_data):
    """
    Calculate the rise in count over the last 90 days.
    """
    if len(filtered_data) < 2:
        logging.warning("Not enough data to calculate rise.")
        return 0

    oldest_count = filtered_data[0][1]
    newest_count = filtered_data[-1][1]
    rise = newest_count - oldest_count
    return rise

def plot_data(filtered_data):
    """
    Plot the count values over time.
    """
    if not filtered_data:
        logging.warning("No data to plot.")
        return

    timestamps, counts = zip(*filtered_data)
    dates = [datetime.fromtimestamp(ts) for ts in timestamps]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, counts, marker='o', linestyle='-', color='b')
    plt.title("Rating Count Over Time")
    plt.xlabel("Date")
    plt.ylabel("Rating Count")
    plt.grid(True)
    plt.show()

def main(asin, domain="US"):
    """
    Main function to fetch and process rating count data.
    """
    logging.info("Starting processing...")

    # Step 1: Fetch ratingCount data
    rating_count = fetch_rating_count(asin, domain)
    if not rating_count:
        logging.error("No ratingCount data found.")
        return

    # Step 2: Process into time-count pairs
    time_count_pairs = process_rating_count(rating_count)
    if not time_count_pairs:
        logging.error("No valid time-count pairs found.")
        return

    # Step 3: Convert to Unix timestamps
    processed_data = convert_to_unix_timestamps(time_count_pairs)

    # Step 4: Filter for the last 90 days
    filtered_data = filter_last_90_days(processed_data)

    # Step 5: Calculate rise
    rise = calculate_rise(filtered_data)
    logging.info(f"Rise in ratingCount over the last 90 days: {rise}")

    # Step 6: Plot data
    plot_data(filtered_data)

# Example usage
if __name__ == "__main__":
    ASIN = "<ASIN>"  # Replace with your ASIN
    main(ASIN)

### ADD OTHER METHODS 