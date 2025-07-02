import dash_mantine_components as dmc
from dash import Dash, callback, Output, Input, State, get_asset_url, no_update, callback_context
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import polars as pl
from polars import col as c
from ui import UIComponents, schema_modal, about_modal, help_modal, hospital_modal, map_modal, distribution_modal
from helpers import (
    get_hcpcs_desc_list, get_product_list, filter_payment_info, add_hospital_data,
    fetch_summarized_prices, schema_for_fig_data, create_map_visualization,
    create_price_distribution_plot,hospitals_data,  create_html_table, no_price_table, get_hcpcs_code_from_desc
)


# Initialize the app
app = Dash(__name__)


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
                    dmc.Title("PRA Hospital Price Transparency", size="h2", className='header-main-title'),
                    dmc.Text("Empowering Patients Through Price Data", className='header-subtitle'),
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
            UIComponents.create_charts_section(),
            UIComponents.create_data_grid(),
            UIComponents.create_price_section(),
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
    "footer": {"height": 60},
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
            .collect(engine='streaming')
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