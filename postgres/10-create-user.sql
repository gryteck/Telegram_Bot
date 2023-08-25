-- file: 10-create-user.sql
CREATE ROLE admin WITH PASSWORD 'test';
ALTER ROLE admin WITH LOGIN;