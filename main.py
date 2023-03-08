import json
from google.cloud import translate_v2 as translate
from tqdm import tqdm
import time
import multiprocessing
import random
from unidecode import unidecode

# Open JSON file and load data
with open("data.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Create Google Translate API client
translate_client = translate.Client.from_service_account_json("credentials.json")

# Define the translation function to be executed in parallel
def translate_text(key, value):
    # Retrieve the text you want to translate from the JSON data
    ru_text = value.get("ru")
    if ru_text is not None and isinstance(ru_text, str):
        try:
            # Add a delay between requests
            time.sleep(random.uniform(0.5, 2.0))
            result = translate_client.translate(ru_text, target_language="ro")
            # Exclude special characters and replace diacritics
            translated_text = unidecode(''.join(e for e in result["translatedText"] if e.isalnum() or e.isspace() or e=="№"))
            value["ro"] = translated_text
        except Exception as e:
            print("Translation failed:", e)
            translated_text = None
    return key, value

if __name__ == '__main__':
    # Start timer
    start_time = time.time()

    # Use multiprocessing to translate text strings in parallel
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = [pool.apply_async(translate_text, args=(key, value)) for key, value in data.items()]
        data = dict([result.get() for result in tqdm(results, desc="Translating", unit=" lines")])

    # Stop timer
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    # Output the updated JSON data to a new file
    with open("updated_data_before.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
