-- ChainSentinel PostgreSQL Initialization
-- Creates extensions and sets up initial configuration

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE chainsentinel TO chainsentinel;
