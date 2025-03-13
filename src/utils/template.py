from langchain_core.prompts import ChatPromptTemplate


class Template():

    def extract_template(self):
        return ChatPromptTemplate.from_template(
            """You are an AI that extracts structured invoice details.

            Extract all line items from this invoice and format them in structured JSON.
            Each item should be extracted separately, and the output should be a list of dictionaries.

            **Important Instructions:**
            - If an item has both `Quantity = 0` and `Amount = 0`, **DO NOT include it** in the output.
            - If the value is Null just return an empty string
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
                ("system", """You are an intelligent assistant specialized in processing and answering queries related to invoices and purchase orders.  
                Use the following context to provide accurate responses:  
                {context}  
                Don't response in a jason if the format needed to be a table then create a table based on the context.
                If the query is unrelated to invoices or POs, politely inform the user that you can only assist with invoice-related queries.
                """),
                ("human", "{query}")
            ]
        )
