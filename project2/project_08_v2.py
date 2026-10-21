"""
DSC 106 Project 2 - Persuasive visualizations (World Bank health/population dataset)

Proposition: "Africa is the future of the world's population."
(Measured with the World Bank's Sub-Saharan Africa region, using its seven world regions.)

Each chart leans on a different persuasive technique:
  Page 1 (FOR)      V1 indexing to a chosen base year     V2 truncated y-axis + zoomed time window   (green = growth is good)
  Page 2 (AGAINST)  V1 logarithmic scale                  V2 truncated y-axis + cherry-picked window (red = decline)
Run:  python3 project_08_v2.py  ->  page1_for_08v2.png, page2_against_08v2.png, persuasive_visualizations_08v2.pdf
"""
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter, PercentFormatter

df = pd.read_csv("health.csv")
df.columns = [c.replace("average_value_", "") for c in df.columns]

POP = "Population, total"
WORKING = "Population ages 15-64, total"
# Children 0-14 = young-age dependency ratio x working-age population
df["children"] = df["Age dependency ratio, young (% of working-age population)"] / 100 * df[WORKING]

SSA = "Sub-Saharan Africa"
REGIONS = [SSA, "South Asia", "East Asia & Pacific", "Europe & Central Asia",
           "Latin America & Caribbean", "Middle East & North Africa", "North America"]
SHORT = {SSA: "Sub-Saharan Africa", "East Asia & Pacific": "East Asia & Pacific",
         "Europe & Central Asia": "Europe & C. Asia", "Latin America & Caribbean": "Latin America",
         "Middle East & North Africa": "Middle East & N. Africa", "North America": "North America"}


def wide(col):
    return df[df["Country Name"].isin(REGIONS + ["World"])].pivot(index="Year", columns="Country Name", values=col)


INK, MUTED, GRID, GRAY = "#0b0b0b", "#6b6a66", "#e4e3df", "#bdbcb6"
GREEN, BLUE, RED = "#008300", "#2a78d6", "#e34948"  # green = growth (for), blue/red = calm/alarm (against)
plt.rcParams.update({
    "font.family": "Helvetica Neue", "font.size": 11, "axes.edgecolor": MUTED,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
})


def style(ax, title, subtitle, grid="y"):
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", color=INK, pad=30)
    ax.text(0, 1.03, subtitle, transform=ax.transAxes, fontsize=10.5, color=MUTED, va="bottom")
    ax.grid(axis=grid, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def header(fig, title, deck, color):
    fig.suptitle(title, fontsize=22, fontweight="bold", color=color, x=0.04, ha="left", y=0.985)
    fig.text(0.04, 0.95, deck, fontsize=12, color=INK)


def source(fig):
    fig.text(0.04, 0.015, "Source: World Bank population indicators (health.csv), 1960-2020. "
             "Regions are the World Bank's seven geographic regions. Working age = 15-64; children = 0-14.",
             fontsize=8.5, color=MUTED)


def highlight_lines(ax, data, accent, label_y, fmt):
    """One line per region: Sub-Saharan Africa in the accent color, the rest gray, labeled at the right edge."""
    for name in REGIONS[::-1]:
        is_ssa = name == SSA
        ax.plot(data.index, data[name], color=accent if is_ssa else GRAY, lw=3.4 if is_ssa else 1.6)
        ax.text(data.index.max() + 1, label_y.get(name, data[name].iloc[-1]),
                f"{SHORT.get(name, name)} {fmt(data[name].iloc[-1])}",
                color=accent if is_ssa else MUTED, fontsize=11 if is_ssa else 9.5,
                fontweight="bold" if is_ssa else "normal", va="center")



def series(name, col):
    return df[df["Country Name"] == name].set_index("Year")[col].sort_index()


GROWTH = "Population growth (annual %)"


# ---------------------------------------------------------------- PAGE 1: FOR
def page_for():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 13))
    header(fig, "Africa Is the World's Future",
           "No region on Earth is growing like Sub-Saharan Africa.", GREEN)

    # V1 - INDEXING: every region set to 100 in 1960, so SSA's small starting size disappears
    pop = wide(POP)
    indexed = pop[REGIONS].div(pop.loc[1960, REGIONS]) * 100
    highlight_lines(a1, indexed, GREEN,
                    {"Middle East & North Africa": 436, "South Asia": 324, "Latin America & Caribbean": 290,
                     "East Asia & Pacific": 226, "North America": 185, "Europe & Central Asia": 139},
                    lambda v: f"{v / 100:.1f}x")
    a1.axhline(100, color=MUTED, lw=1, ls="--")
    a1.text(2019, 80, "1960 = 100", ha="right", color=MUTED, fontsize=10)
    a1.set_xlim(1960, 2020)
    a1.set_ylim(0, 540)
    a1.set_ylabel("Population, indexed (1960 = 100)")
    style(a1, "Sub-Saharan Africa's population has grown five-fold",
          f"Since 1960 it multiplied {indexed.loc[2020, SSA] / 100:.1f}x - faster than any other region and "
          f"more than double East Asia's {indexed.loc[2020, 'East Asia & Pacific'] / 100:.1f}x.")

    # V2 - TRUNCATED AXIS + ZOOMED WINDOW: share of the world's children, 2000-2020 only, axis from 15%
    kids = wide("children")
    share = (kids[REGIONS].div(kids["World"], axis=0) * 100).loc[2000:]
    for name in ["South Asia", "East Asia & Pacific"]:
        a2.plot(share.index, share[name], color=GRAY, lw=2)
        a2.text(2020.4, share[name].iloc[-1] + (0.35 if name == "South Asia" else -0.35),
                f"{SHORT.get(name, name)} {share[name].iloc[-1]:.0f}%", color=MUTED, fontsize=10, va="center")
    a2.plot(share.index, share[SSA], color=GREEN, lw=4)
    a2.text(2020.4, share[SSA].iloc[-1], f"Sub-Saharan Africa {share[SSA].iloc[-1]:.0f}%", color=GREEN,
            fontsize=11.5, fontweight="bold", va="center")
    passed = share.index[share[SSA] > share["East Asia & Pacific"]].min()
    a2.scatter([passed], [share.loc[passed, SSA]], s=90, color=GREEN, zorder=3, edgecolor="white", linewidth=2)
    a2.annotate(f"{passed}: overtakes East Asia", (passed, share.loc[passed, SSA]), xytext=(2005, 25.6),
                fontsize=11, color=GREEN, fontweight="bold", arrowprops=dict(arrowstyle="->", color=GREEN))
    a2.set_xlim(2000, 2020)
    a2.set_xticks(range(2000, 2021, 5))
    a2.set_ylim(15, 30)
    a2.yaxis.set_major_formatter(PercentFormatter(decimals=0))
    a2.set_ylabel("Share of the world's children (0-14)")
    style(a2, "A growing share of the world's next generation is African",
          f"Sub-Saharan Africa's share soared from {share.loc[2000, SSA]:.0f}% to {share.loc[2020, SSA]:.0f}% in "
          f"two decades, passing East Asia and closing on South Asia.")

    source(fig)
    fig.tight_layout(rect=(0.02, 0.03, 0.96, 0.94), h_pad=4)
    return fig


# ---------------------------------------------------------------- PAGE 2: AGAINST
def page_against():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 13))
    header(fig, "Africa's Boom Is Overstated",
           "Sub-Saharan Africa is still far behind Asia - and its growth is already slowing.", BLUE)

    # V1 - LOG SCALE: equal growth rates look parallel, so SSA's five-fold rise looks ordinary
    pop = wide(POP) / 1e6
    for name in ["East Asia & Pacific", "South Asia"]:
        a1.plot(pop.index, pop[name], color=BLUE, lw=3)
        a1.text(2021, pop[name].iloc[-1], f"{SHORT.get(name, name)}\n{pop[name].iloc[-1] / 1e3:.2f}B",
                color=BLUE, fontsize=10.5, fontweight="bold", va="center")
    a1.plot(pop.index, pop[SSA], color=GRAY, lw=2.4)
    a1.text(2021, pop[SSA].iloc[-1], f"Sub-Saharan Africa\n{pop[SSA].iloc[-1] / 1e3:.2f}B",
            color=MUTED, fontsize=10.5, va="center")
    a1.set_yscale("log")
    a1.set_ylim(150, 4000)
    a1.set_yticks([200, 500, 1000, 2000, 4000])
    a1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e3:g}B" if v >= 1000 else f"{v:.0f}M"))
    a1.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    a1.set_xlim(1960, 2020)
    a1.set_ylabel("Population (log scale)")
    gap = pop.loc[2020, ["East Asia & Pacific", "South Asia"]].sum() - pop.loc[2020, SSA]
    style(a1, "Sub-Saharan Africa has never come close to Asia",
          f"In 60 years it never closed the gap: East and South Asia still have {gap / 1e3:.1f} billion more people.")

    # V2 - TRUNCATED AXIS + CHERRY-PICKED WINDOW: SSA growth rate from its 2010s plateau only
    g = series(SSA, GROWTH).loc[2010:]
    a2.fill_between(g.index, 2.6, g.values, color=RED, alpha=0.12, lw=0)
    a2.plot(g.index, g.values, color=RED, lw=3.4, marker="o", markersize=6)
    a2.annotate(f"{g.max():.2f}%", (g.idxmax(), g.max()), xytext=(0, 12), textcoords="offset points",
                ha="center", fontsize=11, color=RED, fontweight="bold")
    a2.annotate(f"{g[2020]:.2f}%\nand falling", (2020, g[2020]), xytext=(-10, -38), textcoords="offset points",
                ha="right", fontsize=11.5, color=RED, fontweight="bold")
    a2.set_xlim(2009.5, 2020.5)
    a2.set_ylim(2.6, 2.8)
    a2.set_yticks([2.60, 2.65, 2.70, 2.75, 2.80])
    a2.yaxis.set_major_formatter(PercentFormatter(decimals=2))
    a2.set_ylabel("Sub-Saharan Africa population growth (% per year)")
    falling_since = g.index[g.diff().fillna(0).ge(0)].max()
    style(a2, "Africa's growth rate is in steady decline",
          f"Growth has fallen every year since {falling_since}. The boom has already peaked.")

    source(fig)
    fig.tight_layout(rect=(0.02, 0.03, 0.96, 0.94), h_pad=4)
    return fig


if __name__ == "__main__":
    f1, f2 = page_for(), page_against()
    f1.savefig("page1_for_08v2.png", dpi=150)
    f2.savefig("page2_against_08v2.png", dpi=150)
    with PdfPages("persuasive_visualizations_08v2.pdf") as pdf:
        pdf.savefig(f1)
        pdf.savefig(f2)
