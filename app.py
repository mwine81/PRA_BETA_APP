import dash_mantine_components as dmc
from dash import Dash, html, dcc, callback, Output, Input, State, get_asset_url, no_update, callback_context
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
from dash_iconify import DashIconify
import polars as pl
from polars import col as c

# Local imports
from helpers import (
    get_hcpcs_desc_list, get_product_list, filter_payment_info, add_hospital_data,
    fetch_summarized_prices, schema_for_fig_data, create_map_visualization,
    create_price_distribution_plot, create_mantine_dictionary, hospitals_data,
    create_html_table, no_price_table, get_hcpcs_code_from_desc
)
from ag_grid_def import columnDefs, defaultColDef, dashGridOptions

# Initialize the app
app = Dash(__name__)


class UIComponents:
    """UI component factory for better organization"""
    
    @staticmethod
    def create_toggle_switch():
        """Create the HCPCS/NDC toggle switch"""
        return dmc.Box([
            dmc.Group([
                dmc.Switch(id="switch-toggle", checked=True),
                dmc.Box(id="switch-text"),
            ])
        ])
    
    @staticmethod
    def create_dropdown():
        """Create the product selection dropdown"""
        return dmc.Box([
            dmc.Select(
                id='selection-dropdown',
                searchable=True,
                placeholder="Select a product or HCPCS..."
            )
        ], className='dropdown-container')
    
    @staticmethod
    def create_control_buttons():
        """Create control buttons"""
        return dmc.Stack([
            dmc.Button(
                "Toggle Price Table", 
                id="price-collapse-btn", 
                n_clicks=0, 
                variant='outline',
                leftSection=DashIconify(icon="mdi:table-eye", width=16),
                color='blue'
            ),
            dmc.Button(
                "Toggle Data Grid", 
                id="collapse-btn", 
                n_clicks=0, 
                variant='outline',
                leftSection=DashIconify(icon="mdi:grid", width=16),
                color='blue'
            ),
            dmc.Button(
                "Export CSV", 
                id="csv-button", 
                n_clicks=0, 
                variant='filled',
                leftSection=DashIconify(icon="mdi:download", width=16),
                color='green'
            ),
            dmc.Button(
                "View Schema", 
                id="schema-btn", 
                n_clicks=0, 
                variant='outline',
                leftSection=DashIconify(icon="mdi:database-eye", width=16),
                color='violet'
            ),
        ], gap='sm')
    
    @staticmethod
    def create_visualizations():
        """Create the graphs grid"""
        return dmc.Grid([
            dmc.GridCol(
                dmc.Card([
                    dmc.Stack([
                        dmc.Group([
                            #dmc.Text("Hospital Map", fw=500, size="sm"),
                            dmc.Button(
                                leftSection=DashIconify(icon="mdi:fullscreen", width=14),
                                children="Expand", 
                                id="expand-map-btn", 
                                n_clicks=0, 
                                variant='light', 
                                size='xs',
                                color='blue'
                            ),
                        ], justify="right", align="center"),
                        dcc.Loading(
                            dcc.Graph(id='map'),
                            type="circle"
                        ),
                    ], gap=0),
                ], shadow='sm', p="sm"),
                span={'base': 12, 'xl': 6} # type: ignore
            ),
            dmc.GridCol(
                dmc.Card([
                    dmc.Stack([
                        dmc.Group([
                            #dmc.Text("Price Distribution", fw=500, size="sm"),
                            dmc.Button(
                                leftSection=DashIconify(icon="mdi:chart-box-outline", width=14),
                                children="Expand", 
                                id="expand-distribution-btn", 
                                n_clicks=0, 
                                variant='light', 
                                size='xs',
                                color='green'
                            ),
                        ], justify="right", align="center"),
                        dcc.Loading(
                            dcc.Graph(id='price-distribution'),
                            type="circle"
                        ),
                    ], gap=0),
                ], shadow='sm', p="sm"),
                span={'base': 12, 'xl': 6} # type: ignore
            ),
        ])
    
    @staticmethod
    def create_charts_section():
        """Create the charts section with professional header"""
        return dmc.Card([
            dmc.Text("Chart Analysis", className='section-title'),
            UIComponents.create_visualizations(),
        ], shadow='sm')
    
    @staticmethod
    def create_price_section():
        """Create the pricing information section"""
        return dmc.Card([
            dmc.Text("Pricing Information", className='section-title'),
            dmc.Text(
                'Click the toggle to expand', 
                size='sm', 
                id='hidden-text-price', 
                className='hidden-text',
                style={'display': 'none'}
            ),
            dmc.Collapse(
                dmc.Box(id='price-info', className='price-info'),
                opened=True, 
                id='price-collapse'
            )
        ], className='pricing-container', shadow='sm')
    
    @staticmethod
    def create_data_grid():
        """Create the data grid section"""
        return dmc.Card([
            dmc.Text("Data Grid", className='section-title'),
            dmc.Text(
                'Click the toggle to expand',
                size='sm', 
                id='hidden-grid-text', 
                className='hidden-text',
                style={'display': 'none'}
            ),
            dmc.Collapse(
                dag.AgGrid(
                    id='grid',
                    className='ag-theme-alpine',
                    columnDefs=columnDefs,
                    defaultColDef=defaultColDef,
                    dashGridOptions=dashGridOptions,
                    csvExportParams={"fileName": "hospital_data.csv"},
                    style={'height': '500px'}
                ),                opened=True, 
                id='collapse-grid'
            )
        ], shadow='sm')
    
    @staticmethod
    def create_navigation():
        """Create the navigation panel"""
        return dmc.Stack([
            dmc.Text('Controls', className='section-title'),
            UIComponents.create_toggle_switch(),
            UIComponents.create_dropdown(),
            UIComponents.create_control_buttons(),
        ], gap='md')
    
    @staticmethod
    def create_footer():
        """Create the footer component"""
        return html.Footer(
            dmc.Box([
                # Main footer content
                dmc.Box([
                    # Left side - PRA branding
                    dmc.Box([
                        dmc.Group([
                            dmc.Image(src=get_asset_url('pra_logo.png'), h=35, className='footer-logo'),
                            dmc.Stack([
                                dmc.Anchor(
                                    dmc.Text("Patient Rights Advocate", className='footer-org-name', fw="bold"),
                                    href="https://www.patientrightsadvocate.org/",
                                    target="_blank",
                                    className='footer-org-link'
                                ),
                                dmc.Text("Empowering Healthcare Transparency", className='footer-mission', size="xs"),
                            ], gap="xs"),
                        ], gap="md", align="center"),
                    ], className='footer-left'),
                    # Copyright bar
                dmc.Box([
                    dmc.Group([
                        dmc.Text("© 2025 Patient Rights Advocate", className='copyright-text', size="xs"),
                        dmc.Text("•", className='separator', size="xs"),
                        dmc.Text("All Rights Reserved", className='rights-text', size="xs"),
                        dmc.Text("•", className='separator', size="xs"),
                        dmc.Anchor(
                            "Privacy Policy",
                            href="https://www.patientrightsadvocate.org/termsofservice",
                            target="_blank",
                            className='footer-link',
                            size="xs"
                        ),
                    ], gap="xs", justify="center"),
                ], className='footer-copyright', visibleFrom="lg"),
                    # Right side - Developer and links
                    dmc.Box([
                        dmc.Stack([
                            dmc.Group([
                                dmc.Text("Developed by", className='footer-dev-label', size="xs"),
                                dmc.Image(src=get_asset_url('3AA-logo-1-stack.jpg'), h=25, className='footer-dev-logo'),
                                dmc.Text("3AxisAdvisors", className='footer-dev-name', fw="bold", size="sm"),
                            ], gap="xs", align="center", justify="center"),
                            
                            dmc.Group([
                                dmc.Anchor(
                                    DashIconify(icon='logos:linkedin-icon', width=18),
                                    href="https://www.linkedin.com/company/patient-rights-advocate/",
                                    className='social-icon', 
                                    target="_blank"
                                ),
                                dmc.Anchor(
                                    DashIconify(icon='logos:x', width=18),
                                    href="https://x.com/PtRightsAdvoc",
                                    className='social-icon', 
                                    target="_blank"
                                ),
                                dmc.Anchor(
                                    DashIconify(icon='logos:facebook', width=18),
                                    href="https://www.facebook.com/thepatientrightsadvocate",
                                    className='social-icon', 
                                    target="_blank"
                                ),
                                dmc.Anchor(
                                    DashIconify(icon='logos:youtube-icon', width=18),
                                    href="https://www.youtube.com/channel/UCN7j6idxar-akDLDzVWD46Q",
                                    className='social-icon', 
                                    target="_blank"
                                ),
                            ], gap="sm", justify="center"),
                        ], gap="xs", align="center"),
                    ], className='footer-right', visibleFrom="lg"),
                ], className='footer-main'),
                
                
            ], className='footer-container')
        )


# Create modals
schema_modal = dmc.Modal(
    id="schema-modal",
    centered=True,
    size="xl",
    children=create_mantine_dictionary(),
    shadow='lg',
)

hospital_modal = dmc.Modal(
    id="hospital-info-modal",
    centered=True,
    size="lg",
    children=[],
    opened=False,
    shadow='lg',
)

# create modal with map
map_modal = dmc.Modal(
    id="map-modal",
    centered=True,
    size="75%",
    children=[
        dcc.Graph(id='map-modal-graph')
    ],
    opened=False,
    shadow='lg',
)

# create modal with distribution plot
distribution_modal = dmc.Modal(
    id="distribution-modal",
    centered=True,
    size="75%",
    children=[
        dcc.Graph(id='distribution-modal-graph')
    ],
    opened=False,
    shadow='lg',
)

about_modal = dmc.Modal(
    id="about-modal",
    centered=True,
    size="lg",
    children=[
        dmc.Stack([
            dmc.Group([
                dmc.Image(src=get_asset_url('pra_logo.png'), h=50),
                dmc.Title("About Patient Rights Advocate", size="h3", c="blue"),
            ], align="center", gap="md"),
            
            dmc.Divider(),
            
            dmc.Text([
                "Patient Rights Advocate (PRA) is dedicated to transforming the healthcare system into one that is transparent, competitive, and fair, ultimately lowering prices and improving care quality for all Americans."
            ], size="md", mb="lg"),
            
            dmc.Stack([
                dmc.Title("Hospital Price Transparency Initiative", size="h4", c="blue"),
                dmc.Text([
                    "Since January 1, 2021, hospitals are required by federal law to publish clear, accessible pricing information online. This platform helps analyze and visualize this crucial pricing data to empower patients with the information they need to make informed healthcare decisions."
                ], size="sm"),
                
                dmc.Title("How This Platform Helps", size="h4", c="blue", mt="md"),
                dmc.List([
                    dmc.ListItem("Search and compare hospital prices across thousands of facilities"),
                    dmc.ListItem("View pricing by HCPCS codes or product names"),
                    dmc.ListItem("Visualize pricing patterns and geographic variations"),
                    dmc.ListItem("Export data for further analysis"),
                    dmc.ListItem("Identify 340B participating hospitals"),
                ], size="sm"),
                  dmc.Group([
                    dmc.Anchor([
                        dmc.Button(
                            "Visit PRA Website",
                            leftSection=DashIconify(icon="mdi:external-link", width=16),
                            variant="filled",
                            color="blue"
                        )
                    ], href="https://www.patientrightsadvocate.org/", target="_blank"),
                    dmc.Anchor([
                        dmc.Button(
                            "Hospital Price Finder",
                            leftSection=DashIconify(icon="mdi:magnify", width=16),
                            variant="outline",
                            color="blue"
                        )
                    ], href="https://hospitalpricingfiles.org/", target="_blank"),
                ], justify="center", mt="lg"),
            ], gap="sm"),
        ], gap="md", p="lg"),
    ],
    opened=False,
    shadow='lg',
)

help_modal = dmc.Modal(
    id="help-modal",
    centered=True,
    size="lg",
    children=[
        dmc.Stack([
            dmc.Group([
                DashIconify(icon="mdi:help-circle", width=40, color="green"),
                dmc.Title("How to Use This Platform", size="h3", c="green"),
            ], align="center", gap="md"),
            
            dmc.Divider(),
            
            dmc.Stack([
                dmc.Title("Getting Started", size="h4", c="green"),                dmc.List([
                    dmc.ListItem([
                        dmc.Text("Toggle Search Mode: ", fw="bold", span=True),
                        "Use the switch to search by HCPCS codes or Product names"
                    ]),
                    dmc.ListItem([
                        dmc.Text("Select a Product: ", fw="bold", span=True),
                        "Choose from the dropdown menu to filter hospital pricing data"
                    ]),
                    dmc.ListItem([
                        dmc.Text("Explore Data: ", fw="bold", span=True),
                        "View pricing information, data grid, and interactive charts"
                    ]),
                ], size="sm"),
                
                dmc.Title("Platform Features", size="h4", c="green", mt="md"),                dmc.Grid([
                    dmc.GridCol([
                        dmc.Stack([
                            dmc.Group([
                                DashIconify(icon="mdi:table-eye", width=20, color="blue"),
                                dmc.Text("Price Information", fw="bold", size="sm")
                            ], gap="xs"),
                            dmc.Text("View summarized pricing statistics for selected products", size="xs", c="gray"),
                        ], gap="xs"),
                    ], span=6),
                    dmc.GridCol([
                        dmc.Stack([
                            dmc.Group([
                                DashIconify(icon="mdi:grid", width=20, color="blue"),
                                dmc.Text("Data Grid", fw="bold", size="sm")
                            ], gap="xs"),
                            dmc.Text("Browse detailed hospital data with sorting and filtering", size="xs", c="gray"),
                        ], gap="xs"),
                    ], span=6),
                    dmc.GridCol([
                        dmc.Stack([
                            dmc.Group([
                                DashIconify(icon="mdi:map", width=20, color="blue"),
                                dmc.Text("Interactive Map", fw="bold", size="sm")
                            ], gap="xs"),
                            dmc.Text("Visualize hospital locations and pricing geographically", size="xs", c="gray"),
                        ], gap="xs"),
                    ], span=6),
                    dmc.GridCol([
                        dmc.Stack([
                            dmc.Group([
                                DashIconify(icon="mdi:chart-histogram", width=20, color="blue"),
                                dmc.Text("Price Distribution", fw="bold", size="sm")
                            ], gap="xs"),
                            dmc.Text("Analyze pricing patterns and distributions", size="xs", c="gray"),
                        ], gap="xs"),
                    ], span=6),
                ]),
                
                dmc.Title("Tips for Success", size="h4", c="green", mt="md"),
                dmc.List([
                    dmc.ListItem("Click on map points to view detailed hospital information"),
                    dmc.ListItem("Use the expand buttons to view charts in full screen"),
                    dmc.ListItem("Export data to CSV for further analysis"),
                    dmc.ListItem("Toggle sections on/off to focus on specific data views"),
                    dmc.ListItem("Look for 340B badges to identify participating hospitals"),
                ], size="sm"),
                
                dmc.Alert(
                    [
                        DashIconify(icon="mdi:information", width=16),
                        dmc.Text("This platform analyzes publicly available hospital pricing data as required by federal transparency rules. Actual costs may vary based on insurance, negotiations, and specific circumstances.", size="sm", ml="xs")
                    ],
                    color="blue",
                    variant="light",
                    mt="md"
                ),
            ], gap="sm"),
        ], gap="md", p="lg"),
    ],
    opened=False,
    shadow='lg',
)

# Create the main layout
layout = dmc.AppShell([
    dmc.AppShellHeader(
        dmc.Box([
            dmc.Group([
                # Left side - Burger and Logo
                dmc.Group([
                    dmc.Burger(id="burger", size="sm", hiddenFrom="sm", opened=False, className="header-burger"),
                    dmc.Anchor(
                        dmc.Image(src=get_asset_url('pra_logo.png'), h=45, className="header-logo"),
                        href="https://www.patientrightsadvocate.org/",
                        target="_blank"
                    ),
                ], gap="md"),
                  # Center - Title and Subtitle
                dmc.Box([
                    dmc.Title("Hospital Price Transparency", size="h2", className='header-main-title'),
                    dmc.Text("Empowering Patients with Clear Healthcare Pricing", className='header-subtitle'),
                ], className="header-title-section"),
                
                # Right side - Action buttons
                dmc.Group([
                    dmc.Button(
                        [DashIconify(icon="material-symbols:info-outline", width=16), "About"],
                        variant="subtle",
                        color="gray",
                        size="sm",
                        className="header-action-btn",
                        id='about-btn'
                    ),
                    dmc.Button(
                        [DashIconify(icon="material-symbols:help-outline", width=16), "Help"],
                        variant="subtle", 
                        color="gray",
                        size="sm",
                        className="header-action-btn",
                        id='help-btn'
                    ),
                ], gap="xs", visibleFrom="md"),
                
            ], justify="space-between", align="center", h="100%", px="lg"),        ], className="header-container")
    ),
    
    dmc.AppShellNavbar(
        id="navbar",
        children=[UIComponents.create_navigation()],
        p="md",
    ),
    
    dmc.AppShellMain([
        dmc.Stack([
            UIComponents.create_price_section(),
            UIComponents.create_data_grid(),
            UIComponents.create_charts_section(),
        ], gap='md'),
        about_modal,
        help_modal,        
        schema_modal,
        hospital_modal,
        map_modal,
        distribution_modal,
    ]),
    
    dmc.AppShellFooter(UIComponents.create_footer()),
], **{
    "header": {"height": 60},
    "footer": {"height": 70},
    "padding": "md",
    "navbar": {
        "width": 325,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    },
    "id": "appshell",
})

app.layout = dmc.MantineProvider(layout)

# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output("switch-text", "children"), 
    Input("switch-toggle", "checked")
)
def update_switch_text(checked):
    """Update the switch description text"""
    return dmc.Text(f"Search by {'HCPCS' if checked else 'Product'}")


@callback(
    [Output('selection-dropdown', 'data'),
     Output('selection-dropdown', 'value')],
    Input('switch-toggle', 'checked')
)
def update_dropdown_options(is_hcpcs):
    """Update dropdown options based on toggle selection"""
    try:
        if is_hcpcs:
            options = get_hcpcs_desc_list()
        else:
            options = get_product_list()
        
        return options, options[0] if options else None
    except Exception as e:
        print(f"Error updating dropdown options: {e}")
        return [], None


@callback(
    Output("appshell", "navbar"),
    [Input("burger", "opened")],
    [State("appshell", "navbar")]
)
def toggle_navbar(opened, navbar):
    """Toggle mobile navbar visibility"""
    navbar["collapsed"] = {"mobile": not opened}
    return navbar


@callback(
    [Output('grid', 'rowData'),
     Output('price-info', 'children')],
    [Input('selection-dropdown', 'value'),
     Input('switch-toggle', 'checked')]
)
def update_data_and_prices(selected_value, is_hcpcs):
    """Update grid data and price information"""
    if not selected_value:
        return [], no_price_table()
    
    try:
        selection_type = 'hcpcs' if is_hcpcs else 'ndc'
        
        # Get filtered data
        filtered_data = (
            filter_payment_info(selection_type, selected_value)
            .pipe(add_hospital_data)
            .collect()
            .to_dicts()
        )
        
        # Get price data
        lookup_value = selected_value
        if selection_type == 'hcpcs':
            lookup_value = get_hcpcs_code_from_desc(selected_value)
        
        prices = fetch_summarized_prices(how=selection_type, value=lookup_value).collect()
        
        if prices.is_empty():
            prices_html = no_price_table()
        else:
            formatted_prices = prices.with_columns(
                amount=pl.format('${}', c.amount)
            ).to_dict(as_series=False)
            prices_html = create_html_table(formatted_prices)
        
        return filtered_data, prices_html
        
    except Exception as e:
        print(f"Error updating data: {e}")
        return [], no_price_table()


@callback(
    [Output('map', 'figure'),
     Output('price-distribution', 'figure')],
    Input('grid', 'virtualRowData')
)
def update_visualizations(virtual_row_data):
    """Update map and price distribution charts"""
    if not virtual_row_data:
        raise PreventUpdate
        
    try:
        data = pl.DataFrame(
            virtual_row_data, 
            schema=schema_for_fig_data(), 
            strict=False
        ).lazy()
        
        map_fig = create_map_visualization(data)
        dist_plot = create_price_distribution_plot(data)
        
        return map_fig, dist_plot
        
    except Exception as e:
        print(f"Error updating visualizations: {e}")
        raise PreventUpdate


@callback(
    [Output("price-collapse", "opened"),
     Output('hidden-text-price', 'style')],
    Input("price-collapse-btn", "n_clicks")
)
def toggle_price_section(n_clicks):
    """Toggle price section visibility"""
    if not n_clicks:
        return True, {'display': 'none'}
    
    is_open = n_clicks % 2 == 1
    text_style = {'display': 'block' if is_open else 'none'}
    
    return not is_open, text_style


@callback(
    [Output("collapse-grid", "opened"),
     Output('hidden-grid-text', 'style')],
    Input("collapse-btn", "n_clicks")
)
def toggle_grid_section(n_clicks):
    """Toggle grid section visibility"""
    if not n_clicks:
        return True, {'display': 'none'}
    
    is_open = n_clicks % 2 == 1
    text_style = {'display': 'block' if is_open else 'none'}
    
    return not is_open, text_style


@callback(
    Output("grid", "exportDataAsCsv"),
    Input("csv-button", "n_clicks"),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    """Export grid data to CSV"""
    return True if n_clicks else False


@callback(
    Output("schema-modal", "opened"),
    Input("schema-btn", "n_clicks"),
    State("schema-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_schema_modal(n_clicks, opened):
    """Toggle schema modal visibility"""
    return not opened

##add callback to expand map to full screen

@callback(
    Output("map-modal", "opened"),
    Output("map-modal-graph", "figure"),
    Input("expand-map-btn", "n_clicks"),
    State("map-modal", "opened"),
    Input("grid", "virtualRowData"),
    prevent_initial_call=True,
)
def toggle_map_modal(n_clicks, opened, virtual_row_data):
    """Toggle map modal visibility"""
    ctx = callback_context
    if not virtual_row_data:
        raise PreventUpdate

    # Only toggle modal if the expand button was clicked
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("expand-map-btn"):
        if not n_clicks:
            return no_update, no_update
        data = pl.DataFrame(
            virtual_row_data,
            schema=schema_for_fig_data(),
            strict=False
        ).lazy()
        map_fig = create_map_visualization(data)
        return not opened, map_fig
    # If triggered by grid data, just update the figure, don't open modal
    elif ctx.triggered and ctx.triggered[0]["prop_id"].startswith("grid"):
        data = pl.DataFrame(
            virtual_row_data,
            schema=schema_for_fig_data(),
            strict=False
        ).lazy()
        map_fig = create_map_visualization(data)
        return no_update, map_fig
    return no_update, no_update

##add callback to expand distribution plot to full screen

@callback(
    Output("distribution-modal", "opened"),
    Output("distribution-modal-graph", "figure"),
    Input("expand-distribution-btn", "n_clicks"),
    State("distribution-modal", "opened"),
    Input("grid", "virtualRowData"),
    prevent_initial_call=True,
)
def toggle_distribution_modal(n_clicks, opened, virtual_row_data):
    """Toggle distribution modal visibility"""
    ctx = callback_context
    if not virtual_row_data:
        raise PreventUpdate

    # Only toggle modal if the expand button was clicked
    if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("expand-distribution-btn"):
        if not n_clicks:
            return no_update, no_update
        data = pl.DataFrame(
            virtual_row_data,
            schema=schema_for_fig_data(),
            strict=False
        ).lazy()
        dist_fig = create_price_distribution_plot(data)
        return not opened, dist_fig
    # If triggered by grid data, just update the figure, don't open modal
    elif ctx.triggered and ctx.triggered[0]["prop_id"].startswith("grid"):
        data = pl.DataFrame(
            virtual_row_data,
            schema=schema_for_fig_data(),
            strict=False
        ).lazy()
        dist_fig = create_price_distribution_plot(data)
        return no_update, dist_fig
    return no_update, no_update



@callback(
    Output("about-modal", "opened"),
    Input("about-btn", "n_clicks"),
    State("about-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_about_modal(n_clicks, opened):
    """Toggle about modal visibility"""
    return not opened

@callback(
    Output("help-modal", "opened"),
    Input("help-btn", "n_clicks"),
    State("help-modal", "opened"),
    prevent_initial_call=True,
)
def toggle_help_modal(n_clicks, opened):
    """Toggle help modal visibility"""
    return not opened

@callback(
    [Output('hospital-info-modal', 'children'),
     Output('hospital-info-modal', 'opened')],
    Input('map', 'clickData'),
    prevent_initial_call=True,
)
def show_hospital_info(click_data):
    """Display hospital information modal when map point is clicked"""
    if not click_data:
        return [], False
    
    try:
        hospital_id = click_data['points'][0]['customdata'][3]
        hospital_data = (
            hospitals_data
            .filter(c.unique_id == hospital_id)
            .collect()
            .to_dict(as_series=False)
        )
        
        if not hospital_data['name']:
            return [], False
        
        # Create hospital info card
        card = dmc.Card([
            dmc.Stack([
                dmc.Group([
                    dmc.Anchor(
                        dmc.Text(hospital_data['name'][0], className='hospital-title'),
                        href=hospital_data.get('hospital_url', ['#'])[0],
                        target="_blank"
                    ),
                    dmc.Badge("340B Participant", color="green") if hospital_data.get('is_340b', [False])[0] else None,
                    dmc.Badge(hospital_data.get('program_type_long'), color="blue") if hospital_data.get('is_340b', [False])[0] else None
                ], justify="start"),
                
                dmc.Divider(),
                  dmc.SimpleGrid([
                    dmc.Stack([
                        dmc.Text("State", size="sm", fw="bold"),
                        dmc.Text(hospital_data['state'][0])
                    ]),
                    dmc.Stack([
                        dmc.Text("Bed Count", size="sm", fw="bold"),
                        dmc.Text(str(hospital_data['beds'][0]))
                    ]),
                ], cols=2),
            ])
        ], shadow="sm", radius="md", p="lg", className='hospital-card')
        
        return card, True
        
    except Exception as e:
        print(f"Error displaying hospital info: {e}")
        return [], False


if __name__ == "__main__":
    app.run(debug=True)