import polars as pl
from config import *
from pathlib import Path
from polars import col as c
import plotly.express as px
import polars.selectors as cs
from dash import dash_table, html
from typing import Dict, List, Union
import dash_mantine_components as dmc
from data_dictionary_table_schema import data_dict_schema
import dash_mantine_components as dmc

def load_parquet(path: Path) -> pl.LazyFrame:
    """
    Load a Parquet file into a Polars DataFrame.
    
    Args:
        path (Path): The path to the Parquet file.
        
    Returns:
        pl.DataFrame: The loaded DataFrame.
    """
    return pl.scan_parquet(path)

def to_date_format():
    return cs.contains("retrieved").str.to_date("%Y-%m-%dT%H:%M:%S%.3fZ")

payment_info = (
    load_parquet(PAYMENT_INFO)
    .with_columns(pl.when(c.drug_unit_of_measurement.is_null() | (c.drug_unit_of_measurement == 0))
                .then(1.0)
                .otherwise(c.drug_unit_of_measurement)
                .alias('drug_unit_of_measurement'))
)
ndc_data = load_parquet(NDC_NAMES)
# J8499 is blacket non chemo drug - remove from selection option
hcpcs_data = load_parquet(HCPCS_DESC).filter(~c.hcpcs.is_in(['J8499']))
hospitals_data = load_parquet(HOSPITALS).with_columns(
    pl.col(['lat','long']).cast(pl.Float64),
    to_date_format()
)

hospital340B = load_parquet(HOSPITAL340B)

# function to add 340b flag to lazyframe on hospital unique_id
def add_340b_info(df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Add a 340B flag to the hospital data based on the hospital340B dataset.
    
    Args:
        df: Input LazyFrame containing hospital data
    
    Returns:
        LazyFrame with an additional 'is_340b' column
    """
    # get list of 340B hospitals
    return (
        df
        .join(hospital340B.select(c.unique_id, c.program_type_long), on='unique_id', how='left')
        .with_columns(c.program_type_long.is_not_null().alias('is_340b'))
    )



# add 340b flag to hospitals_data
hospitals_data = add_340b_info(hospitals_data)

money_col = [
    'standard_charge_discounted_cash',
    'standard_charge_negotiated_dollar',
    'standard_charge_gross'
]

def get_hcpcs_desc_list() -> list:
    """
    Get a list of unique HCPCS descriptions.
    
    Returns:
        list: A list of unique HCPCS descriptions.
    """
    return hcpcs_data.select(c("hcpcs_desc")).unique().sort('hcpcs_desc').collect().to_series().to_list()

def get_product_list() -> list:
    """
    Get a list of unique product names.
    
    Returns:
        list: A list of unique product names.
    """
    return ndc_data.select(c("product")).unique().sort('product').collect().to_series().to_list()

# function that accepts hcpcs_desc and returns hcpcs code
def get_hcpcs_code(hcpcs_desc: str) -> str:
    """
    Get the HCPCS code for a given description.
    
    Args:
        hcpcs_desc (str): The HCPCS description.
        
    Returns:
        str: The corresponding HCPCS code.
    """
    return hcpcs_data.filter(c("hcpcs_desc") == hcpcs_desc).select(c("hcpcs")).collect().item()

def get_ndc_codes(product: str) -> list:
    """
    Get the NDC codes for a given product.
    
    Args:
        product (str): The product name.
        
    Returns:
        list: The corresponding NDC codes.
    """
    return ndc_data.filter(c("product") == product).select(c("ndc")).collect().to_series().to_list()

def filter_payment_info(how: str, value: str, data: pl.LazyFrame = payment_info) -> pl.LazyFrame:
    # check if how is in ["hcpcs", "ndc"]
    # if how not in ["hcpcs", "ndc"]:
    #     raise ValueError("how must be either 'hcpcs' or 'ndc'")
    
    if how == "hcpcs":
        return data.filter(c("hcpcs") == get_hcpcs_code(value))
    
    if how == "ndc":
        return data.filter(c("ndc").is_in(get_ndc_codes(value)))
    
    # Fallback: return an empty LazyFrame with the same schema as data
    return data.filter(pl.lit(False))


# add hospital data to grid
def add_hospital_data(data: pl.LazyFrame) -> pl.LazyFrame:
    data = data.join(
        hospitals_data.select(c.unique_id, c.name, c.state, c.beds, c.is_340b, c.lat, c.long, c.retrieved),
        left_on='hospital_unique_id',
        right_on='unique_id'
    )
    return data

def create_price_distribution_plot(df):
    """
    Create a box plot showing price distribution by drug measurement type.
    
    Args:
        df: Polars DataFrame with columns 'drug_type_of_measurement' and 'price_per_unit'
    
    Returns:
        plotly.graph_objects.Figure
    """
    # function to to create x label with hospital count
    def unique_hospital_count() -> pl.Expr:
        return c.name.n_unique().over('drug_type_of_measurement').alias('hospital_count')

    def drug_type_of_measurement_with_hospital_ct() -> pl.Expr:
        return pl.format('{}\n({})', c.drug_type_of_measurement, unique_hospital_count()).alias('drug_type_of_measurement')

    df = (
        df
        #if drug_unit_of_measurement is null or 0 set to 1.0
        .with_columns(c.drug_unit_of_measurement.fill_null(1.0))
        # calculate price per unit
        .group_by(c.name, c.drug_type_of_measurement)
        .agg(
            ((c.standard_charge_negotiated_dollar.mean() / c.drug_unit_of_measurement.mean())).round(2).alias('price_per_unit')
        )
        .with_columns(drug_type_of_measurement_with_hospital_ct())
    )


    fig = px.box(
        df.collect(),
        x='drug_type_of_measurement',
        y='price_per_unit',
        color='drug_type_of_measurement',
        points='all',
        title='Price Distribution by Drug Measurement Type',
        color_discrete_sequence=px.colors.qualitative.Dark2
    )

    # Configure y-axis
    fig.update_yaxes(
        type='log',
        title_text='Price per Unit (USD)',
        tickprefix="$",
        tickformat=",.2f",
        gridcolor='#E2E2E2',
        title_font=dict(size=16),
        tickfont=dict(size=14)
    )

    # Configure x-axis
    fig.update_xaxes(
        title_text='Drug Type of Measurement',
        gridcolor='#E2E2E2',
        title_font=dict(size=16),
        tickfont=dict(size=14),
        tickangle=0
    )

    # Update box and point styling
    fig.update_traces(
        marker=dict(
            size=6,
            opacity=0.7,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        line=dict(width=1.5),
        boxmean=True,  # Show mean as a dashed line
        jitter=0.3,    # Spread out the points
        whiskerwidth=0.7,
        boxpoints=False  # Show only outlier points
    )    # Update layout
    fig.update_layout(
        template='plotly_white',
        font_family="Segoe UI, Arial, sans-serif",
        title=dict(
            text='Price Distribution by Drug Measurement Type<br><span style="font-size:14px;color:#666">Negotiated Prices per Unit</span>',
            x=0.5,  # Center the title
            xanchor='center',
            y=0.95,
            font=dict(size=20)
        ),
        showlegend=False,
        autosize=True,
        height=500,
        # Increased bottom margin
                    plot_bgcolor='white',
                    annotations=[
                            dict(
                                    text=      "1. The y-axis uses a logarithmic scale. Each box represents the interquartile range (25th–75th percentile); whiskers extend to 1.5× IQR.<br>"
                                                "2. The number in parentheses after each unit on the x-axis indicates the count of hospitals reporting prices in that unit.",
                                    showarrow=False,
                                    xref="paper",
                                    yref="paper",
                                    x=0,
                                    y=-0.26,  # Moved note further down
                font=dict(size=10, color="#666"),
                align="left"
            )
        ]
    )

    # Add thousands separators to hover text
    fig.update_traces(
        hovertemplate="<br>".join([
            "Drug Type: %{x}",
            "Price: $%{y:,.2f}",
            "Mean: $%{mean:,.2f}",
            "<extra></extra>"
        ])
    )
    
    return fig

def create_map_visualization(data: pl.LazyFrame):
    """
    Create a geographical visualization of hospital price distribution.

    Args:
        data: LazyFrame containing hospital data with required columns:
              hospital_unique_id, standard_charge_negotiated_dollar, lat, long, name, state

    Returns:
        plotly.graph_objects.Figure: The configured map visualization
    """
    # Aggregate the data and remove null values
    map_data = (
        data
        .group_by(['hospital_unique_id'])
        .agg(c.standard_charge_negotiated_dollar.mean())
        .pipe(add_hospital_data)
        .filter(c.standard_charge_negotiated_dollar.is_not_null())
        .with_columns([
            pl.min('standard_charge_negotiated_dollar').alias('price_min'),
            pl.max('standard_charge_negotiated_dollar').alias('price_max'),            ((pl.col('standard_charge_negotiated_dollar') - pl.min('standard_charge_negotiated_dollar')) / 
             (pl.max('standard_charge_negotiated_dollar') - pl.min('standard_charge_negotiated_dollar')) * 26 + 4)
            .alias('marker_size')
        ]
        )
        # set default marker size to 4.0 if null
        .with_columns(c.marker_size.fill_nan(4.0))  # Fill null sizes with a default value
        .collect()
    )
    
    # calculate 5th and 95th percentile for color scale
    lower_bound = map_data.select(c.standard_charge_negotiated_dollar.quantile(0.05)).item()
    upper_bound = map_data.select(c.standard_charge_negotiated_dollar.quantile(0.95)).item()

    # Create map visualization
    fig = px.scatter_geo(
        data_frame=map_data,
        lat='lat',
        lon='long',
        size='marker_size',  # Use the scaled size column
        color='standard_charge_negotiated_dollar',
        scope='usa',
        custom_data=['name', 'state', 'standard_charge_negotiated_dollar', 'hospital_unique_id'],
        title='Hospital Price Distribution Across USA',
        color_continuous_scale='Viridis',
        range_color=[lower_bound, upper_bound],  # Set color range based on percentiles
        height=500,
    )

    # Update hover template
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>%{customdata[0]}</b>",
            "State: %{customdata[1]}",
            "Average Price: $%{customdata[2]:,.2f}",
            "<extra></extra>"
        ]),

    )


    # Update layout
    fig.update_layout(
        title=dict(
            text='Hospital Price Distribution Across USA<br><span style="font-size:12px;">Circle size and color indicate average negotiated price</span>',
            x=0.01,
            font=dict(size=18, color='#2c3e50')
        ),
        paper_bgcolor='white',
        geo=dict(
            showland=True,
            showlakes=True,
            showcountries=True,
            showsubunits=True,
            landcolor='rgb(250, 250, 250)',
            subunitcolor='rgb(217, 217, 217)',
            countrycolor='rgb(217, 217, 217)',
            lakecolor='rgb(255, 255, 255)',
            bgcolor='white',
            projection_scale=1.1
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(
            orientation='h',
            thickness=15,
            len=0.7,
            title=dict(
                text='Average Negotiated Price ($)',
                side='bottom',
                font=dict(size=12)
            ),
            y=-0.15,
            tickformat='$,.0f'
        )
    )
    
    return fig

def schema_for_fig_data():
    """
    Define the schema for the DataFrame used in the visualization.
    
    Returns:
        dict: A dictionary defining the schema for the DataFrame.
    """
    return {
        'description': pl.String,   
        'ndc': pl.String,
        'hcpcs': pl.String,
        'setting': pl.String,
        'drug_unit_of_measurement': pl.Int64,
        'drug_type_of_measurement': pl.String,
        'payer_name': pl.String,
        'plan_name': pl.String,
        'standard_charge_gross': pl.Float64,
        'standard_charge_discounted_cash': pl.Float64,
        'standard_charge_negotiated_dollar': pl.Float64,
        'standard_charge_methodology': pl.String,
        'standard_charge_negotiated_percentage': pl.Float64,
        'calculated_negotiated_dollars': pl.Boolean,
        'hospital_unique_id': pl.String,
        'mapped_plan_name': pl.String,
        'mapped_lob_name': pl.String,
        'name': pl.String,
        'state': pl.String,
        'beds': pl.Int32,
        'lat': pl.Float64,
        'long': pl.Float64
    }

def load_price_data(path: Path = PRICE_PATH) -> pl.LazyFrame:
    """
    Load price data from a parquet file.
    
    Args:
        path: Path to the parquet file.

    Returns:
        LazyFrame containing the price data.
    """
    return pl.scan_parquet(path)

def filter_price_data(value: str, how: str) -> pl.LazyFrame:
    # how either 'ndc' or 'hcpcs'
    data = load_price_data()
    if how == 'ndc':
        return data.filter(c.product == value)
    elif how == 'hcpcs':
        return data.filter(c.hcpcs == value)
    else:
        raise ValueError("Invalid filter type. Use 'ndc' or 'hcpcs'.")


def create_hcpcs_description(df: pl.DataFrame) -> pl.DataFrame:
    """Create a combined HCPCS description column."""
    return df.with_columns(
        pl.format('{} - {} ({})', 
                 c.hcpcs, 
                 c.asp_desc, 
                 c.asp_dosage).alias('hcpcs_desc')
    )

def summarize_prices(df: pl.LazyFrame) -> pl.LazyFrame:
    """
    Summarize pricing data by creating a normalized view of ASP and product prices.

    Args:
        df: Input LazyFrame containing pricing data
    Returns:
        LazyFrame with normalized price summaries
    """
    # Prepare HCPCS description
    df = df.with_columns(
        pl.format('{} - {} ({})', c.hcpcs, c.asp_desc, c.asp_dosage).alias('hcpcs_desc')
    )

    # Group and aggregate numeric columns
    processed_data = (
        df
        .group_by(['product', 'hcpcs_desc', 'hcpcs'])
        .agg(cs.numeric().mean().round(2))
    )

    # ASP summary
    asp_prices = (
        processed_data
        .select([
            c.hcpcs_desc.alias('desc'),
            pl.lit('asp').alias('price_type'),
            c.asp.alias('amount')
        ])
        .unique()
        .filter(c.amount.is_not_null())
    )

    # Product price summary
    excluded_cols = {'hcpcs_desc', 'asp', 'hcpcs', 'product'}
    product_prices = (
        processed_data
        .select(['product'] + [
            col for col in processed_data.collect_schema().names() 
            if col not in excluded_cols
        ])
        .rename({'product': 'desc'})
        .unpivot(
            index='desc',
            variable_name='price_type',
            value_name='amount'
        )
        .filter(c.amount.is_not_null())
    )

    return pl.concat([asp_prices, product_prices]).lazy()

def fetch_summarized_prices(how: str, value: str) -> pl.LazyFrame:
    """
    Fetch and summarize prices based on the specified filter.
    
    Args:
        how: Filter type ('ndc' or 'hcpcs')
        value: Value to filter by

    Returns:
        LazyFrame containing the summarized prices
    """
    filtered_data = filter_price_data(value, how)
    return summarize_prices(filtered_data)


def create_mantine_dictionary():
    """
    Create a Mantine-styled data dictionary component.

    Returns:
        dmc.Card: A Dash Mantine component containing the data dictionary
    """
    

    data = data_dict_schema
    
    table = dmc.Box([
        html.Table([
            # Header
            html.Thead(
                html.Tr([
                    html.Th("Column Name", className="dict-header"),
                    html.Th("Data Type", className="dict-header"),
                    html.Th("Description", className="dict-header")
                ])
            ),
            # Body
            html.Tbody([
                html.Tr([
                    html.Td(row["column"], className="dict-cell"),
                    html.Td(row["dtype"], className="dict-cell"),
                    html.Td(row["desc"], className="dict-cell")
                ]) for row in data
            ])
        ], className="dict-table")
    ], className="dict-container")

    return dmc.Box(
        children=[
            dmc.Text("Data Dictionary", className='section-title'),
            table
        ],

    )

def no_price_table():
    return dmc.Box(
            html.Table(
                [html.Tr([
                    html.Td("No pricing information available.", colSpan=3, className="no-prices-row")
                ])]
            ),
            className="price-table-section"
        )


def create_html_table(data):
    """
    Creates an HTML table from a dictionary of data using Dash's html components.

    Args:
        data (dict): A dictionary where each key is a column name and each value is a list of column values.

    Returns:
        dash_html_components.Div: A Dash HTML Div containing the generated table with a header row and data rows.

    Example:
        data = {
            "Name": ["Alice", "Bob"],
            "Age": [30, 25]
        }
        table_div = create_html_table(data)
    """
    return dmc.Box(
            html.Table(
                # Header
                [html.Tr([html.Th(col) for col in data.keys()])] +
                # Body
                [html.Tr([html.Td(data[col][i]) for col in data.keys()]) for i in range(len(data[list(data.keys())[0]]))]
            ),
            className="price-table-section"
        )

# function to get hcpcs code from description
def get_hcpcs_code_from_desc(hcpcs_desc: str) -> str:
    """
    Get the HCPCS code for a given description.
    
    Args:
        hcpcs_desc (str): The HCPCS description.
        
    Returns:
        str: The corresponding HCPCS code.
    """
    return hcpcs_data.filter(c("hcpcs_desc") == hcpcs_desc).select(c("hcpcs")).collect().item()


    

if __name__ == "__main__":
    pass
    #hospital340B.collect().glimpse()
    #hospitals_data.collect().head(1).glimpse()
    #fetch_summarized_prices('hcpcs','J1817').collect().glimpse()

