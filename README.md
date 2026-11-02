# 🎓 Scholarship Advisory — Rule-Based System

A Streamlit web app that uses a **rule-based system** to help a university scholarship committee decide whether an applicant should receive a full scholarship, a partial scholarship, be sent for review, or be rejected.

**BSD3513 Introduction to Artificial Intelligence — Lab Report 3**
**Name:** MOK KER QIN · **Student ID:** SD24032

- **Live app:** <https://your-app.streamlit.app>
- **GitHub repository:** <https://github.com/your-username/scholarship-rbs>

---

## Features

### 1. Applicant facts
Enter the applicant's six facts in the sidebar: CGPA, monthly family income, co-curricular score, community service
hours, current semester and number of disciplinary actions. The values are shown as cards on the main page. Click
**Evaluate** to run the rules.

![Applicant facts](cover.png)

### 2. Decision and matched rules
The decision is shown in a colour-coded banner (green = `AWARD_FULL`, blue = `AWARD_PARTIAL`, yellow = `REVIEW`,
red = `REJECT`) together with the reason and the winning rule. Below it, the table lists every rule that matched
the applicant, ranked by priority. When more than one rule matches, the rule with the highest priority decides.

![Decision and matched rules](decision.png)

### 3. Rule-by-rule check
This section explains *why* the decision was made. Each rule is marked **Matched** or **Not matched**, and opening it
shows every condition, the applicant's value and whether the condition is true or false. A rule is matched only when
all of its conditions are true.

![Rule-by-rule check](check.png)

### 4. Editable rules
The **Rules** tab holds the rule base as JSON, loaded with the five rules from the lab brief. The rules can be edited
or replaced without changing the code. If the JSON is invalid, an error is shown and the default rules are used.

![Rules tab](rules.png)

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
