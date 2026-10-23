# Sweden Commute & Affordable Housing Finder 🇸🇪

An agent-first application designed to help workers and newcomers in Sweden find affordable housing within a realistic commuting distance of their workplace.

## Core Features
1. **Explainable Rent Budgeting**: Computes prudent and maximum rent ceilings based on Swedish net take-home salary, fixed expenses, and emergency buffers, cross-checked against standard Swedish cost-of-living guidelines (Konsumentverket reference values).
2. **Authentic Open Data from SCB (Statistiska centralbyrån)**: Queries SCB's Doris Open API in real-time for official municipal rents per square meter (`BO0406Tab01`) and municipal tax rates (`Kommunalskatter2000`).
3. **Realistic Commute & Corridor Assessment**: Evaluates transit times and rail/metro corridors to major employment hubs (Stockholm Central, Kista Science City, Lindholmen Göteborg, Malmö Central, etc.).
4. **Transparent Housing Listings & Official Queues**: Strictly avoids inventing housing listings. Delivers verified real listings, direct access to official municipal housing queues (*Bostadsförmedlingen i Stockholm*, *Boplats Göteborg*, *Boplats Syd*), and targeted search filters.
5. **Agent-First Guidance with Google GenAI / Vertex AI**: Powered by `gemini-2.5-flash` with autonomous tool calling to explain financial trade-offs and guide relocation decisions.

## Project Structure
- [`app.py`](app.py): FastAPI web server and REST/Chat API endpoints.
- [`agent.py`](agent.py): Google GenAI Vertex AI agent orchestrator with tool declarations.
- [`tools/budget.py`](tools/budget.py): Swedish financial budgeting logic and living expense baselines.
- [`tools/scb_client.py`](tools/scb_client.py): Official SCB Doris API client.
- [`tools/commute.py`](tools/commute.py): Commute matrix and corridor transit calculator.
- [`tools/listings.py`](tools/listings.py): Verified real listing feeds and official municipal queue integrations.
- [`static/index.html`](static/index.html): Interactive dashboard and conversational assistant UI.
- [`tests/test_tools.py`](tests/test_tools.py): Unit test suite.

## Running the Application
Start the server:
```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 8080
```
Then open `http://localhost:8080` in your browser.

## Running Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
