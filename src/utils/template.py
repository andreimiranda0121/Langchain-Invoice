from langchain_core.prompts import ChatPromptTemplate


class Template():

    def extract_template(self):
        return ChatPromptTemplate.from_template(
            """You are an AI that extracts structured invoice details.

            Extract all line items from this invoice and format them in structured JSON.
            Each item should be extracted separately, and the output should be a list of dictionaries.

            **Important Instructions:**
            - If an item has both `Quantity = 0` and `Amount = 0`, **DO NOT include it** in the output.
            - Ensure that the extracted items are in JSON format.
            - Return all extracted items as a **list of dictionaries**.
            - Make all of the date format like this YYYY-MM-DD
            {format_instructions}

            **Invoice Data:**
            {data}
            """
        )
    
    def chat_template(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", """Youre an Intelligent chatbot that answers users query based on the """),
                ("human", "{query}")
            ]
        )