import re
from pathlib import Path

def parse_cards_from_file(input_file: str) -> list:
    """Parses a single text file and returns a list of flashcard data."""
    input_path = Path(input_file)
    
    try:
        text = input_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        return []

    tag = input_path.stem
    # Split the entire file into question/answer sections
    sections = text.split("Accepted Answers:")

    if len(sections) < 2:
        print(f"Warning: Could not parse {input_file}. Ensure it contains 'Accepted Answers:' separators.")
        return []

    qa_pairs = []

    for i in range(len(sections) - 1):
        question_block = sections[i]
        answer_block = sections[i+1]

        # --- Extract the Answer ---
        potential_answer_lines = answer_block.strip().split('\n')
        answer = ""
        for line in potential_answer_lines:
            cleaned_line = line.strip()
            if cleaned_line:
                answer = cleaned_line
                break
        
        # --- Clean up the Question Block ---
        # Remove irrelevant markers like score, points, and correctness confirmation
        if '1 point' in question_block:
            question_block = question_block.split('1 point')[-1]
        
        question_block = re.sub(r'(Yes|No), the answer is.*?Score:\s*\d', '', question_block, flags=re.DOTALL | re.IGNORECASE)
        
        # --- Identify Question vs. Options ---
        # Get all non-empty lines from the cleaned block
        all_lines = [line.strip() for line in question_block.strip().split('\n') if line.strip()]

        # Based on your rule: the last 4 lines are always the options
        if len(all_lines) >= 5: # At least 1 line for the question and 4 for options
            option_parts = all_lines[-4:]
            question_lines = all_lines[:-4]
            question_text = ' '.join(question_lines)
        else:
            # Fallback for any unexpected format
            question_text = ' '.join(all_lines)
            option_parts = []
            if all_lines:
                print(f"Warning: Could not parse options in {input_file} for a question starting with '{all_lines[0]}'")

        
        # --- Format and Combine for the Anki Card ---
        full_question = question_text
        if option_parts:
            enumerated_options = []
            for idx, option in enumerate(option_parts):
                label = f"{chr(97 + idx)})" # a), b), c)...
                enumerated_options.append(f"{label} {option}")

            # Use HTML <br> for new lines in Anki
            formatted_options = "<br>".join(enumerated_options)
            full_question += f"<br><br>{formatted_options}"

        if full_question and answer:
            qa_pairs.append((full_question, answer, tag))

    return qa_pairs


if __name__ == "__main__":
    all_flashcards = []
    
    # Loop from 1 to 10 to generate filenames week01.txt, week02.txt, etc.
    for i in range(1, 12):
        filename = f"week{i:02d}.txt"
        input_path = Path(filename)
        
        if input_path.is_file():
            print(f"Processing {filename}...")
            cards_from_file = parse_cards_from_file(filename)
            all_flashcards.extend(cards_from_file)
        else:
            # This is not an error, just lets you know which files were not found
            print(f"Skipping {filename} as it was not found.")

    # --- Write the combined CSV file ---
    if all_flashcards:
        output_filename = "anki_all_weeks.csv"
        output_path = Path(output_filename)
        
        try:
            with output_path.open('w', encoding='utf-8') as f:
                for q, a, tag in all_flashcards:
                    # Escape double quotes for CSV compatibility
                    q_cleaned = q.replace('"', '""')
                    a_cleaned = a.replace('"', '""')
                    f.write(f'"{q_cleaned}";"{a_cleaned}";"{tag}"\n')
            
            print(f"\nSuccess! Created {len(all_flashcards)} flashcards in '{output_filename}'.")
            print("This file contains cards from all processed week*.txt files.")
            print("\nTo import into Anki:")
            print(f"1. Open Anki and go to File > Import.")
            print(f"2. Select the '{output_filename}' file.")
            print("3. In the import dialog, set 'Fields separated by:' to 'Semicolon'.")
            print("4. Map field 1 to 'Front', field 2 to 'Back', and field 3 to 'Tags'.")
            print("5. IMPORTANT: Make sure to check the 'Allow HTML in fields' option.")
            print("6. Click Import.")

        except Exception as e:
            print(f"Error writing to output file: {e}")
    else:
        print("\nNo flashcards were generated. Please make sure your week*.txt files are in the same directory.")

