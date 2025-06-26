# CompTIA Quiz Tools Usage Guide

This guide explains the order and purpose of each script in the `tools` directory for importing, auditing, and refining CompTIA A+ quiz questions.

---

## 1. Import New Questions from PDF

**Script:** `pdf_question_importer.py`

- **Purpose:** Extracts questions from a provided PDF, categorizes them, deduplicates, and writes them to a staging JSON file (e.g., `new_questions_staging.json`).
- **Usage:**
  ```bash
  python pdf_question_importer.py
  ```
- **Review:** Manually review the staging file for any parsing or categorization issues before merging.

---

## 2. Validate Question Structure

**Script:** `validate_questions.py`

- **Purpose:** Checks all topic JSON files for structural issues or malformed questions.
- **Usage:**
  ```bash
  python validate_questions.py
  ```

---

## 3. Audit Question Categorization

**Script:** `audit_question_topics.py`

- **Purpose:** Scans all questions and compares their current topic to the suggested topic (based on keyword weights), generating a report of mismatches (`topic_audit_report.txt`).
- **Usage:**
  ```bash
  python audit_question_topics.py
  ```

---

## 4. Generate Recategorization Moves

**Script:** `generate_recategorization.py`

- **Purpose:** Reads the audit report and generates a list of move operations (and deletions, if needed) for questions that should be recategorized.
- **Usage:**
  ```bash
  python generate_recategorization.py
  ```
- **Output:** The moves/removes list is written to a file (e.g., `moves_for_apply.txt`).

---

## 5. Apply Categorization Changes

**Script:** `apply_categorization_changes.py`

- **Purpose:** Moves or deletes questions based on the moves/removes list. Updates all topic JSON files, resequences IDs, and performs deduplication.
- **Usage:**
  1. Copy the generated moves/removes list from `moves_for_apply.txt` into the `REMOVES_AND_MOVES` variable in `apply_categorization_changes.py`.
  2. Run:
     ```bash
     python apply_categorization_changes.py
     ```

---

## 6. Re-Audit and Validate

- After applying changes, re-run `audit_question_topics.py` and `validate_questions.py` to confirm all questions are correctly categorized and valid.

---

## Optional: Comprehensive Audit for Reporting

**Script:** `question_topic_audit.py`

- **Purpose:** Performs a global audit and writes a detailed categorization review to `categorization_review_GLOBAL.md`.
- **Usage:**
  ```bash
  python question_topic_audit.py
  ```

---

## Typical Workflow Summary

1. `pdf_question_importer.py` — Import and stage new questions.
2. `validate_questions.py` — Validate all questions.
3. `audit_question_topics.py` — Identify mismatches in categorization.
4. `generate_recategorization.py` — Generate moves/removes list.
5. Copy moves/removes to `apply_categorization_changes.py`.
6. `apply_categorization_changes.py` — Apply changes to topic files.
7. `audit_question_topics.py` & `validate_questions.py` — Confirm everything is correct.
8. Optionally, run `question_topic_audit.py` for a comprehensive report.

---

**Note:**
- Always back up your data before running scripts that modify topic files.
- Manual review is recommended after each major step, especially before and after applying categorization changes.
