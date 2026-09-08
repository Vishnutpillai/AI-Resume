# Intelligent Resume & Job Matching System

An AI-powered resume and job description analysis platform that evaluates how well a candidate's resume matches a target job description, identifies skill gaps, provides explainable recommendations, optimizes the resume, and recalculates the match score.

The system is designed as an end-to-end production-oriented AI/ML application combining document processing, NLP, semantic matching, scoring, resume optimization, embeddings, LLMs, and API-based deployment.

---

## 🚀 Project Overview

Finding the right job is not only about having the required skills. A resume must also communicate those skills clearly and align with the language, requirements, experience, education, and keywords used in a job description.

The **Intelligent Resume & Job Matching System** automates this process.

The system follows the workflow:

```text
Resume
   ↓
Document Ingestion
   ↓
Text Extraction / OCR
   ↓
Resume Parsing
   ↓
Structured Resume Profile
   ↓
              ┌─────────────────────┐
Job Description → JD Parsing       │
              └─────────────────────┘
                       ↓
                Job Profile
                       ↓
              Matching & Scoring
                       ↓
             Initial Match Score
                       ↓
               Skill Gap Analysis
                       ↓
             Resume Optimization
                       ↓
             Optimized Resume
                       ↓
             Recalculate Score
                       ↓
          Before vs After Analysis