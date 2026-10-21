# Persuasive Visualizations: Write-up

**Proposition:** Africa is the future of the world's population.

**Dataset:** World Bank population indicators (`health.csv`), 1960–2020.
"Africa" means the World Bank's **Sub-Saharan Africa** region, compared with the other six world regions.

**Files:** `project_08_v2.py` builds `page1_for_08v2.png`, `page2_against_08v2.png`, and `persuasive_visualizations_08v2.pdf`.

---

## Page 1: For ("Africa Is the World's Future")

### Chart 1: Population growth since 1960

| Technique | How it's used |
|---|---|
| Indexing to a base year | Every region starts at 100 in 1960. Africa ends at **5.0x**, East Asia at **2.3x**. |
| What it hides | Africa started much smaller (~227M people vs. 1B+ in East Asia), so it is still far behind in actual size. |
| Selective highlighting | Only Africa is colored; every other region is gray. |

### Chart 2: Share of the world's children, 2000–2020

| Technique | How it's used |
|---|---|
| Truncated y-axis | The axis starts at 15%, not 0%, so 16% to 24% looks like a steep climb. |
| Zoomed time window | Only the last 20 years are shown, when the rise is steepest. |
| Emphasized crossover | A dot marks the year (2019) Africa passes East Asia, even though they differ by less than one point. |
| Loaded wording | "Soared" in the subtitle. |

**Color:** Green for Africa. Green suggests healthy, positive growth.

---

## Page 2: Against ("Africa's Boom Is Overstated")

### Chart 1: Population on a log scale

| Technique | How it's used |
|---|---|
| Logarithmic scale | Steady growth looks like a calm straight line, so Africa's five-fold rise looks ordinary. |
| What it hides | On a normal scale, Africa is catching up with Asia quickly. |
| Grouping by color | East and South Asia share one blue, so they read as one big "Asia" (4.2B vs. Africa's 1.14B). |
| De-emphasis | Africa is drawn in gray, so it fades into the background. |

### Chart 2: Africa's growth rate, 2010–2020

| Technique | How it's used |
|---|---|
| Truncated y-axis | The axis only spans 2.60% to 2.80%, so a tiny 0.14-point drop looks like a crash. |
| Cherry-picked window | Starts right at the 2011 peak. |
| What it hides | Africa still grows about **2.5x faster** than the world average (1.0%). |
| No comparison | Other regions are left out, so there is nothing to measure the drop against. |
| Loaded wording | "And falling" and "the boom has already peaked." |

**Color:** Red for the falling line (alarm, decline). Blue for Asia (calm, stable).

---

## Across Both Pages

- **Same data, opposite stories.** Both top charts use the same population numbers. Indexing makes Africa look explosive; the log scale makes it look ordinary.
- **Color sets the mood.** Green means good growth on page 1. On page 2, blue means stability and red means decline.
- **Titles tell you what to think.** Every title states the conclusion before you read the chart.
- **The data itself is honest.** Every number is accurate and every axis is labeled. The persuasion comes from scale, time window, color and emphasis, not from fake data.
