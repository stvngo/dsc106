import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).parent
OUT = HERE / "output"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#888888",
    "xtick.color": "#444444",
    "ytick.color": "#222222",
    "axes.labelcolor": "#222222",
})

INK = "#1f1f1f"
MUTED = "#6b6b6b"
UPF_COLOR = "#d1495b"
MIN_COLOR = "#2e8b57"
STORE_COLORS = {"Walmart": "#1f6fb4", "Target": "#cc2936", "WholeFoods": "#2e8b57"}
STORE_LABELS = {"Walmart": "Walmart", "Target": "Target", "WholeFoods": "Whole Foods"}

# GroceryDB uses parallel "-wf" categories for some aisles; merge the true duplicates.
MERGE = {
    "drink-juice-wf": "drink-juice",
    "seafood-wf": "seafood",
    "rice-grains-wf": "rice-grains-packaged",
    "nuts-seeds-wf": "snacks-nuts-seeds",
}
LABELS = {
    "baby-food": "Baby food", "baking": "Baking mixes & supplies", "bread": "Bread",
    "breakfast": "Breakfast (waffles, pancakes)", "cakes": "Cakes", "cereal": "Cereal",
    "cheese": "Cheese", "coffee-beans-wf": "Coffee beans", "cookies-biscuit": "Cookies & biscuits",
    "culinary-ingredients": "Oils, vinegars & sweeteners", "dairy-yogurt-drink": "Yogurt & dairy drinks",
    "dressings": "Dressings", "drink-coffee": "Coffee drinks", "drink-juice": "Juice",
    "drink-shakes-other": "Shakes & other drinks", "drink-soft-energy-mixes": "Soda, energy & drink mixes",
    "drink-tea": "Tea", "drink-water-wf": "Water", "eggs-wf": "Eggs", "ice-cream-dessert": "Ice cream & frozen dessert",
    "jerky": "Jerky", "mac-cheese": "Mac & cheese", "meat-packaged": "Packaged meat",
    "meat-poultry-wf": "Fresh meat & poultry", "milk-milk-substitute": "Milk & milk substitutes",
    "muffins-bagels": "Muffins & bagels", "pasta-noodles": "Pasta & noodles",
    "pastry-chocolate-candy": "Pastry, chocolate & candy", "pizza": "Pizza",
    "prepared-meals-dishes": "Prepared meals", "produce-beans-wf": "Fresh produce & beans",
    "produce-packaged": "Packaged produce", "pudding-jello": "Pudding & jello",
    "rice-grains-packaged": "Rice & grains", "rolls-buns-wraps": "Rolls, buns & wraps",
    "salad": "Salad kits", "sauce-all": "Sauces", "sausage-bacon": "Sausage & bacon",
    "seafood": "Seafood", "snacks-bars": "Snack bars", "snacks-chips": "Chips",
    "snacks-dips-salsa": "Dips & salsa", "snacks-mixes-crackers": "Crackers & snack mixes",
    "snacks-nuts-seeds": "Nuts & seeds", "snacks-popcorn": "Popcorn", "soup-stew": "Soup & stew",
    "spices-seasoning": "Spices & seasoning", "spread-squeeze": "Spreads (nut butter, jam)",
}


def load():
    raw = pd.read_csv(HERE.parent / "data" / "grocerydb.csv")
    df = raw.drop_duplicates().copy()
    df["category"] = df["category"].replace(MERGE)
    df["aisle"] = df["category"].map(LABELS)
    df["upf"] = df["FPro_class"] == 3
    df["kcal100"] = 4 * df["Protein"] + 4 * df["Carbohydrate"] + 9 * df["Total Fat"]
    df["macros"] = df["Protein"] + df["Carbohydrate"] + df["Total Fat"]
    df["usd_100kcal"] = df["price percal"] * 100
    stats = {
        "raw": len(raw),
        "dupes": len(raw) - len(df),
        "kept": len(df),
    }
    return df, stats


def price_subset(df):
    """Rows where price per calorie is meaningful."""
    has_price = df["usd_100kcal"].notna()
    plausible = df["macros"] <= 100
    caloric = df["kcal100"] >= 20
    d = df[has_price & plausible & caloric]
    info = {
        "no_price": int((~has_price).sum()),
        "implausible": int((has_price & ~plausible).sum()),
        "low_cal": int((has_price & plausible & ~caloric).sum()),
        "n": len(d),
    }
    return d, info


def dollars(x, _=None):
    return f"${x:.2f}" if x < 1 else f"${x:.0f}" if x == int(x) else f"${x:.1f}"


def add_header(fig, title, subtitle, top=0.965):
    height_in = fig.get_figheight()
    title_lines = title.count("\n") + 1
    fig.text(0.03, top, title, fontsize=19, fontweight="bold", color=INK, va="top", linespacing=1.15)
    sub_top = top - (title_lines * 0.33 + 0.15) / height_in
    fig.text(0.03, sub_top, subtitle.replace("$", r"\$"), fontsize=11, color=MUTED, va="top", linespacing=1.5)


def add_footer(fig, text):
    fig.text(0.03, 0.015, text.replace("$", r"\$"), fontsize=8.3, color=MUTED, va="bottom", linespacing=1.4)


# ---------------------------------------------------------------- candidate A
def chart_aisle_price(df, stats):
    d, info = price_subset(df)
    g = d.groupby(["aisle", "upf"])["usd_100kcal"].agg(["median", "count"]).unstack("upf")
    g = g[(g[("count", False)] >= 15) & (g[("count", True)] >= 15)]
    t = pd.DataFrame({
        "minimal": g[("median", False)], "upf": g[("median", True)],
        "n_min": g[("count", False)], "n_upf": g[("count", True)],
    })
    t["ratio"] = t["upf"] / t["minimal"]
    t = t.sort_values("ratio")

    overall_min = d.loc[~d.upf, "usd_100kcal"].median()
    overall_upf = d.loc[d.upf, "usd_100kcal"].median()

    fig = plt.figure(figsize=(10, 12.5))
    ax = fig.add_axes([0.30, 0.115, 0.50, 0.70])
    y = np.arange(len(t))

    cheaper = t["ratio"] < 0.5
    for yi, (name, r) in zip(y, t.iterrows()):
        strong = r.ratio < 0.5
        lc = UPF_COLOR if strong else "#bdbdbd"
        ax.plot([r.minimal, r.upf], [yi, yi], color=lc, lw=2.4 if strong else 1.6, alpha=0.55 if strong else 1, zorder=1)
    ax.scatter(t["minimal"], y, s=60, color=MIN_COLOR, zorder=3, label="Not ultra-processed (NOVA 0–2)")
    ax.scatter(t["upf"], y, s=60, color=UPF_COLOR, zorder=3, label="Ultra-processed (NOVA 3)")

    for yi, (name, r) in zip(y, t.iterrows()):
        pct = (1 - r.ratio) * 100
        txt = f"{pct:.0f}% cheaper" if r.ratio < 1 else f"{(r.ratio - 1) * 100:.0f}% pricier"
        strong = r.ratio < 0.5
        ax.text(1.02, yi, txt, transform=ax.get_yaxis_transform(), va="center", fontsize=9.5,
                color=UPF_COLOR if strong else MUTED, fontweight="bold" if strong else "normal")

    ax.set_xscale("log")
    ax.set_xlim(0.12, 6.2)
    ax.set_xticks([0.15, 0.25, 0.5, 1, 2, 4])
    ax.xaxis.set_major_formatter(FuncFormatter(dollars))
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda *_: ""))
    ax.set_yticks(y)
    ax.set_yticklabels(t.index, fontsize=10.5)
    for lab, strong in zip(ax.get_yticklabels(), cheaper):
        if strong:
            lab.set_fontweight("bold")
    ax.invert_yaxis()
    ax.set_ylim(len(t) - 0.4, -0.6)
    ax.grid(axis="x", color="#e6e6e6", lw=0.8, which="major")
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Median price per 100 calories (USD, log scale)", fontsize=11)
    ax.text(1.02, -0.9, "Ultra-processed\nvs. not", transform=ax.get_yaxis_transform(),
            fontsize=9, color=MUTED, va="bottom", fontweight="bold")

    n_strong = int(cheaper.sum())
    ax.axhspan(-0.5, n_strong - 0.5, color=UPF_COLOR, alpha=0.07, zorder=0, lw=0)
    ax.text(5.8, (n_strong - 1) / 2,
            "Snacks, sweets & baked goods:\nthe ultra-processed option\ncosts less than half as much\nper calorie",
            ha="right", va="center", fontsize=10, color=UPF_COLOR, fontstyle="italic")

    n_pricier = int((t["ratio"] > 1).sum())
    ax.axhspan(len(t) - n_pricier - 0.5, len(t) - 0.5, color="#888888", alpha=0.06, zorder=0, lw=0)
    ax.text(5.8, len(t) - n_pricier / 2 - 0.5,
            "Staples & ingredients:\nultra-processed versions\ncost more per calorie",
            ha="right", va="center", fontsize=10, color=MUTED, fontstyle="italic")

    leg = fig.legend(*ax.get_legend_handles_labels(), loc="upper left", bbox_to_anchor=(0.295, 0.858),
                     ncol=2, frameon=False, fontsize=10.5, handletextpad=0.3, columnspacing=1.5)

    add_header(
        fig,
        "In the snack, sweets and bread aisles, ultra-processed\ncalories cost less than half as much",
        f"Across all {info['n']:,} priced products, the median ultra-processed product costs "
        f"${overall_upf:.2f} per 100 calories vs. ${overall_min:.2f} for less-processed items.\n"
        "But the discount is aisle-specific: for pasta, dressings and spreads the ultra-processed option costs more.",
    )
    add_footer(
        fig,
        "Data: GroceryDB (Menichetti et al., Nature Food 2023), Walmart, Target & Whole Foods listings. Processing level = predicted NOVA class.\n"
        f"Removed {stats['dupes']} exact duplicate rows, {info['no_price']:,} items with no price-per-calorie, {info['implausible']} items whose protein+fat+carbs "
        f"exceed 100 g per 100 g, and {info['low_cal']} items\nunder 20 kcal/100 g (water, tea, coffee beans, spices), where price per calorie is not meaningful. "
        "Shows aisles with at least 15 products in each group, sorted by\nprice ratio. Medians are used because prices are heavily right-skewed.",
    )
    return fig, {"t": t, "info": info, "overall": (overall_min, overall_upf)}


# ---------------------------------------------------------------- candidate B
def chart_store_aisles(df, stats):
    shares = df.groupby(["aisle", "store"])["upf"].agg(["mean", "count"]).unstack("store")
    ok = (shares["count"] >= 20).all(axis=1)
    p = shares["mean"][ok] * 100
    p = p.sort_values("WholeFoods", ascending=False)
    overall = df.groupby("store")["upf"].mean() * 100

    rate = df.groupby(["store", "aisle"])["upf"].mean().unstack(0)
    mix = df.groupby(["store", "aisle"]).size().unstack(0).fillna(0)
    mix = mix / mix.sum()
    wf_with_walmart_mix = (rate["WholeFoods"].fillna(rate["Walmart"]) * mix["Walmart"]).sum() * 100

    rows = ["All products"] + list(p.index)
    fig = plt.figure(figsize=(10, 13))
    ax = fig.add_axes([0.30, 0.075, 0.58, 0.735])
    y = np.arange(len(rows))
    y = np.where(y == 0, -0.6, y)

    def draw(yi, vals, big=False):
        lo, hi = min(vals.values()), max(vals.values())
        ax.plot([lo, hi], [yi, yi], color="#c9c9c9", lw=3 if big else 1.6, zorder=1)
        for s, v in vals.items():
            ax.scatter(v, yi, s=110 if big else 48, color=STORE_COLORS[s], zorder=3,
                       edgecolor="white", lw=0.8)

    draw(y[0], overall.to_dict(), big=True)
    for yi, (name, r) in zip(y[1:], p.iterrows()):
        draw(yi, r.to_dict())

    for s, ha, dx in [("WholeFoods", "right", -1.6), ("Walmart", "center", 0), ("Target", "left", 1.6)]:
        v = overall[s]
        ax.text(v + dx, y[0] - 0.55, f"{STORE_LABELS[s]} {v:.0f}%" if s != "Walmart" else f"{v:.0f}%",
                ha=ha, va="bottom", fontsize=10, color=STORE_COLORS[s], fontweight="bold")

    ax.axhline(0.2, color="#999999", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(rows, fontsize=10.5)
    ax.get_yticklabels()[0].set_fontweight("bold")
    ax.get_yticklabels()[0].set_fontsize(12)
    ax.invert_yaxis()
    ax.set_ylim(len(rows) - 0.4, -2.2)
    ax.set_xlim(-2, 102)
    ax.set_xticks(range(0, 101, 20))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("Share of products classified ultra-processed (NOVA 3)", fontsize=11, labelpad=8)
    ax.spines["top"].set_visible(True)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#e9e9e9", lw=0.8)
    ax.set_axisbelow(True)

    all_high = p[(p >= 90).all(axis=1)].index
    idx = [rows.index(a) for a in all_high]
    ax.axhspan(min(idx) - 0.5, max(idx) + 0.5, xmin=0.0, xmax=1, color="#f3d9dc", alpha=0.45, zorder=0)
    ax.text(3, (min(idx) + max(idx)) / 2,
            f"{len(all_high)} aisles are ≥90% ultra-processed\nat every store, Whole Foods included",
            fontsize=10, color="#a3303f", va="center", fontstyle="italic")

    low_aisles = df.groupby("aisle")["upf"].mean() < 0.5
    low_share = df[df["aisle"].isin(low_aisles[low_aisles].index)].groupby("store").size() / df.groupby("store").size() * 100
    first_low = next(i for i, a in enumerate(rows) if a in p.index and p.loc[a, "WholeFoods"] < 50)
    ax.axhspan(first_low - 0.5, len(rows) - 0.5, color="#e3f1e8", alpha=0.6, zorder=0, lw=0)
    ax.text(101, first_low + 0.1,
            "Mostly unprocessed aisles (fresh food,\ncheese, pasta, nuts, spices) are where\n"
            f"Whole Foods' assortment differs:\nsuch aisles are {low_share['WholeFoods']:.0f}% of its products, vs.\n"
            f"{low_share['Walmart']:.0f}% at Walmart and {low_share['Target']:.0f}% at Target",
            ha="right", va="top", fontsize=10, color="#1f5e3a", fontstyle="italic", linespacing=1.4)

    handles = [plt.Line2D([], [], marker="o", ls="", ms=9, color=STORE_COLORS[s], label=STORE_LABELS[s])
               for s in ["WholeFoods", "Walmart", "Target"]]
    leg = ax.legend(handles=handles, loc="center left", bbox_to_anchor=(0.03, 0.5), frameon=True,
                    fontsize=10, title="Store", title_fontsize=10, borderpad=0.8)
    leg.get_frame().set_edgecolor("#cccccc")

    add_header(
        fig,
        "Whole Foods stocks fewer ultra-processed foods, but its\nbread, snack and dessert aisles look like everyone else's",
        f"{overall['WholeFoods']:.0f}% of Whole Foods products are ultra-processed vs. {overall['Walmart']:.0f}% at Walmart and "
        f"{overall['Target']:.0f}% at Target. But about half that gap comes from which aisles\nit stocks: "
        f"with Walmart's mix of aisles (and its own rate within each aisle), Whole Foods' share would be {wf_with_walmart_mix:.0f}%.",
    )
    add_footer(
        fig,
        f"Data: GroceryDB (Menichetti et al., Nature Food 2023), {stats['kept']:,} product listings after removing {stats['dupes']} exact duplicate rows. "
        "Processing level = predicted NOVA class\n(0 unprocessed, 1 culinary ingredient, 2 processed, 3 ultra-processed). "
        "GroceryDB's duplicate Whole Foods-specific categories (juice, seafood, grains, nuts) were merged.\n"
        "Shows aisles with at least 20 products at each store, sorted by Whole Foods' share. "
        "Grey bars span the lowest to highest store.",
    )
    return fig, {"p": p, "overall": overall, "mixadj": wf_with_walmart_mix, "all_high": list(all_high)}


# ---------------------------------------------------------------- candidate C
def chart_store_price(df, stats):
    d, info = price_subset(df)
    m = d.groupby(["store", "FPro_class"])["usd_100kcal"].median().unstack("FPro_class")
    n = d.groupby(["store", "FPro_class"]).size().unstack("FPro_class")
    classes = [0, 1, 2, 3]
    names = ["Unprocessed /\nminimally processed", "Processed culinary\ningredients", "Processed\nfoods", "Ultra-\nprocessed"]

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_axes([0.08, 0.14, 0.70, 0.62])
    x = np.arange(4)
    for s in ["WholeFoods", "Target", "Walmart"]:
        vals = m.loc[s, classes].values
        ax.plot(x, vals, color=STORE_COLORS[s], lw=2.6, marker="o", ms=9, zorder=3)
        ax.text(3.12, vals[-1], f"{STORE_LABELS[s]}  ${vals[-1]:.2f}", color=STORE_COLORS[s],
                fontsize=11.5, fontweight="bold", va="center")
        ax.text(-0.12, vals[0], f"${vals[0]:.2f}", color=STORE_COLORS[s], fontsize=11,
                fontweight="bold", va="center", ha="right")

    wf_upf = m.loc["WholeFoods", 3]
    wm_min = m.loc["Walmart", 0]
    ax.axhspan(wm_min, wf_upf, xmin=0.0, xmax=1, color="#e9f3ec", zorder=0)
    ax.annotate(
        f"A Whole Foods ultra-processed calorie (${wf_upf:.2f})\ncosts more than an unprocessed\none at Walmart (${wm_min:.2f})",
        xy=(3, wf_upf), xytext=(1.35, 1.32), fontsize=10.5, color="#1f5e3a", fontstyle="italic",
        arrowprops=dict(arrowstyle="->", color="#1f5e3a", lw=0.9, connectionstyle="arc3,rad=-0.2"),
    )

    ns = n.sum()
    ax.annotate(
        "Oils, butter and sugar are almost\npure calories, cheap per calorie",
        xy=(1, m.loc["Walmart", 1]), xytext=(1.12, 0.05), fontsize=10, color=MUTED, fontstyle="italic",
        arrowprops=dict(arrowstyle="-", color="#999999", lw=0.8),
    )

    ax.set_xticks(x)
    ax.set_xticklabels([f"{nm}\n(n = {ns[c]:,})" for nm, c in zip(names, classes)], fontsize=11)
    ax.set_xlim(-0.55, 3.1)
    ax.set_ylim(0, 1.45)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:.2f}"))
    ax.set_ylabel("Median price per 100 calories (USD)", fontsize=11.5)
    ax.set_xlabel("Degree of processing (predicted NOVA class)", fontsize=11.5, labelpad=10)
    ax.grid(axis="y", color="#e6e6e6")
    ax.set_axisbelow(True)

    drops = {s: (1 - m.loc[s, 3] / m.loc[s, 0]) * 100 for s in m.index}
    add_header(
        fig,
        "Ultra-processed calories are cheaper than unprocessed ones at\nevery store, but where you shop matters even more so",
        f"Going from unprocessed to ultra-processed foods cuts the median price of 100 calories by {drops['Target']:.0f}% at Target, "
        f"{drops['Walmart']:.0f}% at Walmart and {drops['WholeFoods']:.0f}% at Whole Foods.\n"
        f"Medians of {info['n']:,} priced products; removed duplicates, missing prices, impossible nutrient values and items under 20 kcal per 100 g.",
        top=0.965,
    )
    return fig, {"m": m, "n": n, "drops": drops, "clean": info}


def writeup_page(title, paragraphs):
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.08, 0.95, title, fontsize=15, fontweight="bold", va="top", color=INK)
    renderer = fig.canvas.get_renderer()
    y = 0.905
    for para in paragraphs:
        wrapped = textwrap.fill(" ".join(para.split()), width=106).replace("$", r"\$")
        t = fig.text(0.08, y, wrapped, fontsize=9.6, va="top", color=INK, linespacing=1.4)
        height = t.get_window_extent(renderer).height / fig.bbox.height
        y -= height + 0.018
    if y + 0.018 < 0.035:
        raise ValueError(f"write-up overflows page ({y:.3f})")
    return fig


def save(name, fig, writeup_title, paragraphs):
    fig.savefig(OUT / f"{name}.png", dpi=200)
    with PdfPages(OUT / f"{name}.pdf") as pdf:
        pdf.savefig(fig)
        w = writeup_page(writeup_title, paragraphs)
        pdf.savefig(w)
        plt.close(w)
    plt.close(fig)


if __name__ == "__main__":
    from writeups import WRITEUPS

    df, stats = load()
    for name, fn in [("A_aisle_price", chart_aisle_price),
                     ("B_store_aisles", chart_store_aisles),
                     ("C_store_price", chart_store_price)]:
        fig, info = fn(df, stats)
        title, paras = WRITEUPS[name](stats, info)
        save(name, fig, title, paras)
        print(name, "done")
