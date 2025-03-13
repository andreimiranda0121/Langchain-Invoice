import pandas as pd

class DataFrame:
    """
    Defines DataFrame structures for different companies.
    """

    @staticmethod
    def company_a():
        return pd.DataFrame(
            {
                "invoice_no": pd.Series(dtype="str"),
                "po_no": pd.Series(dtype="str"),
                "description": pd.Series(dtype="str"),
                "quantity": pd.Series(dtype="float"),
                "date": pd.Series(dtype="str"),
                "unit_price": pd.Series(dtype="float"),
                "amount": pd.Series(dtype="float"),
                "total": pd.Series(dtype="float"),
            }
        )

    @staticmethod
    def company_b():
        return pd.DataFrame(
            {
                "invoice_no": pd.Series(dtype="str"),
                "po_no": pd.Series(dtype="str"),
                "description": pd.Series(dtype="str"),
                "quantity": pd.Series(dtype="float"),
                "unit_price": pd.Series(dtype="float"),
                "total_cost": pd.Series(dtype="float"),
                "currency": pd.Series(dtype="str"),
                "supplier_email": pd.Series(dtype="str"),
                "supplier_contact": pd.Series(dtype="str"),
            }
        )

    @staticmethod
    def select_dataframe(company_name):
        dataframes = {
            "Company A": DataFrame.company_a,
            "Company B": DataFrame.company_b,
        }
        return dataframes.get(company_name, DataFrame.company_a)()
