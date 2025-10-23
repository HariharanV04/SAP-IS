-- Migration SQL for all iflow tables
-- Execute this in Supabase SQL Editor
-- Order matters due to foreign key dependencies: packages -> assets & components

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- 1. IFLOW_PACKAGES TABLE (must be created first due to foreign keys)
-- ============================================================================

DROP TABLE IF EXISTS iflow_assets CASCADE;
DROP TABLE IF EXISTS iflow_components CASCADE;
DROP TABLE IF EXISTS iflow_packages CASCADE;

CREATE TABLE public.iflow_packages (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  package_name TEXT NOT NULL,
  version TEXT,
  description TEXT,
  iflw_xml TEXT,
  description_embedding vector(1536) NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT iflow_packages_pkey PRIMARY KEY (id)
) TABLESPACE pg_default;

-- Indexes for iflow_packages
CREATE INDEX idx_iflow_packages_package_name ON iflow_packages(package_name);
CREATE INDEX idx_iflow_packages_version ON iflow_packages(version);
CREATE INDEX idx_iflow_packages_created_at ON iflow_packages(created_at);

-- Vector index for description embedding
CREATE INDEX idx_iflow_packages_description_embedding 
  ON iflow_packages USING ivfflat (description_embedding vector_cosine_ops)
  WITH (lists = 100);


-- ============================================================================
-- 2. IFLOW_ASSETS TABLE
-- ============================================================================

CREATE TABLE public.iflow_assets (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  package_id UUID NULL,
  file_name TEXT NOT NULL,
  file_type TEXT NULL,
  description TEXT NULL,
  content TEXT NULL,
  content_embedding vector(1536) NULL,
  description_embedding vector(1536) NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT iflow_assets_pkey PRIMARY KEY (id),
  CONSTRAINT iflow_assets_package_id_fkey FOREIGN KEY (package_id) 
    REFERENCES iflow_packages(id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Indexes for iflow_assets
CREATE INDEX idx_iflow_assets_package_id ON iflow_assets(package_id);
CREATE INDEX idx_iflow_assets_file_type ON iflow_assets(file_type);
CREATE INDEX idx_iflow_assets_file_name ON iflow_assets(file_name);
CREATE INDEX idx_iflow_assets_created_at ON iflow_assets(created_at);

-- Vector indexes for similarity search
CREATE INDEX idx_iflow_assets_content_embedding 
  ON iflow_assets USING ivfflat (content_embedding vector_cosine_ops)
  WITH (lists = 100);
  
CREATE INDEX idx_iflow_assets_description_embedding 
  ON iflow_assets USING ivfflat (description_embedding vector_cosine_ops)
  WITH (lists = 100);


-- ============================================================================
-- 3. IFLOW_COMPONENTS TABLE
-- ============================================================================

CREATE TABLE public.iflow_components (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  package_id UUID NULL,
  component_id TEXT NOT NULL,
  activity_type TEXT NULL,
  description TEXT NULL,
  complete_bpmn_xml TEXT NULL,
  properties JSONB NULL,
  related_scripts JSONB NULL,
  code_embedding vector(1536) NULL,
  description_embedding vector(1536) NULL,
  activity_type_embedding vector(1536) NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT iflow_components_pkey PRIMARY KEY (id),
  CONSTRAINT iflow_components_package_id_fkey FOREIGN KEY (package_id) 
    REFERENCES iflow_packages(id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Indexes for iflow_components
CREATE INDEX idx_iflow_components_package_id ON iflow_components(package_id);
CREATE INDEX idx_iflow_components_component_id ON iflow_components(component_id);
CREATE INDEX idx_iflow_components_activity_type ON iflow_components(activity_type);
CREATE INDEX idx_iflow_components_created_at ON iflow_components(created_at);

-- Vector indexes for similarity search
CREATE INDEX idx_iflow_components_code_embedding 
  ON iflow_components USING ivfflat (code_embedding vector_cosine_ops)
  WITH (lists = 100);
  
CREATE INDEX idx_iflow_components_description_embedding 
  ON iflow_components USING ivfflat (description_embedding vector_cosine_ops)
  WITH (lists = 100);
  
CREATE INDEX idx_iflow_components_activity_type_embedding 
  ON iflow_components USING ivfflat (activity_type_embedding vector_cosine_ops)
  WITH (lists = 100);


-- ============================================================================
-- TABLE COMMENTS
-- ============================================================================

COMMENT ON TABLE iflow_packages IS 'Stores iFlow package metadata';
COMMENT ON TABLE iflow_assets IS 'Stores iFlow package file assets with vector embeddings';
COMMENT ON TABLE iflow_components IS 'Stores iFlow components/activities with vector embeddings';


-- ============================================================================
-- OPTIONAL: ROW LEVEL SECURITY (uncomment if needed)
-- ============================================================================

-- ALTER TABLE iflow_packages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE iflow_assets ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE iflow_components ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Enable read access for all users" ON iflow_packages FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON iflow_assets FOR SELECT USING (true);
-- CREATE POLICY "Enable read access for all users" ON iflow_components FOR SELECT USING (true);

