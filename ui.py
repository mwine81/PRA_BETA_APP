import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html, dcc, get_asset_url
import dash_ag_grid as dag
from ag_grid_def import columnDefs, defaultColDef, dashGridOptions
from helpers import create_mantine_dictionary

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
        expand_icon = DashIconify(icon="mdi:fullscreen", width=22, height=22, style={"verticalAlign": "middle"})
        return dmc.Grid([
            dmc.GridCol(
                dmc.Card([
                    dmc.Stack([
                        dmc.Box([
                            dmc.Button(
                                expand_icon,
                                id="expand-map-btn",
                                n_clicks=0,
                                variant='subtle',
                                size='lg',
                                className='expand-fab',
                                style={
                                    'position': 'absolute',
                                    'top': '12px',
                                    'left': '12px',  # Move to left
                                    'zIndex': 2,
                                    'borderRadius': '50%',
                                    'padding': '0.35rem',
                                    'minWidth': '44px',
                                    'minHeight': '44px',
                                    'width': '44px',
                                    'height': '44px',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.10)',
                                    'background': 'rgba(255,255,255,0.95)',
                                    'border': '1px solid #e3e8ee',
                                    'transition': 'box-shadow 0.2s, background 0.2s',
                                }
                            ),
                        ], style={'position': 'relative', 'width': '100%', 'height': '0'}),
                        dcc.Loading(
                            dcc.Graph(id='map'),
                            type="circle"
                        ),
                    ], gap=0, style={'position': 'relative'}),
                ], shadow='sm', p="sm"),
                span={'base': 12, 'xl': 6} # type: ignore
            ),
            dmc.GridCol(
                dmc.Card([
                    dmc.Stack([
                        dmc.Box([
                            dmc.Button(
                                expand_icon,
                                id="expand-distribution-btn",
                                n_clicks=0,
                                variant='subtle',
                                size='lg',
                                className='expand-fab',
                                style={
                                    'position': 'absolute',
                                    'top': '12px',
                                    'left': '12px',  # Move to left
                                    'zIndex': 2,
                                    'borderRadius': '50%',
                                    'padding': '0.35rem',
                                    'minWidth': '44px',
                                    'minHeight': '44px',
                                    'width': '44px',
                                    'height': '44px',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center',
                                    'boxShadow': '0 2px 8px rgba(0,0,0,0.10)',
                                    'background': 'rgba(255,255,255,0.95)',
                                    'border': '1px solid #e3e8ee',
                                    'transition': 'box-shadow 0.2s, background 0.2s',
                                }
                            ),
                        ], style={'position': 'relative', 'width': '100%', 'height': '0'}),
                        dcc.Loading(
                            dcc.Graph(id='price-distribution'),
                            type="circle"
                        ),
                    ], gap=0, style={'position': 'relative'}),
                ], shadow='sm', p="sm"),
                span={'base': 12, 'xl': 6} # type: ignore
            ),
        ])
    
    @staticmethod
    def create_charts_section():
        """Create the charts section with professional header"""
        return dmc.Card([
            dmc.Text("Chart Analysis", className='section-title', style={'textAlign': 'center'}),
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
                ),
                opened=True, 
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
                dmc.Box([
                    dmc.Text("Powered By", className='footer-text'),
                    dmc.Image(src=get_asset_url('3AA-logo-1-stack.jpg'), className='footer-logo'),
                ], className='footer-left'),
                
                dmc.Box([
                    dmc.Box([
                        dmc.Text("© 2025 3AxisAdvisors", className='copyright-text'),
                        dmc.Text("All Rights Reserved", className='rights-text'),
                    ], className='footer-text-stack'),
                    
                    dmc.Box([
                        dmc.Anchor(
                            DashIconify(icon='logos:linkedin-icon'),
                            href="#", className='social-icon', target="_blank"
                        ),
                        dmc.Anchor(
                            DashIconify(icon='logos:facebook'),
                            href="#", className='social-icon', target="_blank"
                        ),
                        dmc.Anchor(
                            DashIconify(icon='logos:x'),
                            href="#", className='social-icon', target="_blank"
                        ),
                    ], className='social-icons'),
                ], className='footer-right'),
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
    size="75%", # type: ignore
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
    size="75%", # type: ignore
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
        dmc.Text("About Hospital Price Transparency", className='modal-title'),
        dmc.Text("This modal provides information about the hospital price transparency initiative.", className='modal-content'),
    ],
    opened=False,
    shadow='lg',
)

help_modal = dmc.Modal(
    id="help-modal",
    centered=True,
    size="lg",
    children=[
        dmc.Text("Help", className='modal-title'),
        dmc.Text("This modal provides information about how to use the hospital price transparency platform.", className='modal-content'),
    ],
    opened=False,
    shadow='lg',
)