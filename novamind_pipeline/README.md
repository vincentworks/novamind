HOW TO RUN

1. Clone the repository

git clone <your-repo-url>
cd novamind_pipeline

2. Set up a virtual environment

python3 -m venv venv
source venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Set up environment variables

Create a file named .env in the project root and add:

HUBSPOT_PRIVATE_APP_TOKEN=your_token_here

Note:

This is only required for the HubSpot integration step
The rest of the pipeline runs fully with mock data.

5. Run the pipeline

Run each step in order:

python3 src/generate_content.py --topic "AI in creative automation"
python3 src/crm_simulation.py
python3 src/hubspot_integration.py (requires HubSpot token)
python3 src/analyze_performance.py

6. View outputs

All outputs are saved in the "data" folder:

generated_content.json → AI-generated blog and newsletters
campaign_log.json → campaign and audience segmentation
hubspot_payloads.json → CRM and email API payloads
performance_log.json → performance metrics and insights
