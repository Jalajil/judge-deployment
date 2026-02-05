"""
Fix Saudi-Judge-AWQ config.json for vLLM compatibility.

This script removes the 'scale_dtype' and 'zp_dtype' fields that are 
not supported by older vLLM versions used in RunPod workers.
"""
import requests
import json
import os

MODEL_ID = "Aljalajil/Saudi-Judge-AWQ"
OUTPUT_FILE = "config_fixed.json"

def remove_unsupported_fields(obj):
    """Recursively remove unsupported fields from config."""
    if isinstance(obj, dict):
        # Fields to remove (not supported by RunPod's vLLM version)
        fields_to_remove = ['scale_dtype', 'zp_dtype']
        
        return {
            k: remove_unsupported_fields(v) 
            for k, v in obj.items() 
            if k not in fields_to_remove
        }
    elif isinstance(obj, list):
        return [remove_unsupported_fields(item) for item in obj]
    else:
        return obj

def main():
    print(f"Downloading config.json from {MODEL_ID}...")
    r = requests.get(f'https://huggingface.co/{MODEL_ID}/raw/main/config.json')
    
    if r.status_code != 200:
        print(f"Error: Could not download config.json (status {r.status_code})")
        return
    
    original_config = r.json()
    
    # Fix the config
    print("Removing unsupported fields (scale_dtype, zp_dtype)...")
    fixed_config = remove_unsupported_fields(original_config)
    
    # Save the fixed config
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixed_config, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Fixed config saved to: {OUTPUT_FILE}")
    print(f"\n{'='*60}")
    print("NEXT STEPS:")
    print("="*60)
    print(f"""
1. Go to: https://huggingface.co/{MODEL_ID}/blob/main/config.json

2. Click the "Edit" button (pencil icon)

3. Replace the entire content with the content from:
   {os.path.abspath(OUTPUT_FILE)}

4. Add commit message: "Fix config for vLLM compatibility"

5. Click "Commit changes to main"

6. Wait 1-2 minutes, then restart your RunPod workers

Or use the Hugging Face CLI:
   huggingface-cli upload {MODEL_ID} {OUTPUT_FILE} config.json
""")

if __name__ == '__main__':
    main()
