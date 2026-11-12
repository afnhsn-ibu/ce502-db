# Data Warehouse Design Project

**CE 502 · launched in Week 7** · Individual or pairs · 20 points
**Due:** [date, set by your instructor]
**Supports:** Lessons 7-1 to 7-3, especially the Lesson 7-2 food-delivery scenario and the measures slide (`l72-measures`)

## The task

Choose a domain you know and design a data warehouse that answers real management questions. Suggested domains:

- university enrolments
- hospital admissions
- public transport ridership
- a library's loans
- an online shop
- energy use of buildings
- football match statistics

You do not build a production system. You produce a **design** and **prove it with SQL** on a small sample in the course PostgreSQL container.

## What to deliver

A PDF report of 4–6 pages plus one `.sql` file that creates your schema, inserts the sample and runs your five queries.

1. **Business context** (half a page):
   - Who are the decision makers, and what decisions will the warehouse support?
   - Write three to five business questions.
   - List the operational (OLTP) source systems the data comes from.
2. **Facts and grain.**
   - Name your fact table(s).
   - State the **grain** in one sentence: "one row per …".
   - List the measures, and mark each one **additive**, **semi-additive** or **non-additive**, with one sentence of justification. For example, a stock level cannot be summed over time, and an average grade must be recomputed, not summed.
3. **Dimensions.** At least **four** dimensions, each with three or more attributes and at least one **hierarchy**, for example day → month → quarter → year.
4. **Star schema diagram.**
   - Boxes and lines, with the fact table in the middle and keys and measures shown.
   - In one paragraph, say whether any dimension should be snowflaked, and why or why not.
5. **Five OLAP queries in SQL.** Write five business questions and the SQL that answers each on your star schema. Together they must use:
   - a **roll-up**;
   - a **drill-down**;
   - a **slice or dice**;
   - a **pivot**;
   - at least one of **`ROLLUP`, `CUBE` or `GROUPING SETS`**.
6. **ETL plan.** For each source:
   - what you extract;
   - how you clean and transform it, with at least **two concrete integration problems** (different codes for the same thing, currencies, renamed courses, duplicates, missing dates…);
   - how often you load;
   - how you **check** that a load is correct, as with the totals check in Practice 7.
7. **Materialisation.** Which one or two cuboids would you materialise, and why? When are they refreshed?
8. **Sample run.** Create the schema in PostgreSQL, insert **20–200 sample rows** (generated or invented, clearly marked as such), and include the output of your five queries.

## How to run your SQL in the course container

Save `dw_project.sql` in the kit folder, for example in `labs/week07/`, on your laptop. Then:

```bash
docker exec ce502-postgres createdb -U postgres dwproject
docker exec -w /kit/labs/week07 ce502-postgres psql -U postgres -d dwproject -f dw_project.sql
```

Start the file with `DROP SCHEMA IF EXISTS project CASCADE; CREATE SCHEMA project; SET search_path = project;` so that it can be run again from scratch.

## Rubric (20 points)

| Criterion | 4 – excellent | 3 – good | 2 – partial | 0 – missing |
|---|---|---|---|---|
| **Facts, grain and measures** | Grain stated precisely and used consistently; every measure correctly typed and justified | Grain clear; one measure mistyped | Grain vague ("one row per sale" without saying what a sale is) or several measures mistyped | Missing |
| **Dimensions and hierarchies** | 4+ dimensions, sensible attributes, a real hierarchy in most of them | 4 dimensions, hierarchies thin | Fewer than 4 dimensions or no hierarchy | Missing |
| **Schema diagram and snowflake decision** | Clear diagram matching the SQL; snowflake decision justified | Diagram clear, justification weak | Diagram and SQL disagree, or no justification | Missing |
| **OLAP queries and SQL** | Five meaningful questions; all five required operations; SQL runs and output shown | One required operation missing, or one query fails | Several operations missing, or SQL does not run | Missing |
| **ETL, materialisation and sample run** | Two concrete integration problems, a validation check, justified materialisation, sample outputs shown | One of these weak | Generic ETL ("clean the data") and no check | Missing |

Pairs submit one report and both names. Both partners must be able to explain every part.

## Example outline (university enrolments)

- **Fact:** `fact_enrolment`. Grain: one student in one course section in one semester.
- **Measures:**
  - `credits`: additive;
  - `grade_points`: non-additive, so average it and never sum it across students;
  - `enrolment_count`: additive, always 1 per row, which makes counting easy.
- **Dimensions:**
  - `dim_semester` (term → academic year);
  - `dim_course` (course → department → faculty, level);
  - `dim_student` (programme, entry year, nationality);
  - `dim_instructor` (title, department).
- **Questions:**
  - credits taught per faculty per year (roll-up);
  - drill from faculty to course for the faculty that grew most;
  - slice on the latest semester;
  - pivot of nationality × faculty;
  - `ROLLUP (faculty, department)` with subtotals.
- **ETL problems:** course codes renamed in 2023; grades on different scales in two programmes.

## Academic integrity

You may use AI tools to improve the language of your report. The design decisions, the SQL and the explanations must be your own, and you must be able to explain them if asked. Declare any help at the end of the report.
