from pathlib import Path
    

BASE_DIR =Path('DATABASE')
PAYMENT_INFO = BASE_DIR / "db.parquet"
NDC_NAMES = BASE_DIR / "ndc_names.parquet"
HCPCS_DESC = BASE_DIR / "hcpcs_desc.parquet"
HOSPITALS = BASE_DIR / "hospital.parquet"
PRICE_PATH = BASE_DIR / 'prices.parquet'
HOSPITAL340B = BASE_DIR / 'hospital340b.parquet'



    