-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    email VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create test users with bcrypt hashed passwords
-- Password for fedor: usertest1
-- Password for testuser: testpassword123

-- Note: These are bcrypt hashes for the passwords
INSERT INTO users (id, username, password_hash, email) VALUES 
('user-001', 'fedor', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGdddxyXQRC', 'fedor@example.com'),
('user-002', 'testuser', '$2b$12$GhvMmNVjRW29ulnudl.LbuAnUtN/LzaKthnqMlgKJjLJDs1beQeJq', 'test@example.com')
ON CONFLICT (id) DO NOTHING;