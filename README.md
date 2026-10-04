# AI Expense & Budget Intelligence

### Sequential Multi-Agent Financial Decision Support System

An intelligent personal finance and budgeting application that transforms transaction data into actionable financial insights using a **four-agent sequential workflow**.

The system combines **deterministic Python-based financial analytics** with **AI-powered interpretation and recommendation generation**. It analyzes spending patterns, detects unusual transactions, constructs a financially constrained monthly budget, and produces a prioritized action plan.

---

## 📌 Project Overview

Managing personal finances is not only about recording expenses. The real challenge is understanding:

- Where money is being spent
- Which transactions require attention
- How spending compares with financial constraints
- What a sustainable monthly budget should look like
- What actions should be taken next

**AI Expense & Budget Intelligence** addresses this problem through a specialized multi-agent decision-support pipeline.

Instead of asking one AI model to perform the entire task, the system divides the problem into four specialized agents:

> **Transaction Analysis → Anomaly Detection → Budget Planning → Financial Advisory**

Each downstream agent consumes the intelligence produced by earlier stages.

---

# 🎯 Objectives

The project aims to:

1. Analyze historical transaction data and identify major spending patterns.
2. Detect unusual or high-value transactions using deterministic statistical analysis.
3. Develop a realistic monthly budget using income, target budget, recurring spending, and anomaly information.
4. Generate explainable financial recommendations.
5. Demonstrate how specialized agents can collaborate sequentially to support a financial decision.

---

# 🤖 Multi-Agent Architecture

```text
                         USER
                          │
                          ▼
                 ┌─────────────────┐
                 │ Transaction CSV │
                 │ + Income        │
                 │ + Budget        │
                 └────────┬────────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │ AGENT 1                 │
             │ Transaction Analyst     │
             │                         │
             │ Spending Analysis       │
             └───────────┬─────────────┘
                         │
                         │ Spending Intelligence
                         ▼
             ┌─────────────────────────┐
             │ AGENT 2                 │
             │ Anomaly Detector        │
             │                         │
             │ Statistical Detection   │
             └───────────┬─────────────┘
                         │
                         │ Anomaly Intelligence
                         ▼
             ┌─────────────────────────┐
             │ AGENT 3                 │
             │ Budget Planner           │
             │                         │
             │ Budget Optimization     │
             └───────────┬─────────────┘
                         │
                         │ Budget + Savings Outlook
                         ▼
             ┌─────────────────────────┐
             │ AGENT 4                 │
             │ Financial Advisor       │
             │                         │
             │ Decision Synthesis      │
             └───────────┬─────────────┘
                         │
                         ▼
                ┌────────────────────┐
                │ FINAL ACTION PLAN  │
                │                    │
                │ Prioritized        │
                │ Financial Actions  │
                └────────────────────┘
