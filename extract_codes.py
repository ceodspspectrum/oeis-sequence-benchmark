import os
import json

# Define the directory mappings from Responses to Codes
directory_mappings = {
    'SequenceEasyResponses_gpt-4o-mini': 'SequenceEasyCodes_gpt-4o-mini',
    'SequenceEasyResponses_o1-mini': 'SequenceEasyCodes_o1-mini',
    'SequenceHardResponses_gpt-4o': 'SequenceHardCodes_gpt-4o',
    'SequenceEasyResponses_gpt-4o': 'SequenceEasyCodes_gpt-4o',
    'SequenceHardResponses_gpt-4o-mini': 'SequenceHardCodes_gpt-4o-mini',
    'SequenceHardResponses_o1-mini': 'SequenceHardCodes_o1-mini',
    'SequenceEasyResponses_claude-3-5-sonnet-20241022': 'SequenceEasyCodes_claude-3-5-sonnet-20241022',
    'SequenceHardResponses_claude-3-5-sonnet-20241022': 'SequenceHardCodes_claude-3-5-sonnet-20241022',
    'SequenceEasyResponses_llama-405b': 'SequenceEasyCodes_llama-405b',
    'SequenceHardResponses_llama-405b': 'SequenceHardCodes_llama-405b',
    'SequenceEasyResponses_llama-70b': 'SequenceEasyCodes_llama-70b',
    'SequenceHardResponses_llama-70b': 'SequenceHardCodes_llama-70b',
    'SequenceHardResponses_o1-preview': 'SequenceHardCodes_o1-preview',
    'SequenceEasyResponses_o1-preview': 'SequenceEasyCodes_o1-preview',
    'SequenceEasyResponses_gemini-1.5-flash': 'SequenceEasyCodes_gemini-1.5-flash',
    'SequenceHardResponses_gemini-1.5-flash': 'SequenceHardCodes_gemini-1.5-flash',
    'SequenceEasyResponses_gemini-1.5-pro': 'SequenceEasyCodes_gemini-1.5-pro',
    'SequenceHardResponses_gemini-1.5-pro': 'SequenceHardCodes_gemini-1.5-pro',
    'SequenceEasyResponses_gpt-3.5-turbo-1106': 'SequenceEasyCodes_gpt-3.5-turbo-1106',
    'SequenceHardResponses_gpt-3.5-turbo-1106': 'SequenceHardCodes_gpt-3.5-turbo-1106',
    'SequenceEasyResponses_llama33-70b': 'SequenceEasyCodes_llama33-70b',
    'SequenceHardResponses_llama33-70b': 'SequenceHardCodes_llama33-70b',
    'SequenceEasyResponses_o1': 'SequenceEasyCodes_o1',
    'SequenceHardResponses_o1': 'SequenceHardCodes_o1',
    #'SequenceEasyResponses_': 'SequenceEasyCodes_',
    #'SequenceHardResponses_': 'SequenceHardCodes_',
}

# Create the corresponding code directories if they don't exist
for response_dir, code_dir in directory_mappings.items():
    if not os.path.exists(code_dir):
        os.makedirs(code_dir)

# Function to extract the last code block inside triple backticks
def extract_code(response):
    parts = response.split('```')
    code_block = ""
    if len(parts) >= 3:  # Ensure there are enough parts to contain a valid code block
        code_block = parts[-2].strip()  # Get the last code block (even index)
        
        # If it starts with "python", strip it
        if code_block.startswith("python"):
            code_block = code_block[len("python"):].strip()
    else:
        # If no triple backticks are found, return the entire response as the code block
        code_block = response.strip()
        
    return code_block

# Process each directory
for response_dir, code_dir in directory_mappings.items():
    for filename in os.listdir(response_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(response_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                response = data.get('response', '')
                
                # Extract the code from the response
                code = extract_code(response)

                # Print full response and extracted code
                print(f"Full response from {filename}:\n{response}\n")
                print(f"Extracted code from {filename}:\n{code}\n{'-'*80}\n")
                
                # Create a new filename for the Python file
                code_filename = filename.replace('.json', '.py')
                code_file_path = os.path.join(code_dir, code_filename)
                
                # Write the extracted code to the Python file
                with open(code_file_path, 'w', encoding='utf-8') as code_file:
                    code_file.write(code)

print("Code extraction and file creation complete.")
