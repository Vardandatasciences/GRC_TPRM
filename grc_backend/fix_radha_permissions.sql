-- Fix permissions for radha.sharma user in tprm_integration database
-- Run this in MySQL: mysql -u admin -p tprm_integration < fix_radha_permissions.sql

USE tprm_integration;

-- Check current permissions
SELECT 
  UserId, UserName, Email,
  ListContracts, ContractDashboard, CreateContract, UpdateContract, DeleteContract,
  IsActive
FROM rbac_tprm 
WHERE UserId = 1 AND UserName = 'radha.sharma';

-- Update all contract permissions to 1 (enabled)
UPDATE rbac_tprm 
SET 
  ListContracts = 1,
  ContractDashboard = 1,
  CreateContract = 1,
  UpdateContract = 1,
  DeleteContract = 1,
  ApproveContract = 1,
  RejectContract = 1,
  ArchiveContract = 1,
  RenewContract = 1,
  AmendContract = 1,
  IsActive = 'Y'
WHERE UserId = 1;

-- Verify the update
SELECT 
  UserId, UserName, Email,
  ListContracts, ContractDashboard, CreateContract, UpdateContract, DeleteContract,
  IsActive
FROM rbac_tprm 
WHERE UserId = 1 AND UserName = 'radha.sharma';

-- Show confirmation message
SELECT 'Permissions updated successfully for radha.sharma!' AS Status;


