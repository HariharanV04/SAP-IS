# Database Scripts

All SQL scripts for setting up IMigrate databases (Supabase).

---

## Quick Setup (Run in Order)

### **1. Feedback System**
```bash
# Run in Supabase SQL Editor
# https://supabase.com/dashboard/project/YOUR_PROJECT/sql
```

**File:** `supabase_feedback_schema.sql`  
**Creates:** 6 tables for user feedback collection
- `migration_feedback` - User ratings and feedback
- `documentation_feedback` - Documentation quality feedback
- `component_mapping_feedback` - Component accuracy feedback
- `learned_migration_patterns` - AI-learned patterns
- `platform_connector_mappings` - Platform-specific mappings
- `feedback_analytics` - Analytics view

### **2. Intent Learning System**
**File:** `supabase_intent_training_schema.sql`  
**Creates:** 5 tables for AI pattern learning
- `component_pattern_library` - Learned component patterns
- `intent_training_examples` - Historical training data
- `component_co_occurrence` - Component relationships
- `intent_prompt_versions` - Prompt evolution
- `generation_feedback` - Per-generation feedback

**File:** `supabase_intent_training_seed_data.sql`  
**Seeds:** 45+ component patterns, 5 training examples, 8 co-occurrence patterns

### **3. Job Tracking** (Optional)
**File:** `supabase_job_tracking_schema.sql`  
**Creates:** Job tracking table for persistent job storage

### **4. All-in-One** (Advanced)
**File:** `create_all_tables.sql`  
**Creates:** All tables at once (use if starting fresh)

---

## Files

| File | Purpose | Tables/Functions | Size |
|------|---------|------------------|------|
| `supabase_feedback_schema.sql` | Feedback system | 6 tables | ~9KB |
| `supabase_intent_training_schema.sql` | Intent learning | 5 tables | ~8KB |
| `supabase_intent_training_seed_data.sql` | Seed data | - | ~15KB |
| `supabase_job_tracking_schema.sql` | Job tracking | 1 table | ~3KB |
| `create_all_tables.sql` | All-in-one setup | All tables | ~25KB |
| **`rag_similarity_search_function.sql`** | **RAG similarity search** | **1 RPC function** | **~2KB** |

---

## Usage

### **Option A: Step-by-Step (Recommended)**
```bash
# 1. Open Supabase SQL Editor
# 2. Copy content from supabase_feedback_schema.sql and run
# 3. Copy content from supabase_intent_training_schema.sql and run
# 4. Copy content from supabase_intent_training_seed_data.sql and run
# 5. (Optional) Copy content from supabase_job_tracking_schema.sql and run
```

### **Option B: All-in-One**
```bash
# Copy content from create_all_tables.sql and run once
```

---

## Verification

After running scripts, verify tables exist:

```sql
-- Check feedback tables
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename LIKE '%feedback%';

-- Check intent learning tables
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename LIKE '%pattern%' OR tablename LIKE '%intent%';

-- Check pattern count
SELECT COUNT(*) FROM component_pattern_library;
-- Should return: 45+
```

---

## Updating

**Feedback Schema:**
- Add new columns to `migration_feedback`
- Update constraints as needed
- Re-run relevant sections

**Pattern Library:**
- Add new patterns to `supabase_intent_training_seed_data.sql`
- Re-run seed script (idempotent - uses DELETE then INSERT)

---

## Troubleshooting

### **Error: relation already exists**
```sql
-- Drop existing tables first
DROP TABLE IF EXISTS migration_feedback CASCADE;
DROP TABLE IF EXISTS component_pattern_library CASCADE;
-- Then re-run creation script
```

### **Error: check constraint violation**
```
-- Check your data matches constraints:
-- overall_rating: 1-5
-- component_mapping_accuracy: 1-10
-- confidence_score: 0.0-1.0
```

---

**See `../DEPLOYMENT_GUIDE.md` for full setup instructions**

