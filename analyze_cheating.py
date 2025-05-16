import os
import json
import time
from openai import OpenAI

# Initialize the OpenAI client using the provided API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the structured output schema to force a 1 or 0 output
schema = {
    "type": "object",
    "properties": {
        "output": {
            "type": "integer",
            "enum": [0, 1]
        }
    },
    "required": ["output"]
}

# Define directories containing code files
directories = [
    "SequenceEasyCodes_gpt-4o-mini", "SequenceEasyCodes_gpt-4o", 
    "SequenceHardCodes_gpt-4o-mini", "SequenceHardCodes_gpt-4o",
    "SequenceEasyCodes_o1-mini", "SequenceHardCodes_o1-mini",
    "SequenceEasyCodes_o1-preview", "SequenceHardCodes_o1-preview",
    "SequenceEasyCodes_claude-3-5-sonnet-20241022", "SequenceHardCodes_claude-3-5-sonnet-20241022",
    "SequenceEasyCodes_llama-405b", "SequenceHardCodes_llama-405b",
    "SequenceEasyCodes_llama-70b", "SequenceHardCodes_llama-70b",
    "SequenceEasyCodes_gemini-1.5-flash", "SequenceHardCodes_gemini-1.5-flash",
    "SequenceEasyCodes_gemini-1.5-pro", "SequenceHardCodes_gemini-1.5-pro",
    "SequenceEasyCodes_llama33-70b", "SequenceHardCodes_llama33-70b",
    "SequenceEasyCodes_o1", "SequenceHardCodes_o1",
    #"SequenceEasyCodes_", "SequenceHardCodes_",
]

# Function to process each Python file and save the result
def analyze_code_file(file_path, retries=5, delay=1):
    # Create the output file path (with .cheated extension)
    cheated_file_path = file_path.replace(".py", ".cheated")

    # Check if the .cheated file already exists
    if os.path.exists(cheated_file_path):
        print(f"Skipping {file_path} as .cheated file already exists.")
        return

    # Read the code from the file
    with open(file_path, 'r') as file:
        code = file.read().strip()

    # Create the prompt with the updated content
    prompt = f"""The following piece of code is from a test where the test-taker was asked not to use a look-up table. Instead, the test-taker should have written a code that computes an element in a sequence. In some cases it's OK to have a few items in a look-up table (e.g., the Fibonacci sequence), but it should be considered cheating if the look-up table is unnecessary. If the following piece of code uses a look-up table to cheat, output a 1, otherwise output a 0. Here is the code:\n\n```\n{code}\n```"""

    for attempt in range(retries):
        try:
            # Make the API request with structured output and temperature set to 0
            chat_completion = client.chat.completions.create(
                model="gpt-4o",  # Using the "gpt-4o" model
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # Set temperature to 0
                functions=[
                    {
                        "name": "output",
                        "description": "Returns 1 if the code uses a look-up table, otherwise 0",
                        "parameters": schema
                    }
                ]
            )

            # Correctly access the generated response
            output_value = json.loads(chat_completion.choices[0].message.function_call.arguments)["output"]

            # Write the result (1 or 0) to the .cheated file
            with open(cheated_file_path, 'w') as cheated_file:
                cheated_file.write(str(output_value))

            print(f"Processed {file_path}, result: {output_value}")
            return  # Success, exit the function

        except Exception as e:
            print(f"Error processing {file_path} (Attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to process {file_path} after {retries} attempts.")

# Iterate through all the directories and process each Python file
for directory in directories:
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".py"):
            file_path = os.path.join(directory, filename)
            analyze_code_file(file_path)

