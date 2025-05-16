import os
import json
from openai import OpenAI

# Initialize the OpenAI client using the provided API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the categories for prompts and responses
categories = ["Easy", "Hard"]

# Define the models to be used
models = ["gpt-4o", "gpt-4o-mini", "o1-mini", "o1-preview", "gpt-3.5-turbo-1106", "o1"]

# Loop over both "Easy" and "Hard" categories
for category in categories:
    # Loop over each model
    for model in models:
        # Set the prompt and response directories based on the category and model
        prompt_directory = f"Sequence{category}Prompts/"
        response_directory = f"Sequence{category}Responses_{model}/"

        # Ensure the response directory exists
        if not os.path.exists(response_directory):
            os.makedirs(response_directory)

        # Iterate over all the .txt files in the prompt directory
        for filename in sorted(os.listdir(prompt_directory)):
            if filename.endswith(".txt"):
                file_path = os.path.join(prompt_directory, filename)

                # Read the content of the file (prompt)
                with open(file_path, 'r') as file:
                    prompt = file.read().strip()

                # Determine the path where the response will be stored
                response_file_path = os.path.join(response_directory, filename.replace(".txt", ".json"))

                # Check if the response has already been saved (cache)
                if os.path.exists(response_file_path):
                    print(f"Loaded cached response for {filename} in {category} using {model}:")
                    with open(response_file_path, 'r') as response_file:
                        cached_response = json.load(response_file)
                        print(f"Cached response: {cached_response['response']}\n")
                else:
                    # If not cached, make the API request using the correct API method
                    try:
                        # Create a chat completion using OpenAI API with the specified model
                        chat_completion = client.chat.completions.create(
                            model=model,  # Use the model in the loop
                            messages=[{"role": "user", "content": prompt}],
                        )

                        # Correctly access the generated response
                        generated_text = chat_completion.choices[0].message.content.strip()

                        # Store the result in a JSON file
                        result_data = {
                            "prompt": prompt,
                            "response": generated_text
                        }

                        # Write the result to a JSON file in the response directory
                        with open(response_file_path, 'w') as response_file:
                            json.dump(result_data, response_file, indent=4)

                        # Print the result
                        print(f"Prompt from {filename} in {category} using {model}:")
                        print(f"Generated response: {generated_text}\n")

                    except Exception as e:
                        print(f"Error processing {filename} in {category} using {model}: {str(e)}")
