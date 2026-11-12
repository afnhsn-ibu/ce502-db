# CE 502 · Big Data Project – An Architecture Proposal

**Launched in Week 8** · Individual or pairs · 20 points · peer-graded
**Report due:** [date] · **Peer reviews due:** [date + 1 week]
**Lessons:** 8-1 What Is Big Data?, 8-2 The V's and the Challenges, 8-3 Big Data Architecture

## 1. The task

Write the proposal a data architect writes *before* anything is built: a realistic big data system for an organisation of your choice, with every design decision justified. You build nothing and write no code. The value of the report is in the reasoning, the numbers and the trade-offs.

Ideas, or choose your own:

- a city's smart-parking network;
- a mobile operator's network monitoring;
- an online shop's clickstream and recommendations;
- a hospital's patient-monitoring sensors;
- a university learning platform's activity logs;
- a logistics company's fleet tracking;
- a national tax authority's e-invoicing system.

An organisation you know, for example from work or a family business, makes a stronger report. Do not use NYC taxis: you already analysed them in Practice 8.

## 2. What to deliver

One PDF of **5–7 pages**, plus diagrams and tables, with these nine sections.

1. **Problem and value** (half a page). The organisation, the decision or service the system supports, and how you will measure success. Example: "reduce average search time for parking from 12 to 5 minutes".
2. **Data sources.** At least **three** sources. For each one give:
   - its format: structured, semi-structured or unstructured;
   - its size per day, with the calculation;
   - its arrival pattern: continuous, hourly, nightly or on demand.
3. **The ten V's.** A table with all ten V's: volume, velocity, variety, veracity, value, variability, visualisation, validity, vulnerability, volatility. For each, say how it applies, how big the issue is (low, medium or high), and how your design handles it. Use numbers where you can; estimates are fine if you show the calculation.
4. **Architecture.** A diagram with all the layers from Lesson 8-3: sources, ingestion, collector, processing, storage, query and analysis, visualisation, plus security and monitoring across all layers. For each layer, name a **concrete tool** and justify it against **one alternative**, for example "Kafka rather than RabbitMQ because …".
5. **Batch, stream or both.** Choose, and justify with your use case and latency needs. If you choose both, explain lambda or kappa.
6. **Storage estimate.** Raw data per day × retention period × replication factor (× compression) = total. Show the arithmetic and state your assumptions.
7. **Security and privacy.** Cover:
   - which personal data you hold, and who may see what;
   - encryption at rest and in transit;
   - masking or anonymisation;
   - the regulations that apply: GDPR, and in North Macedonia the Law on Personal Data Protection (2020) [check the current text].
8. **Data quality and monitoring.** Three automated checks with thresholds, for example "share of rows with a missing sensor ID < 1% per hour, else alert". Practice 8's Q3 is a model.
9. **Risks.** The top three risks (technical, cost, legal or organisational), each with how you reduce it.

Cite every product claim and every statistic with a source and a year.

## 3. Rubric (20 points)

| Criterion | 4 · Excellent | 3 · Good | 2 · Partial | 0 · Missing |
|---|---|---|---|---|
| **Problem, sources and value** (sections 1–2) | Clear, measurable value; 3+ sources with format, size per day (calculated) and arrival pattern | Clear value; sources complete but one size not calculated | Vague value, or fewer than 3 sources | Missing |
| **Ten V's analysis** (section 3) | All ten, specific to the case, rated, each with a design response and numbers where possible | All ten, mostly specific | Some V's missing, or generic text that could describe any system | Missing |
| **Architecture and tools** (section 4) | Every layer present; a real tool per layer, each compared with an alternative; security and monitoring shown across layers | All layers, some comparisons missing | Layers missing, or tools named without justification | Missing |
| **Processing choice and storage estimate** (sections 5–6) | Batch/stream choice justified by concrete latency needs; storage arithmetic correct, with stated assumptions | Sound choice; small arithmetic or assumption gaps | Choice not justified, or estimate wrong by an order of magnitude | Missing |
| **Security, quality and risks** (sections 7–9) | Specific privacy measures and regulation; 3 automated checks with thresholds; 3 risks with mitigations | Mostly specific; one element weak | Generic statements ("we will encrypt the data") | Missing |

## 4. Peer review

You review **two** reports, assigned through the course platform, using the rubric above. For each review:

- give a score per criterion with one sentence of reasoning that quotes or points to the part of the report you mean;
- give **two strengths** and **one concrete improvement**, such as "Section 6 multiplies by 3 for replication but forgets that Parquet compresses; state a compression ratio".

The instructor moderates the peer marks. A review that ignores the rubric, or gives every criterion 4 without reasons, loses the review's share of the grade.

## 5. Rules

- **Pairs** submit one report with both names and a short note on who did what. Both students review individually.
- **AI tools** may help with language and with checking arithmetic. Every design decision, number and source must be your own and verifiable. List the tools you used in a declaration at the end.
- **Late submission:** follows the course policy in the syllabus.
