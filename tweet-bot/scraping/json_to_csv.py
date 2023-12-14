import json
import csv

# Load the JSON data from a file
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Extract caption and image_text and save to CSV
def save_to_csv(data, output_filename):
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['caption', 'image_text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in data:
            writer.writerow({'caption': item.get('caption', ''), 'image_text': item.get('image_text', '')})

# Main function to load JSON and save to CSV
def main():
    json_filename = 'outputs/iamjenmann.json'  # Replace with your JSON filename
    csv_filename = 'outputs/iamjenmann.csv'  # Name of the output CSV file

    json_data = load_json(json_filename)
    save_to_csv(json_data, csv_filename)

if __name__ == "__main__":
    main()