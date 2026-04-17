# Sample RFQ documents simulating real customer enquiries
# These represent the kind of unstructured text ECAM Engineering receives

RFQ_SAMPLES = [
    {
        "rfq_id": "RFQ001",
        "customer": "Midlands Aerospace",
        "text": """
        Request for Quotation — Midlands Aerospace Ltd
        Date: 15 April 2026

        We require a quotation for the manufacture of precision bearing housings 
        as per the following specification:

        Material: Aluminium alloy 6082-T6
        Quantity: 200 units
        Dimensions: 150mm diameter x 80mm length
        Tolerance: +/- 0.05mm on bore diameter
        Surface finish: Ra 1.6 on bearing surfaces, Ra 3.2 general
        Treatment: Hard anodise to 25 microns
        Delivery: Required within 6 weeks of order confirmation
        Drawing reference: MA-BH-2026-004

        Please confirm material certification requirements and 
        inspection report format. First article inspection required.
        """
    },
    {
        "rfq_id": "RFQ002",
        "customer": "TechFab Engineering",
        "text": """
        Quotation Request

        From: TechFab Engineering Solutions
        To: ECAM Engineering

        Part: Mild steel mounting brackets
        Spec: S275 mild steel, laser cut and press braked
        Qty: 50 off
        Thickness: 10mm plate
        Finish: Shot blast and prime, RAL 9005 powder coat
        Tolerance: Standard fabrication +/- 1mm
        Delivery: 4 weeks

        Please include cost per unit and tooling charges if applicable.
        Contact: procurement@techfab.co.uk
        """
    },
    {
        "rfq_id": "RFQ003",
        "customer": "Northern Hydraulics",
        "text": """
        PURCHASE ENQUIRY

        Northern Hydraulics Group require pricing for:

        Component: Stainless steel manifold blocks
        Grade: 316L stainless
        Number required: 25 pieces
        Machining: 5-axis CNC, complex internal porting
        Pressure rating: Must withstand 350 bar working pressure
        Testing: Hydraulic pressure test certificate required
        Lead time needed: 8 weeks maximum
        Delivery to: Sheffield facility

        Note: Previous supplier unable to meet capacity. 
        Urgent requirement. Please advise earliest start date.
        """
    }
]