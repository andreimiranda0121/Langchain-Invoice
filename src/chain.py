from langchain_google_genai import GoogleGenerativeAI
from src.schema import Schema
from src.template import Template
from dotenv import load_dotenv


class Chaining():
    def __init__(self):
        load_dotenv()
        self.template = Template()
        self.schema = Schema()
        self.model = GoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3
        )

    def estimate_tokens(self, text):
        #Estimate token count using character length (approx 1 token = 4 chars)
        return len(text) // 4

    def response(self, file_data):
        
        parser = self.schema.create_schema()
        template = self.template.extract_template()
        chain = template | self.model | parser

        formatted_prompt = template.format(data=file_data,format_instructions=parser.get_format_instructions())

        input_tokens = self.estimate_tokens(formatted_prompt)

        response = chain.invoke({"data": file_data, "format_instructions":parser.get_format_instructions()})

        output_text = str(response)

        output_tokens = self.estimate_tokens(output_text)

        total_tokens = input_tokens + output_tokens

        print(f"Estimated Input Tokens: {input_tokens}")
        print(f"Estimated Output Tokens: {output_tokens}")
        print(f"Estimated Total Tokens: {total_tokens}")
        print(response)
        return response
