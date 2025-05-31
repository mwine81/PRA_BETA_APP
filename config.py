from pathlib import Path
import shutil

BASE_DIR =Path('DATABASE')
PAYMENT_INFO = BASE_DIR / "db.parquet"
NDC_NAMES = BASE_DIR / "ndc_names.parquet"
HCPCS_DESC = BASE_DIR / "hcpcs_desc.parquet"
HOSPITALS = BASE_DIR / "hospital.parquet"
PRICE_PATH = BASE_DIR / 'prices.parquet'
HOSPITAL340B = BASE_DIR / 'hospital340B.parquet'


def update_files():
    FROM_DIR = Path(r'C:\Users\mwine\Projects\MAY_2025\dev\HOSPITAL_APP')
    TO = Path().cwd()
    shutil.copy(FROM_DIR / 'app4.py', TO / 'app.py')
    shutil.copy(FROM_DIR / 'assets/custom.css', TO / 'assets/custom.css')
    shutil.copy(FROM_DIR / 'ag_grid_def.py', TO / 'ag_grid_def.py')
    shutil.copy(FROM_DIR / 'data_dictionary_table_schema.py', TO / 'data_dictionary_table_schema.py')
    shutil.copy(FROM_DIR / 'helpers.py', TO / 'helpers.py')

if __name__ == "__main__":
    update_files()
    print("Files updated successfully.")