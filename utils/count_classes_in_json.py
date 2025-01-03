import os
import json


def count_classes_in_json(directory):
    # Dictionary to store class counts
    class_counts = {}

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)

            # Load JSON file
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

                # Check and count labels
                for shape in data.get('shapes', []):
                    label = shape.get('label', 'Unknown')
                    class_counts[label] = class_counts.get(label, 0) + 1

    return class_counts


# Directory containing LabelMe JSON files
directory_path = "/Users/antonshever/Desktop/dataset/frame-new"

# Run the script and display the results
class_counts = count_classes_in_json(directory_path)
for class_name, count in class_counts.items():
    print(f"Class '{class_name}': {count} occurrences")
