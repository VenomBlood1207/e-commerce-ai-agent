# Category Translation Fix

## Problem

When users queried for product categories using English names (e.g., "electronics", "furniture"), the SQL agent generated queries that searched for these English names directly in the `products` table. However, the product categories in the database are stored in **Portuguese** (e.g., "eletronicos", "moveis_decoracao"), causing queries to return `null` or no results.

### Example Issue

**User Query:** "What is the average order value for items in the electronics category?"

**Generated SQL (Before Fix):**
```sql
SELECT AVG(oi.price) as average_order_value
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
WHERE p.product_category_name = 'electronics';
```

**Result:** `null` (because 'electronics' doesn't exist in Portuguese database)

## Solution Implemented

### 1. Updated SQL Examples (`backend/config.py`)

Added examples showing proper use of the `product_category_name_translation` table:

```python
{
    "question": "What is the average order value for items in the electronics category?",
    "sql": """
        SELECT AVG(oi.price) as average_order_value
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation pct 
            ON p.product_category_name = pct.product_category_name
        WHERE pct.product_category_name_english LIKE '%electronics%' 
           OR pct.product_category_name_english LIKE '%eletronicos%'
           OR p.product_category_name LIKE '%eletronicos%'
           OR p.product_category_name LIKE '%informatica%'
    """
}
```

### 2. Enhanced Schema Description (`backend/database/queries.py`)

Added important notes at the top of schema description:

```
IMPORTANT NOTES:
1. Product categories are stored in PORTUGUESE in the 'products' table
2. ALWAYS use the 'product_category_name_translation' table to handle English category names
3. When filtering by category in English (e.g., 'electronics', 'furniture'), use:
   - JOIN with product_category_name_translation table
   - Use LIKE '%keyword%' for flexible matching
   - Check both English translation AND Portuguese names
4. Common category mappings:
   - electronics → eletronicos, informatica_acessorios
   - furniture → moveis_decoracao
   - toys → brinquedos
   - books → livros_tecnicos, livros_interesse_geral
```

### 3. Updated SQL Generation Prompt (`backend/llm/groq_client.py`)

Added critical rules to the system prompt:

```
CRITICAL RULES:
1. Product categories are in PORTUGUESE in the database
2. When user mentions category names in ENGLISH (e.g., electronics, furniture, toys):
   - ALWAYS JOIN with product_category_name_translation table
   - Use: LEFT JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
   - Filter using: WHERE pct.product_category_name_english LIKE '%keyword%'
   - Also check Portuguese names as fallback
3. Use LIKE with wildcards for flexible category matching
4. Common mappings: electronics→eletronicos/informatica, furniture→moveis, toys→brinquedos
```

## How It Works Now

### Translation Table Structure

The `product_category_name_translation` table maps Portuguese to English:

| product_category_name (PT) | product_category_name_english (EN) |
|----------------------------|-----------------------------------|
| eletronicos                | electronics                       |
| moveis_decoracao           | furniture_decor                   |
| informatica_acessorios     | computers_accessories             |
| brinquedos                 | toys                              |

### Query Generation Process

1. **User asks in English:** "What is the average order value for electronics?"
2. **SQL Agent recognizes:** English category name mentioned
3. **Generates query with:**
   - JOIN to translation table
   - LIKE matching on English column
   - Fallback to Portuguese names
4. **Executes successfully:** Returns actual data

### Example Corrected Query

**User Query:** "What is the average order value for items in the electronics category?"

**Generated SQL (After Fix):**
```sql
SELECT AVG(oi.price) as average_order_value
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation pct 
    ON p.product_category_name = pct.product_category_name
WHERE pct.product_category_name_english LIKE '%electronics%' 
   OR p.product_category_name LIKE '%eletronicos%'
   OR p.product_category_name LIKE '%informatica%'
```

**Result:** Returns actual average value (e.g., $125.50)

## Benefits

1. ✅ **Handles English queries:** Users can ask in English naturally
2. ✅ **Handles Portuguese queries:** Still works with Portuguese names
3. ✅ **Flexible matching:** LIKE operator catches variations
4. ✅ **Fallback logic:** Checks both English and Portuguese
5. ✅ **Better examples:** LLM learns from correct patterns
6. ✅ **Clear guidance:** Explicit rules in prompts

## Common Category Mappings

| English | Portuguese | Alternative Portuguese |
|---------|-----------|----------------------|
| electronics | eletronicos | informatica_acessorios |
| furniture | moveis_decoracao | moveis_sala, moveis_quarto |
| toys | brinquedos | - |
| books | livros_tecnicos | livros_interesse_geral |
| sports | esporte_lazer | - |
| beauty | beleza_saude | perfumaria |
| fashion | moda_bolsas_e_acessorios | - |
| home | casa_conforto | utilidades_domesticas |

## Testing

### Test Queries

1. **Electronics:**
   - "What is the average order value for electronics?"
   - "Show me top selling electronics products"
   - "How many electronics orders were placed?"

2. **Furniture:**
   - "What's the revenue from furniture sales?"
   - "List furniture products with highest ratings"
   - "Average price of furniture items"

3. **Mixed:**
   - "Compare sales between electronics and furniture"
   - "Which category has more orders: toys or books?"

### Expected Behavior

- All queries should return actual data (not null)
- Both English and Portuguese category names should work
- Partial matches should work (e.g., "electron" matches "electronics")

## Files Modified

1. **`backend/config.py`**
   - Added 2 new SQL examples with translation table usage
   - Updated existing example to use translation

2. **`backend/database/queries.py`**
   - Enhanced schema description with translation notes
   - Added common category mappings

3. **`backend/llm/groq_client.py`**
   - Updated SQL generation prompt with critical rules
   - Added explicit translation table instructions

## Future Enhancements

- [ ] Add more category mappings to documentation
- [ ] Create a category lookup function
- [ ] Add fuzzy matching for misspelled categories
- [ ] Support for multiple languages beyond PT/EN
- [ ] Cache translation mappings for faster queries

---

**Status:** ✅ Implemented and Tested
**Date:** November 9, 2024
**Impact:** High - Fixes critical issue with category-based queries
