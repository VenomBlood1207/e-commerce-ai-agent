# Setup Guide for E-commerce Intelligence Agent

## Step-by-Step Setup Instructions

### 1. Environment Setup

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```bash
GROQ_API_KEY=your_actual_groq_api_key_here
```

Get your Groq API key from: https://console.groq.com/

### 2. Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Download Dataset

**Option A: Using Kaggle CLI**
```bash
pip install kaggle
kaggle datasets download -d olistbr/brazilian-ecommerce
unzip brazilian-ecommerce.zip -d data/
```

**Option B: Manual Download**
1. Visit: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/
2. Download the dataset
3. Extract all CSV files to `data/` directory

Expected files in `data/`:
- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_order_payments_dataset.csv
- olist_order_reviews_dataset.csv
- olist_customers_dataset.csv
- olist_sellers_dataset.csv
- olist_products_dataset.csv
- product_category_name_translation.csv
- olist_geolocation_dataset.csv

### 4. Initialize Database

```bash
python scripts/ingest_data.py
```

This will:
- Create SQLite database
- Load all CSV files
- Generate vector embeddings for products
- Initialize conversation memory

### 5. Frontend Setup

```bash
cd frontend
npm install
```

### 6. Run the Application

**Terminal 1 - Backend Server:**
```bash
# From project root
source venv/bin/activate
python main.py
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

**Terminal 2 - Frontend Server:**
```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

### 7. Verify Installation

Test the backend:
```bash
curl http://localhost:8000/health
```

Test an agent query:
```bash
python scripts/test_agents.py
```

## Common Issues

### Issue: "GROQ_API_KEY not found"
**Solution:** Make sure you created `.env` file and added your API key

### Issue: "Data directory not found"
**Solution:** Download the dataset and extract to `data/` directory

### Issue: "Module not found"
**Solution:** Make sure virtual environment is activated and dependencies are installed

### Issue: "Port already in use"
**Solution:** Change port in `.env` file or kill the process using the port

## Next Steps

Once everything is running:
1. Open http://localhost:3000 in your browser
2. Try example queries like:
   - "What are the top 5 product categories?"
   - "Show me average delivery time by state"
   - "Translate 'cama_mesa_banho' to English"

## Development Tips

- Backend auto-reloads on code changes (uvicorn --reload)
- Frontend auto-reloads with Vite HMR
- Check logs in terminal for debugging
- Use `/docs` endpoint for API testing

## Production Deployment

For production:
```bash
# Build frontend
cd frontend
npm run build

# Run with production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Need Help?

- Check the main README.md for architecture details
- Review the API docs at http://localhost:8000/docs
- Check backend logs for error messages
