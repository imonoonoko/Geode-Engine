
import json
import os

PATH = "memory_data/brain_concepts.json"

def clean():
    if not os.path.exists(PATH):
        print("No concepts file.")
        return

    with open(PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    concepts = data.get("concepts", {})
    to_delete = []

    print(f"Total concepts: {len(concepts)}")
    
    for key in concepts.keys():
        if len(key) > 15:
            print(f"Detecting junk key: {key}")
            to_delete.append(key)
        if "カナメ" in key and len(key) > 5:
             print(f"Detecting target junk: {key}")
             to_delete.append(key)

    for key in to_delete:
        del concepts[key]
        print(f"Deleted: {key}")
    
    data["concepts"] = concepts
    
    with open(PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    print("Concepts cleaned.")

if __name__ == "__main__":
    clean()
