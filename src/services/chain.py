import logging
from langchain_google_genai import GoogleGenerativeAI, ChatGoogleGenerativeAI
from src.utils.schema import Schema
from src.utils.template import Template
from dotenv import load_dotenv
from src.database.vector_store import VectorStore
from langchain_openai import ChatOpenAI

logging.basicConfig(level=logging.DEBUG)

class Chaining():
    def __init__(self):
        load_dotenv()
        self.vector = VectorStore()
        self.template = Template()
        self.schema = Schema()
        self.extract_model = GoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3
        )
        self.chat_model = ChatOpenAI(
            model="gpt-4o"
        )

    def estimate_tokens(self, text):
        """Estimate token count using character length (approx 1 token = 4 chars)."""
        return len(text) // 4

    def response(self, file_data, company_name):
        parser = self.schema.create_schema(company_name)
        print(parser)
        template = self.template.extract_template()
        chain = template | self.extract_model | parser

        formatted_prompt = template.format(data=file_data, format_instructions=parser.get_format_instructions())
        input_tokens = self.estimate_tokens(formatted_prompt)

        response = chain.invoke({"data": file_data, "format_instructions": parser.get_format_instructions()})
        output_text = str(response)
        output_tokens = self.estimate_tokens(output_text)
        total_tokens = input_tokens + output_tokens

        print(f"Estimated Input Tokens: {input_tokens}")
        print(f"Estimated Output Tokens: {output_tokens}")
        print(f"Estimated Total Tokens: {total_tokens}")
        logging.debug(f"Response: {response}")

        return response

    def chat_response(self,query):
        context = self.vector.query_vector_store(query)
        template = self.template.chat_template()
        chain = template | self.chat_model
        response = chain.invoke({"query":query, "context": context})
        return response.content