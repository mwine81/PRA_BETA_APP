
#c.unique_id,c.name,c.state,c.beds,c.lat,c.long

dashGridOptions = {
    # "pagination": True,
    # "paginationAutoPageSize": True,
}

defaultColDef = {
    # set null cells to red
    'cellClassRules': {
            'invalid-data': "[null].includes(params.value)"
        },
    'sortable': True,
    # filter option
    'filter': True,
    "filterParams": {
            "buttons": ["clear", "apply"],
        },
    "initialWidth": 200,
    "wrapHeaderText": True,
    "autoHeaderHeight": True,
}

columnDefs = [
    ##c.unique_id,c.name,c.state,c.beds,c.lat,c.long

    {
        'headerName': 'Hospital Information Toggle',
        'children': [
                {
                'headerName': 'Hospital Name',
                'field': 'name'
            },
            {
                'headerName': 'Hospital State',
                'field': 'state',
                'columnGroupShow': 'open',
            },
            {
                'headerName': 'Hospital Beds',
                'field': 'beds',
                'columnGroupShow': 'open',
            },
            
            {
                'headerName': 'Hospital Latitude',
                'field': 'lat',
                'columnGroupShow': 'open',
                'hide': True,
            },
            {
                'headerName': 'Hospital Longitude',
                'field': 'long',
                'columnGroupShow': 'open',
                'hide': True,
            },
            
        ]
    },
    {
        'headerName': '340B',
        'field': 'is_340b',
        'columnGroupShow': 'open',
    },
    {
        'headerName': 'Description',
        'field': 'description'
    },
    {
        'headerName': 'Product Id Toggle',
        'children': [
            {
                'headerName': 'NDC',
                'field': 'ndc',
                'columnGroupShow': 'open',
            },
            {
                'headerName': 'HCPCS',
                'field': 'hcpcs',
                'columnGroupShow': 'closed',
            },
        ]
    },
    {
        'headerName': 'Setting',
        'field': 'setting'
    },
    {
        'headerName': 'Drug Unit of Measurement',
        'field': 'drug_unit_of_measurement',
        'valueFormatter': {"function": 'd3.format(",")(params.value)'}
    },
    {
        'headerName': 'Drug Type of Measurement',
        'field': 'drug_type_of_measurement',
        # "cellStyle": {
        #     "styleConditions": [
        #         {
        #             "condition": "[null].includes(params.value)",
        #             "style": {
        #                 "backgroundColor": "red",
        #                 "opacity": 0.1,
        #             }
        #         }
        #     ]
        # },
        
    },
    {
        'headerName': 'Plan Information Toggle',
        'children': [
            {
            'headerName': 'Payer Name',
            'field': 'payer_name',
            'columnGroupShow': 'closed',
            },
            {
                'headerName': 'Plan Name',
                'field': 'plan_name',
                'columnGroupShow': 'closed',
            },
            {
                'headerName': 'Mapped Plan Name',
                'field': 'mapped_plan_name',
                'columnGroupShow': 'open',
            },
            {
                'headerName': 'Mapped LOB Name',
                'field': 'mapped_lob_name',
                'columnGroupShow': 'open',
            }
        ]
    },

    {
        'headerName': 'Standard Charge Negotiated Dollar',
        'field': 'standard_charge_negotiated_dollar',
        'valueFormatter': {"function": 'd3.format("$,.2f")(params.value)'},
        'cellClassRules': {
            'calculated-data': "params.data.calculated_negotiated_dollars === true"
        },
        'headerTooltip': 'Values in RED are calculated from the negotiated percentage and standard charge gross',
    },
    {
        'headerName': 'Standard Charge Gross',
        'field': 'standard_charge_gross',
        'columnGroupShow': 'open',
            'valueFormatter': {"function": 'd3.format("$,.2f")(params.value)'},
    },
    {
        'headerName': 'Standard Charge Discounted Cash',
        'field': 'standard_charge_discounted_cash',
        'columnGroupShow': 'open',
        'valueFormatter': {"function": 'd3.format("$,.2f")(params.value)'},
            'cellClassRules': {
            'calculated-data': {"function": "params.data.standard_charge_discounted_cash < params.data.standard_charge_negotiated_dollar"}
        },
    },
    {
        'headerName': 'Standard Charge Methodology',
        'field': 'standard_charge_methodology'
    },
    {
        'headerName': 'Standard Charge Negotiated Percentage',
        'field': 'standard_charge_negotiated_percentage',
        'valueFormatter': {"function": 'd3.format(".1%")(params.value)'},
    },
    {
        'headerName': 'Calculated Negotiated Dollars',
        'field': 'calculated_negotiated_dollars',
        'hide': True,
    },
    {
        'headerName': 'Hospital Unique ID',
        'field': 'hospital_unique_id',
        'hide': True,
    },
        {
        'headerName': 'As Of Date',
        'field': 'retrieved',
        'hide': False,
    },
    
]