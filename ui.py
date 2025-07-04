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
                placeholder="Search for a procedure or medication..."
            )
        ], className='dropdown-container')
    
    @staticmethod
    def create_control_buttons():
        """Create control buttons"""
        return dmc.Stack([
            dmc.Button(
                "Toggle Price Comparison", 
                id="price-collapse-btn", 
                n_clicks=0, 
                variant='outline',
                leftSection=DashIconify(icon="mdi:table-eye", width=16),
                color='blue'
            ),
            dmc.Button(
                "Toggle Hospital Data", 
                id="collapse-btn", 
                n_clicks=0, 
                variant='outline',
                leftSection=DashIconify(icon="mdi:grid", width=16),
                color='blue'
            ),
            dmc.Button(
                "Export Data", 
                id="csv-button", 
                n_clicks=0, 
                variant='filled',
                leftSection=DashIconify(icon="mdi:download", width=16),
                color='green'
            ),
            dmc.Button(
                "Data Dictionary", 
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
        """Create the charts section with professional, modern header"""
        return dmc.Card([
            dmc.Text(
                "Hospital Price Analysis",
                className='section-title-modern',
                style={
                    'textAlign': 'center',
                    'fontSize': '1.35rem',
                    'fontWeight': 600,
                    'letterSpacing': '0.01em',
                    'marginBottom': '0.5rem',
                    'color': '#1565c0',
                }
            ),
            UIComponents.create_visualizations(),
        ], shadow='sm')
    
    @staticmethod
    def create_price_section():
        """Create the pricing information section with modern header"""
        return dmc.Card([
            dmc.Text(
                "Price Transparency Data",
                className='section-title-modern',
                style={
                    'fontSize': '1.15rem',
                    'fontWeight': 500,
                    'textAlign': 'center',
                    'letterSpacing': '0.01em',
                    'marginBottom': '0.3rem',
                    'color': '#1565c0',
                }
            ),
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
        """Create the data grid section with modern header"""
        return dmc.Card([
            dmc.Text(
                "Hospital Pricing Database",
                className='section-title-modern',
                style={
                    'fontSize': '1.15rem',
                    'fontWeight': 500,
                    'textAlign': 'center',
                    'letterSpacing': '0.01em',
                    'marginBottom': '0.3rem',
                    'color': '#1565c0',
                }
            ),
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
        """Create the navigation panel with Actions section directly under the search dropdown."""
        return dmc.Card([
            dmc.Stack([
                dmc.Text(
                    'Search & Filter',
                    className='section-title-modern',
                    style={
                        'fontSize': '1.05rem',
                        'fontWeight': 500,
                        'letterSpacing': '0.01em',
                        'marginBottom': '0.2rem',
                        'color': '#1976d2',
                    }
                ),
                dmc.Divider(mb='xs'),
                dmc.Group([
                    UIComponents.create_toggle_switch(),
                    dmc.Tooltip(
                        label="Switch between HCPCS and NDC codes",
                        children=DashIconify(icon="mdi:help-circle-outline", width=18, color="#1976d2"),
                        position="right",
                        withArrow=True,
                        offset=4
                    )
                ], gap='xs', align='center'),
                dmc.Space(h=2),
                dmc.Box(
                    UIComponents.create_dropdown(),
                    style={
                        'flexGrow': 0,
                        'display': 'flex',
                        'flexDirection': 'column',
                        #'minHeight': '90px',
                        'marginBottom': '0.5rem',
                    }
                ),
                # Actions section moved directly under dropdown
                dmc.Divider(mb='xs'),
                dmc.Text("Actions", size="sm", style={'color': '#888', 'marginBottom': '0.2rem', 'marginTop': '0.2rem', 'fontWeight': 500}),
                UIComponents.create_control_buttons(),
                dmc.Space(h=2),
                # ...rest of sidebar content if any...
            ], gap='sm', style={
                'flexGrow': 1,
                'display': 'flex',
                'flexDirection': 'column',
                'height': '100%'
            }),
        ], shadow='md', p='md', radius='md', style={
            'background': 'linear-gradient(135deg, #f8fafc 80%, #e3f2fd 100%)',
            'border': '1px solid #e3e8ee',
            'minWidth': '270px',
            'maxWidth': '340px',
            'margin': '0 auto',
            'boxShadow': '0 2px 12px rgba(30, 64, 175, 0.07)',
            'height': 'calc(100vh - 48px)',  # 48px for header/footer or as needed
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'flex-start',
            'paddingBottom': '1.5rem',  # leave some space at the bottom
        })
    
    @staticmethod
    def create_footer():
        """Create the footer component"""
        return html.Footer(
            dmc.Box([
                dmc.Box([
                    dmc.Text("Empowering Patients Through Price Transparency", className='footer-text', style={'fontStyle': 'italic', 'color': '#0074D9'}),
                    dmc.Anchor(
                        dmc.Image(src=get_asset_url('pra_logo.png'), className='footer-logo'),
                        href="https://www.patientrightsadvocate.org/",
                        target="_blank"
                    ),
                ], className='footer-left'),
                
                dmc.Box([
                    dmc.Box([
                        dmc.Text("© 2025 Patient Rights Advocate", className='copyright-text'),
                        dmc.Anchor(
                            dmc.Text("Developed by 3AxisAdvisors", className='rights-text'),
                            href="https://www.3axisadvisors.com/",
                            target="_blank"
                        )
                    ], className='footer-text-stack'),
                    
                    dmc.Box([
                        dmc.Anchor(
                            DashIconify(icon='logos:linkedin-icon'),
                            href="https://www.linkedin.com/company/patient-rights-advocate/", className='social-icon', target="_blank"
                        ),
                        dmc.Anchor(
                            DashIconify(icon='logos:facebook'),
                            href="https://www.facebook.com/thepatientrightsadvocate", className='social-icon', target="_blank"
                        ),
                        dmc.Anchor(
                            DashIconify(icon='logos:x'),
                            href="https://x.com/PtRightsAdvoc", className='social-icon', target="_blank"
                        ),
                    ], className='social-icons'),
                ], className='footer-right', visibleFrom='md'),
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
        dmc.Stack([
            dmc.Text("About PRA Hospital Price Transparency", size="xl", fw="bold", c="blue"),
            dmc.Divider(),
            dmc.Text([
                "Patient Rights Advocate (PRA) is dedicated to transforming healthcare through ",
                dmc.Text("price transparency", fw="bold", c="blue", span=True),
                ". We believe that transparent, competitive, and fair pricing leads to lower costs and better care quality for all Americans."
            ], size="md"),
            dmc.Space(h="md"),
            dmc.Text("Our Mission:", fw="bold", size="lg", c="blue"),
            dmc.List([
                dmc.ListItem("Empower patients with clear, accurate healthcare pricing information"),
                dmc.ListItem("Advocate for compliance with federal price transparency requirements"),
                dmc.ListItem("Support patients who have been overcharged due to lack of transparency"),
                dmc.ListItem("Transform healthcare into a transparent, competitive marketplace"),
            ], spacing="xs"),
            dmc.Space(h="md"),
            dmc.Group([
                dmc.Anchor(
                    dmc.Button(
                        "Visit PatientRightsAdvocate.org",
                        leftSection=DashIconify(icon="mdi:open-in-new"),
                        variant="filled",
                        color="blue"
                    ),
                    href="https://www.patientrightsadvocate.org/",
                    target="_blank"
                ),
                dmc.Anchor(
                    dmc.Button(
                        "Hospital Price Finder",
                        leftSection=DashIconify(icon="mdi:hospital-building"),
                        variant="outline",
                        color="blue"
                    ),
                    href="https://hospitalpricingfiles.org/",
                    target="_blank"
                ),
            ], justify="center"),
        ], gap="sm"),
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
            dmc.Text("How to Use This Hospital Price Transparency Tool", size="xl", fw="bold", c="blue"),
            dmc.Divider(),
            dmc.Text("This tool helps you explore hospital pricing data to make informed healthcare decisions.", size="md"),
            dmc.Space(h="sm"),
            
            dmc.Accordion([
                dmc.AccordionItem([
                    dmc.AccordionControl("Getting Started", icon=DashIconify(icon="mdi:play-circle")),
                    dmc.AccordionPanel([
                        dmc.List([
                            dmc.ListItem("Use the toggle switch to select between HCPCS codes or NDC drug codes"),
                            dmc.ListItem("Select a specific product or procedure from the dropdown menu"),
                            dmc.ListItem("View pricing data in the table and explore hospital locations on the map"),
                            dmc.ListItem("Use the expand buttons to view charts in full screen"),
                        ])
                    ]),
                ], value="getting-started"),
                
                dmc.AccordionItem([
                    dmc.AccordionControl("Understanding the Data", icon=DashIconify(icon="mdi:information")),
                    dmc.AccordionPanel([
                        dmc.List([
                            dmc.ListItem("Prices shown are what hospitals have disclosed in their transparency files"),
                            dmc.ListItem("340B hospitals participate in a federal drug discount program"),
                            dmc.ListItem("Click on map points to see detailed hospital information"),
                            dmc.ListItem("Use the data grid to sort and filter results"),
                            dmc.ListItem(
                                dmc.Anchor(
                                    "Learn more about our methods",
                                    href="https://mwine81-pra-methods.share.connect.posit.cloud/",
                                    target="_blank",
                                    style={"color": "#1976d2", "textDecoration": "underline"}
                                )
                            ),
                        ])
                    ]),
                ], value="understanding-data"),
                
                dmc.AccordionItem([
                    dmc.AccordionControl("Additional Resources", icon=DashIconify(icon="mdi:link")),
                    dmc.AccordionPanel([
                        dmc.Group([
                            dmc.Anchor(
                                dmc.Button(
                                    "PRA Price Finder",
                                    leftSection=DashIconify(icon="mdi:magnify"),
                                    size="sm",
                                    variant="outline"
                                ),
                                href="https://hospitalpricingfiles.org/",
                                target="_blank"
                            ),
                            dmc.Anchor(
                                dmc.Button(
                                    "How to Shop for Healthcare",
                                    leftSection=DashIconify(icon="mdi:cart"),
                                    size="sm",
                                    variant="outline"
                                ),
                                href="https://www.patientrightsadvocate.org/howtoshop",
                                target="_blank"
                            ),
                        ], gap="sm")
                    ]),
                ], value="resources"),
            ], value="getting-started"),
        ], gap="sm"),
    ],
    opened=False,
    shadow='lg',
)