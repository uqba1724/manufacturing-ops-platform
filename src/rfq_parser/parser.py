import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import anthropic
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
# This makes ANTHROPIC_API_KEY available to the script
load_dotenv()


# --- COST RATES ---
# These are the unit cost assumptions used to generate the cost estimate
# In a real system these would come from a pricing database
COST_RATES = {
    "materials": {
        "Aluminium 6082": 8.50,   # £ per kg
        "Mild Steel S275": 3.20,   # £ per kg
        "Stainless Steel 316L": 18.00,  # £ per kg
        "default": 5.00            # £ per kg fallback
    },
    "machining_per_hour": 65.0,    # £ per hour CNC machining
    "setup_charge": 150.0,         # £ fixed setup charge per job
    "finishing_per_unit": 8.0,     # £ per unit for surface treatment
    "margin_pct": 0.20             # 20% margin
}


def parse_rfq_with_ai(rfq_text: str, rfq_id: str) -> dict:
    """
    Sends an RFQ text to the Claude API and returns structured JSON
    with extracted fields, a BoM stub, and a cost estimate.
    """

    # Initialise the Anthropic client
    # It automatically reads ANTHROPIC_API_KEY from environment variables
    client = anthropic.Anthropic()

    # --- SYSTEM PROMPT ---
    # This tells the AI exactly what role it is playing and
    # what format to return. Being explicit about JSON format
    # is critical — without it the AI might return prose.
    system_prompt = """You are an RFQ (Request for Quotation) parser for a precision 
engineering company. Your job is to extract structured information from 
unstructured RFQ documents.

Extract the following fields and return ONLY a valid JSON object with no 
additional text, no markdown, no code blocks — just the raw JSON:

{
    "part_name": "name of the part or component",
    "material": "material specification",
    "quantity": integer or null if not specified,
    "dimensions": "key dimensions as a string or null",
    "tolerance": "tolerance specification or null",
    "surface_finish": "surface finish requirements or null",
    "treatment": "surface treatment or coating or null",
    "delivery_weeks": integer number of weeks or null,
    "special_requirements": "any special requirements or null",
    "confidence": "high, medium, or low based on clarity of the RFQ",
    "missing_fields": ["list of important fields that were not specified"]
}

If a field is not mentioned, use null. Be precise and use the exact 
specifications mentioned. Do not invent information not present in the text."""

    # --- API CALL ---
    # We send the system prompt and the RFQ text to Claude
    # max_tokens limits the response length — 1000 is enough for JSON
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"Please parse this RFQ document:\n\n{rfq_text}"
            }
        ],
        system=system_prompt
    )

    # Extract the text response from the API response object
    raw_response = message.content[0].text

# Clean the response — remove markdown code blocks if present
    # The AI sometimes wraps JSON in ```json ... ``` formatting
    cleaned_response = raw_response.strip()
    if cleaned_response.startswith("```"):
        # Remove opening ```json or ``` and closing ```
        lines = cleaned_response.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned_response = "\n".join(lines).strip()

    # Parse the cleaned JSON string into a Python dictionary
    try:
        extracted = json.loads(cleaned_response)
    except json.JSONDecodeError:
        # If still not valid JSON, return an error structure
        extracted = {
            "error": "Failed to parse AI response as JSON",
            "raw_response": raw_response
        }
        return {"rfq_id": rfq_id, "extraction": extracted,
                "bom": [], "cost_estimate": {}}

    # --- GENERATE BOM STUB ---
    # Use the extracted fields to build a simple Bill of Materials
    bom = generate_bom(extracted)

    # --- GENERATE COST ESTIMATE ---
    cost_estimate = generate_cost_estimate(extracted, bom)

    return {
        "rfq_id": rfq_id,
        "parsed_at": datetime.utcnow().isoformat(),
        "extraction": extracted,
        "bom": bom,
        "cost_estimate": cost_estimate
    }


def generate_bom(extracted: dict) -> list:
    """
    Generates a Bill of Materials stub from extracted RFQ fields.
    Returns a list of BOM line items.
    """
    bom = []
    item_counter = 1

    # Material line item
    if extracted.get("material") and extracted.get("quantity"):
        # Estimate material weight: assume 0.5kg per unit as default
        # In a real system this would use the dimensions and material density
        estimated_weight_kg = 0.5 * extracted["quantity"]

        bom.append({
            "item_no": item_counter,
            "item_code": f"MAT{item_counter:03d}",
            "description": f"{extracted['material']} raw material",
            "quantity": estimated_weight_kg,
            "unit": "kg",
            "unit_cost": get_material_rate(extracted["material"]),
            "total_cost": round(
                estimated_weight_kg * get_material_rate(extracted["material"]), 2
            )
        })
        item_counter += 1

    # Machining line item
    if extracted.get("quantity"):
        # Estimate machining hours: 0.25 hours per unit as default
        estimated_hours = 0.25 * extracted["quantity"]

        bom.append({
            "item_no": item_counter,
            "item_code": f"PROC{item_counter:03d}",
            "description": "CNC machining and programming",
            "quantity": estimated_hours,
            "unit": "hours",
            "unit_cost": COST_RATES["machining_per_hour"],
            "total_cost": round(
                estimated_hours * COST_RATES["machining_per_hour"], 2
            )
        })
        item_counter += 1

    # Surface treatment line item
    if extracted.get("treatment") and extracted.get("quantity"):
        bom.append({
            "item_no": item_counter,
            "item_code": f"PROC{item_counter:03d}",
            "description": f"Surface treatment: {extracted['treatment']}",
            "quantity": extracted["quantity"],
            "unit": "units",
            "unit_cost": COST_RATES["finishing_per_unit"],
            "total_cost": round(
                extracted["quantity"] * COST_RATES["finishing_per_unit"], 2
            )
        })
        item_counter += 1

    # Setup charge — fixed per job
    bom.append({
        "item_no": item_counter,
        "item_code": f"SETUP{item_counter:03d}",
        "description": "Job setup and programming",
        "quantity": 1,
        "unit": "job",
        "unit_cost": COST_RATES["setup_charge"],
        "total_cost": COST_RATES["setup_charge"]
    })

    return bom


def get_material_rate(material: str) -> float:
    """Returns the cost per kg for a given material string."""
    material_lower = material.lower()
    for key, rate in COST_RATES["materials"].items():
        key_lower = key.lower()
        # Check both directions to handle variable word order
        if key_lower in material_lower or material_lower in key_lower:
            return rate
        # Also check if all significant words from the key appear in material
        key_words = [w for w in key_lower.split() if len(w) > 2]
        if all(w in material_lower for w in key_words):
            return rate
    return COST_RATES["materials"]["default"]


def generate_cost_estimate(extracted: dict, bom: list) -> dict:
    """
    Generates a cost estimate from the BOM.
    Returns subtotal, margin, and total.
    """
    subtotal = sum(item["total_cost"] for item in bom)
    margin = round(subtotal * COST_RATES["margin_pct"], 2)
    total = round(subtotal + margin, 2)

    quantity = extracted.get("quantity", 1) or 1
    cost_per_unit = round(total / quantity, 2)

    return {
        "subtotal": round(subtotal, 2),
        "margin_pct": COST_RATES["margin_pct"] * 100,
        "margin": margin,
        "total_estimate": total,
        "quantity": quantity,
        "cost_per_unit": cost_per_unit,
        "currency": "GBP",
        "note": "Estimate only — subject to drawing review and final pricing"
    }


if __name__ == "__main__":
    from src.rfq_parser.sample_rfqs import RFQ_SAMPLES

    print("ECAM RFQ Parser — AI-Powered Document Extraction")
    print("=" * 55)

    for sample in RFQ_SAMPLES:
        print(f"\nProcessing {sample['rfq_id']} — {sample['customer']}")
        print("-" * 40)

        result = parse_rfq_with_ai(sample["text"], sample["rfq_id"])

        print(f"Part:      {result['extraction'].get('part_name', 'N/A')}")
        print(f"Material:  {result['extraction'].get('material', 'N/A')}")
        print(f"Quantity:  {result['extraction'].get('quantity', 'N/A')}")
        print(f"Delivery:  {result['extraction'].get('delivery_weeks', 'N/A')} weeks")
        print(f"Confidence:{result['extraction'].get('confidence', 'N/A')}")

        missing = result['extraction'].get('missing_fields', [])
        if missing:
            print(f"Missing:   {', '.join(missing)}")

        print(f"\nBOM ({len(result['bom'])} items):")
        for item in result["bom"]:
            print(f"  {item['item_code']}: {item['description']}")
            print(f"    {item['quantity']} {item['unit']} x £{item['unit_cost']} = £{item['total_cost']}")

        print(f"\nCost Estimate:")
        print(f"  Subtotal:     £{result['cost_estimate']['subtotal']}")
        print(f"  Margin (20%): £{result['cost_estimate']['margin']}")
        print(f"  Total:        £{result['cost_estimate']['total_estimate']}")
        print(f"  Per unit:     £{result['cost_estimate']['cost_per_unit']}")

        print("\n" + "=" * 55)