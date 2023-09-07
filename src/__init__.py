import os.path

import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
import pytesseract
from PIL import Image
import openai
import json

# Set your OpenAI API key here
openai.api_key = ""
prompt_common_text = """
Return result in JSON format without any explanation.
Output:
{}
"""


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    doc.close()
    return text


def extract_text_from_pdf_with_image(pdf_path):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        # Initialize an empty string to store extracted text
        extracted_text = ""

        # Iterate through each page in the PDF
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]

            # Extract the image from the page as a PIL image
            pix = page.get_pixmap()
            img_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Perform OCR on the image to extract text
            text = pytesseract.image_to_string(img_pil, lang='eng')

            # Append the extracted text to the result
            extracted_text += text

        # Close the PDF file
        pdf_document.close()

        return extracted_text
    except Exception as e:
        return str(e)


def generate_openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": ""
            }
        ],
        temperature=0,
        max_tokens=2048
    )
    return response.choices[0].message.content


def generate_prompt_based_on_file(file_name):
    prompt = {
        "LNG_1_QatarGas": "Extract fields: \"Buyer\", \"Seller\", \"Terms of Delivery\" and \"Discharge Location\", "
                          "\"Quantity\", \"Price\", \"Scheduled Unloading Window\".",
        "LNG_1_QatarGas_IMG": "Extract fields: \"Buyer\", \"Seller\", \"Terms of Delivery\" and \"Discharge Location\","
                              "\"Quantity\", \"Price\", \"Scheduled Unloading Window\".",
        "LNG_3_Gunvor_TAR": "Extract fields: \"Buyer\", \"Seller\", \"Time\", and \"Role\".",
        "LNG_3_Gunvor_TVB": "Extract fields: \"Buyer\", \"Seller\", \"Pricing Period\" and \"Quantity\".",
        "ExternalEmail_SpreadTrade_Structured": "Extract fields from leg 1 and leg 2: \"Buyer\", \"Seller\", "
                                                "\"Delivery Point\", \"Price\" and \"Quantity\".",
        "ExternalEmail_GME_Structured": "Extract fields: \"Date\", \"Price\" and \"Quantity\".",
        "ExternalEmail_GME_Structured_IMG": "Extract fields: \"Date\", \"Price\" and \"Quantity\".",
        "ExternalEmail_PSV_Structured": "Extract fields: \"Buyer\", \"Seller\", \"Period\", \"Delivery Point\", "
                                        "\"Price\" and \"Quantity\".",
        "ExternalEmail_PSV_Structured_WrongSeller": "Extract fields: \"Buyer\", \"Seller\", \"Period\", \"Delivery "
                                                    "Point\", \"Price\" and \"Quantity\".",
        "ExternalEmail_Unstructured": "Extract fields: \"Buyer\", \"Seller\", \"Period\", \"Delivery Point\", "
                                      "\"Price\" and \"Quantity\".",
        "ExternalEmail_Unstructured_Italian": "Extract fields: \"Buyer\", \"Seller\", \"Period\", \"Delivery Point\", "
                                      "\"Price\" and \"Quantity\"."
    }

    return prompt.get(file_name)


def main():
    # Create a tkinter root window (it won't be shown)
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open a file dialog for the user to select a file
    file_path = filedialog.askopenfilename(title="Select a file")
    file_name = ""
    if file_path:
        try:
            # Open the selected file for reading
            with open(file_path, 'r') as file:
                file_name_with_extension = os.path.basename(file_path)
                # Split the file name and extension
                file_name, file_extension = os.path.splitext(file_name_with_extension)
                print(f"\nFile Name: {file_name}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("No file selected.")

    prompt = generate_prompt_based_on_file(file_name) + prompt_common_text

    #print(f"\nPrompt: {prompt}")

    if 'IMG' in file_name:
        complete_prompt = prompt.format(extract_text_from_pdf_with_image(file_path))
    else:
        complete_prompt = prompt.format(extract_text_from_pdf(file_path))

    print(f"\nPrompt: {complete_prompt}")

    response = generate_openai_response(complete_prompt)
    output = json.loads(response)

    print(f"\nTrade Attributes: {response}")


if __name__ == "__main__":
    main()
