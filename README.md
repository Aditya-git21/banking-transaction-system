# High-Availability Banking Transaction System

# High-Availability Banking Transaction System (Zero Data Loss)

## Overview
This project implements a **serverless banking transaction system** on AWS that guarantees **exactly-once execution**, **strong consistency**, and **automatic rollback** in case of failures.

The system is designed using the **Saga Pattern**, a common approach for handling distributed transactions in large-scale financial systems.

---

## Problem Statement
In distributed systems, transaction flows such as money transfers can fail partially (for example, debit succeeds but credit fails), leading to data inconsistency and financial risk.

This project addresses that problem by ensuring:
- Either the entire transaction completes successfully, or
- The system safely rolls back to the original state with **zero data loss**

---

## Architecture
The system follows a serverless, event-driven architecture:

- **AWS Step Functions** orchestrate the transaction flow
- **AWS Lambda** functions handle debit, credit, and rollback operations
- **Amazon RDS (PostgreSQL)** provides strong consistency using ACID transactions

---

## AWS Services Used
- AWS Lambda (Debit, Credit, Rollback)
- AWS Step Functions
- Amazon RDS (PostgreSQL)
- AWS IAM
- Amazon CloudWatch

---

## Transaction Flow (Saga Pattern)

1. A transaction request is received by the Step Functions state machine
2. **Debit Lambda**
   - Validates account balance
   - Performs idempotent debit operation
3. **Credit Lambda**
   - Credits the destination account
4. If the credit step fails:
   - **Rollback Lambda** is triggered automatically
   - The debited amount is restored
5. The transaction ends in one of two states:
   - **Success**: Debit and Credit completed
   - **Safe Failure**: Rollback executed and system restored

---

## Key Features
- Exactly-once processing using idempotency keys
- Strong consistency with database transactions
- Automatic rollback using compensating transactions
- Retry and failure handling through Step Functions
- Fully serverless and scalable design
- Observability through CloudWatch logs

---

## Failure Handling
The system is designed to handle partial failures safely:
- Any failure in downstream steps triggers a rollback
- The system always returns to a consistent state
- Duplicate or partial transactions are prevented

This guarantees **zero financial data loss**.

---

## Security and Reliability
- IAM roles configured with least-privilege access
- Stateless Lambda functions for high availability
- Controlled retries and timeouts at the orchestration layer
- Secure database connectivity

---

## Project Status
- Core transaction system implemented
- End-to-end success and failure scenarios validated
- Ready for extension and production hardening

---

## Possible Enhancements
- API Gateway for external access
- Authentication using JWT or Amazon Cognito
- AWS Secrets Manager for secure credential storage
- CloudWatch alarms and metrics
- Performance and cost optimization

