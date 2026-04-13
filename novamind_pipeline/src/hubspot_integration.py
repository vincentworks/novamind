import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CONTACTS_PATH = DATA_DIR / "contacts.json"
GENERATED_CONTENT_PATH = DATA_DIR / "generated_content.json"
HUBSPOT_PAYLOADS_PATH = DATA_DIR / "hubspot_payloads.json"

HUBSPOT_TOKEN = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN")
HUBSPOT_BASE_URL = "https://api.hubapi.com"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_headers():
    if not HUBSPOT_TOKEN:
        raise ValueError("Missing HUBSPOT_PRIVATE_APP_TOKEN in .env")
    return {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }


def split_name(full_name: str):
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def build_contact_upsert_payload(contacts):
    inputs = []

    for contact in contacts:
        first, last = split_name(contact.get("name", ""))
        inputs.append({
            "id": contact["email"],
            "idProperty": "email",
            "properties": {
                "email": contact["email"],
                "firstname": first,
                "lastname": last,
                "custom_persona": contact["persona"]
            }
        })

    return {"inputs": inputs}


def upsert_contacts_to_hubspot(payload):
    # Using legacy v3 endpoint here because it is still documented and straightforward for take-home use.
    # HubSpot also has newer date-versioned APIs, but the v3 contacts upsert flow remains well documented.
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/batch/upsert"
    response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
    return response


def build_mock_send_payloads(contacts, generated_content):
    newsletters = generated_content.get("newsletters", {})
    campaign = generated_content.get("campaign_metadata", {})
    blog_title = generated_content.get("blog_title", "")
    campaign_id = campaign.get("campaign_id", "cmp_001")
    campaign_date = campaign.get("campaign_date", "")

    send_payloads = []

    for contact in contacts:
        persona = contact["persona"]
        newsletter = newsletters.get(persona, "")
        subject = ""
        body = ""

        if isinstance(newsletter, dict):
            subject = newsletter.get("subject", "")
            body = newsletter.get("body", "")
        elif isinstance(newsletter, str):
            parts = newsletter.split("\n\n", 1)
            first_part = parts[0].strip()
            body = parts[1].strip() if len(parts) > 1 else newsletter.strip()
            subject = first_part.replace("Subject:", "").strip() if first_part.lower().startswith("subject:") else "Newsletter"

        send_payloads.append({
            "recipient_email": contact["email"],
            "persona": persona,
            "hubspot_single_send_payload": {
                "emailId": 123456789,
                "message": {
                    "to": contact["email"]
                },
                "contactProperties": {
                    "persona": persona
                },
                "customProperties": {
                    "blog_title": blog_title,
                    "campaign_id": campaign_id,
                    "campaign_date": campaign_date,
                    "newsletter_subject": subject,
                    "newsletter_body": body
                }
            }
        })

    return send_payloads


def main():
    contacts = load_json(CONTACTS_PATH)
    generated_content = load_json(GENERATED_CONTENT_PATH)

    print("Building HubSpot contact upsert payload...")
    contact_payload = build_contact_upsert_payload(contacts)

    print("Sending contacts to HubSpot...")
    response = upsert_contacts_to_hubspot(contact_payload)

    print(f"HubSpot status code: {response.status_code}")
    try:
        response_json = response.json()
    except Exception:
        response_json = {"raw_text": response.text}

    print("HubSpot response:")
    print(json.dumps(response_json, indent=2))

    print("Writing mocked newsletter-send payloads...")
    send_payloads = build_mock_send_payloads(contacts, generated_content)

    output = {
        "contact_upsert_request": contact_payload,
        "contact_upsert_response": response_json,
        "mock_single_send_requests": send_payloads
    }

    save_json(HUBSPOT_PAYLOADS_PATH, output)
    print(f"Saved mocked HubSpot payloads to: {HUBSPOT_PAYLOADS_PATH}")


if __name__ == "__main__":
    main()