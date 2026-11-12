# Assignment · Solving the Relational Problem

**CE 502 · Week 9** · Individual · peer-graded · 20 points
**Report:** 1,200–1,800 words, plus at least one architecture diagram · **Due:** [date] · **Peer reviews due:** [date]
**Lessons:** 9-1 Scaling Relational Systems, 9-2 NoSQL Data Models, 9-3 MongoDB and Cassandra (and Weeks 1–8 where they help)

## The question

One organisation's data and workload are growing faster than its relational database. Should it **stretch the relational system** with bigger hardware, replication, sharding, partitioning or distributed SQL? Should it **adopt NoSQL** for part of its data? Or should it **combine both** (polyglot persistence)? You act as its data architect and argue your answer.

## Choose your organisation

Choose **one real organisation** whose data platform is described in public sources: engineering blogs, conference talks, case studies, annual reports or news articles. Good examples are a bank, a ride-hailing or delivery app, a streaming service, an online shop, a telecom operator, a public service or a university. Companies such as Uber, Netflix, Discord, Shopify, Spotify and Airbnb publish detailed engineering blogs.

- Use **at least three** sources and cite each one (author or organisation, title, date, URL).
- Where the sources do not give a number, make a reasonable estimate and **label it as an estimate**. Do not invent facts about the organisation.
- If you cannot find enough public material, use the fictional scenario **BalkanRide** below and say so in your introduction. The maximum mark is the same.

### Fallback scenario: BalkanRide (fictional)

BalkanRide is a ride-hailing and food-delivery app operating in five Balkan countries. It started 6 years ago on a single PostgreSQL server. Today it has:

- 4 million registered users and 120,000 drivers;
- 1.5 million trips and deliveries per day, peaking at 900 per second on Friday evenings;
- GPS pings from active drivers every 4 seconds, up to 30,000 writes per second;
- in-app chat messages between riders and drivers;
- payments and driver payouts, which must never be lost or counted twice;
- a product team that adds new delivery types (groceries, pharmacy, parcels) every few months, each with different item attributes.

Problems this year:

- the primary server runs at 85% CPU at peak;
- the GPS table grows by 2 billion rows per month;
- a 40-minute outage in one data centre made the app unusable in all five countries;
- schema migrations for new delivery types take weeks.

## What your report must contain

1. **Workload analysis.** Split the organisation's data into workloads, for example payments, orders, location data, messages, catalogue and analytics. For each workload, give its access pattern (reads vs writes, by key or by query), its volume and growth, and how consistent it must be.
2. **Recommendation per workload.** Choose a database type and product, and justify the choice with course concepts: scaling up vs out, replication, sharding, the aggregate model, ACID vs BASE, CAP. **At least one workload must stay relational or use distributed SQL**; explain why.
3. **Data models for two workloads.** Use whichever fits each workload:
   - relational tables with keys;
   - an example JSON document;
   - a Cassandra table with its partition and clustering keys, designed query-first, with the query it serves.
4. **Scaling and availability plan.** Give the sharding or partition keys, the replication factor and the placement across regions or data centres, and the failover approach. Explain what your design does during a **network partition** between two data centres (CAP, Lesson 9-1).
5. **Consistency choices.** For the most critical workload (for example payments) and the highest-volume one (for example location data), state the isolation level, write concern or consistency level you would use, and the trade-off. Use R + W > RF where it applies.
6. **Migration and risk.** How to move from today's system without downtime, and the impact on staff skills, existing code and operations.

**Deliverables:**

- one PDF report of 1,200–1,800 words, with at least one architecture diagram and a reference list;
- a one-slide summary, which may be shown in class.

## Peer review

After the deadline you receive **three** classmates' reports. For each one:

1. Score every criterion of the rubric below.
2. Write **two strengths** and **one concrete suggestion**.
3. Do not deduct points because the author chose a different product than you would, if the choice is justified.

Your instructor checks a sample of the reviews and moderates scores that differ widely. A careless review (scores with no comments) can cost you up to 2 points on your own mark.

## Rubric (20 points)

| Criterion | 4 | 3 | 2 | 0 |
|---|---|---|---|---|
| **Workload analysis** | All major workloads, each with access pattern, volume and consistency need, supported by cited sources or labelled estimates | All major workloads, one dimension weak | Some workloads missing or vague | Missing |
| **Technology choices** | Each choice justified with course concepts; trade-offs stated; at least one relational or distributed SQL workload argued | Justified, but one trade-off missing | Choices with generic justification ("NoSQL scales") | Missing or unjustified |
| **Data models** | Two correct, query-driven models with keys; for Cassandra, the query each table serves | Two models, one with a minor error | Models present but not query-driven or with errors | Missing |
| **Scaling, availability and CAP** | Clear sharding/replication plan and placement; partition behaviour explained for this design | Plan clear; CAP explained in general terms only | Plan incomplete; CAP only named | Missing |
| **Consistency, migration and clarity** | Correct consistency choices with trade-offs; realistic migration; clear writing, diagram and references | Mostly correct; one part thin | Partly correct or unclear; few sources | Missing |

## Academic integrity

AI tools may help you with language and with understanding sources. They must not write the report or invent sources or figures. Every claim about the organisation must come from a cited source or be labelled as your estimate. List any AI use in a short note at the end of the report.
