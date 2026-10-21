"""
Exports the two figures used in project2_report.html as standalone images:

  for_fivefold.png      FOR: "Sub-Saharan Africa's population has grown five-fold" (page 1, top chart)
  against_asia_gap.png  AGAINST: "Sub-Saharan Africa has never come close to Asia" (page 2, top chart)

Run:  python3 export_report_figures.py
"""
import matplotlib.pyplot as plt

import project_08_v2 as p


def for_fivefold():
    fig, ax = plt.subplots(figsize=(10, 7.2))
    fig.suptitle("Africa Is the World's Future", fontsize=22, fontweight="bold", color=p.GREEN,
                 x=0.04, ha="left", y=0.98)
    fig.text(0.04, 0.915, "No region on Earth is growing like Sub-Saharan Africa.", fontsize=12, color=p.INK)

    pop = p.wide(p.POP)
    indexed = pop[p.REGIONS].div(pop.loc[1960, p.REGIONS]) * 100
    p.highlight_lines(ax, indexed, p.GREEN,
                      {"Middle East & North Africa": 436, "South Asia": 324, "Latin America & Caribbean": 290,
                       "East Asia & Pacific": 226, "North America": 185, "Europe & Central Asia": 139},
                      lambda v: f"{v / 100:.1f}x")
    ax.axhline(100, color=p.MUTED, lw=1, ls="--")
    ax.text(2019, 80, "1960 = 100", ha="right", color=p.MUTED, fontsize=10)
    ax.set_xlim(1960, 2020)
    ax.set_ylim(0, 540)
    ax.set_ylabel("Population, indexed (1960 = 100)")
    p.style(ax, "Sub-Saharan Africa's population has grown five-fold",
            f"Since 1960 it multiplied {indexed.loc[2020, p.SSA] / 100:.1f}x - faster than any other region and "
            f"more than double East Asia's {indexed.loc[2020, 'East Asia & Pacific'] / 100:.1f}x.")

    fig.text(0.04, 0.02, "Source: World Bank population indicators (health.csv), 1960-2020. "
             "Regions are the World Bank's seven geographic regions.", fontsize=8.5, color=p.MUTED)
    fig.tight_layout(rect=(0.02, 0.04, 0.96, 0.91))
    return fig


def against_asia_gap():
    fig, ax = plt.subplots(figsize=(10, 7.2))
    fig.suptitle("Africa's Boom Is Overstated", fontsize=22, fontweight="bold", color=p.BLUE,
                 x=0.04, ha="left", y=0.98)
    fig.text(0.04, 0.915, "Sub-Saharan Africa is still far behind Asia.", fontsize=12, color=p.INK)

    pop = p.wide(p.POP) / 1e6
    label_y = {"East Asia & Pacific": 2600, "South Asia": 1700}
    for name in ["East Asia & Pacific", "South Asia"]:
        ax.plot(pop.index, pop[name], color=p.BLUE, lw=3)
        ax.text(2021, label_y[name], f"{p.SHORT.get(name, name)}\n{pop[name].iloc[-1] / 1e3:.2f}B",
                color=p.BLUE, fontsize=10.5, fontweight="bold", va="center")
    ax.plot(pop.index, pop[p.SSA], color=p.GRAY, lw=2.4)
    ax.text(2021, pop[p.SSA].iloc[-1], f"Sub-Saharan Africa\n{pop[p.SSA].iloc[-1] / 1e3:.2f}B",
            color=p.MUTED, fontsize=10.5, va="center")
    ax.set_yscale("log")
    ax.set_ylim(150, 4000)
    ax.set_yticks([200, 500, 1000, 2000, 4000])
    ax.yaxis.set_major_formatter(p.FuncFormatter(lambda v, _: f"{v / 1e3:g}B" if v >= 1000 else f"{v:.0f}M"))
    ax.yaxis.set_minor_formatter(p.FuncFormatter(lambda v, _: ""))
    ax.set_xlim(1960, 2020)
    ax.set_ylabel("Population (log scale)")
    gap = pop.loc[2020, ["East Asia & Pacific", "South Asia"]].sum() - pop.loc[2020, p.SSA]
    p.style(ax, "Sub-Saharan Africa has never come close to Asia",
            f"In 60 years it never closed the gap: East and South Asia still have {gap / 1e3:.1f} billion more people.")

    fig.text(0.04, 0.02, "Source: World Bank population indicators (health.csv), 1960-2020. "
             "Regions are the World Bank's seven geographic regions.", fontsize=8.5, color=p.MUTED)
    fig.tight_layout(rect=(0.02, 0.04, 0.93, 0.91))
    return fig


if __name__ == "__main__":
    for_fivefold().savefig("for_fivefold.png", dpi=150)
    against_asia_gap().savefig("against_asia_gap.png", dpi=150)
