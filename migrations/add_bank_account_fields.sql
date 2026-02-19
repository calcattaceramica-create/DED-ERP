-- Add new fields to bank_accounts table
-- Date: 2026-02-12
-- Description: Add account_type, opening_balance, and notes fields to bank_accounts
-- Database: erp_system.db (not instance/erp.db)

-- Add account_type column
ALTER TABLE bank_accounts ADD COLUMN account_type VARCHAR(20) DEFAULT 'current';

-- Add opening_balance column
ALTER TABLE bank_accounts ADD COLUMN opening_balance FLOAT DEFAULT 0.0;

-- Add notes column
ALTER TABLE bank_accounts ADD COLUMN notes TEXT;

-- Update existing records to set opening_balance equal to current_balance
UPDATE bank_accounts SET opening_balance = current_balance WHERE opening_balance IS NULL OR opening_balance = 0;

-- Update existing records to set default account_type
UPDATE bank_accounts SET account_type = 'current' WHERE account_type IS NULL;

