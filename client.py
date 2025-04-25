import requests
import json
import os

# --- Configuration ---
# Replace with the actual IP address and port if your Flask app is running elsewhere
# or if 'localhost' doesn't work. Use the IP address shown when Flask starts (e.g., 192.168.1.6)
# If running the client on the *same* machine as the server, 'localhost' or '127.0.0.1' usually works.
API_URL = "http://localhost:6999/summarize"
# API_URL = "http://192.168.1.6:6999/summarize" # Example using specific IP

BOOK_NAME = "活着"
AUTHOR = "余华"

# Output filename (will be saved in the same directory as the script)
OUTPUT_FILENAME = f"{BOOK_NAME}_summary_{AUTHOR}.json"
# --- End Configuration ---

def call_summarize_api(url, book_name, author):
    """Calls the book summarization API."""
    payload = {
        "bookName": book_name,
        "author": author
    }
    headers = {
        "Content-Type": "application/json"
    }

    print(f"Sending request to {url} for '{book_name}' by {author}...")

    try:
        # Using json=payload automatically sets Content-Type and encodes the dict
        response = requests.post(url, headers=headers, json=payload, timeout=3000) # Increased timeout for potentially long LLM calls

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        print(f"Received successful response (Status Code: {response.status_code})")
        # Return the parsed JSON data
        return response.json()

    except requests.exceptions.ConnectionError as e:
        print("\n--- Error ---")
        print(f"Could not connect to the server at {url}.")
        print("Please ensure the Flask server is running and the URL is correct.")
        print(f"Details: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print("\n--- Error ---")
        print(f"The request timed out waiting for a response from {url}.")
        print("The server might be taking too long to process the request.")
        print(f"Details: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print("\n--- Error ---")
        print(f"An error occurred during the request to {url}:")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")
        else:
            print(f"Details: {e}")
        return None
    except json.JSONDecodeError:
        print("\n--- Error ---")
        print("Failed to decode the JSON response from the server.")
        print(f"Response Text: {response.text}")
        return None

def save_to_file(data, filename):
    """Saves the provided data dictionary to a JSON file."""
    try:
        # Get the directory where the script is running
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)

        print(f"Saving response to {filepath}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            # Use ensure_ascii=False to keep non-ASCII characters (like Chinese) as they are
            # Use indent=4 for pretty printing
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved data to {filepath}")
        return True
    except IOError as e:
        print("\n--- Error ---")
        print(f"Could not write to file {filename}: {e}")
        return False
    except Exception as e:
        print("\n--- Error ---")
        print(f"An unexpected error occurred while saving the file: {e}")
        return False

if __name__ == "__main__":
    # Call the API
    summary_data = call_summarize_api(API_URL, BOOK_NAME, AUTHOR)

    # If data was received successfully, save it
    if summary_data:
        save_to_file(summary_data, OUTPUT_FILENAME)
    else:
        print("\nAPI call failed. Did not save data.")
