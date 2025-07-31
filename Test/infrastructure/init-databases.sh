#!/bin/bash
set -e

# Создаем базы данных для разных версий
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE morphik_stable;
    CREATE DATABASE morphik_experimental;
    
    -- Добавляем pgvector extension в каждую БД
    \c morphik_stable
    CREATE EXTENSION IF NOT EXISTS vector;
    
    \c morphik_experimental
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL