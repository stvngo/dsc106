def _cleaning_common(stats):
    return (
        f"The CSV has {stats['raw']:,} rows (not the ~50,000 the description mentions), of which "
        f"{stats['dupes']} are exact duplicates that I removed. I kept products that appear at more than one "
        "store, since each listing is a real item on that store's shelf."
    )


def aisle_price(stats, info):
    t = info["t"]
    lo, hi = info["overall"]
    cheap = t[t["ratio"] < 0.5]
    pricier = t[t["ratio"] > 1]
    return "Write-up: Where ultra-processed calories are cheap", [
        f"""A common explanation for why ultra-processed food dominates American diets is that it is
        cheaper. GroceryDB supports this on average: the median ultra-processed product (NOVA class 3)
        costs ${hi:.2f} per 100 calories versus ${lo:.2f} for less-processed products. But a single
        average blends very different aisles, so I compared both groups inside each aisle. The resulting
        story is that the "cheap calorie" discount is concentrated in the snack, sweets and bread aisles
        ({', '.join(cheap.index).lower()}), where ultra-processed calories cost less than half as much.
        For {len(pricier)} aisles, including pasta, dressings, spreads and rice, the ultra-processed
        version is actually more expensive. The audience is shoppers and policy readers who have heard
        "processed food is cheap."
        """,

        f"""{_cleaning_common(stats)} I used the dataset's price-per-calorie column (scaled to dollars per
        100 kcal). I dropped
        {info['info']['no_price']:,} items with no price-per-calorie, {info['info']['implausible']} items whose protein,
        fat and carbohydrates add up to more than 100 g per 100 g (physically impossible, e.g. 20,000 g of
        carbohydrate), and {info['info']['low_cal']} items under 20 kcal per 100 g (water, tea, coffee beans,
        spices), where price per calorie is not a meaningful measure of affordability. This leaves {info['info']['n']:,} products. I split products into ultra-processed (NOVA 3)
        versus everything else (NOVA 0 to 2), since classes 1 and 2 are too small to compare per aisle. I
        merged four Whole Foods-specific categories that duplicate general ones (juice, seafood, grains,
        nuts) and kept only aisles with at least 15 products in each group so medians are stable. I used medians because price per calorie is extremely right-skewed (even after cleaning,
        the most expensive item costs about 1,200 times the median per calorie).""",

        """I used a dumbbell chart: each aisle is a row, and the two groups' medians are dots on a shared
        horizontal position axis, the most accurate channel for comparing quantities. The connecting line's
        length shows the size of the price gap. The x-axis is logarithmic because the claim is about ratios
        ("half as much") and aisle medians span more than a 10x range; on a log scale equal ratios look equally long in every
        aisle. Rows are sorted by that ratio so the reader sees a continuous ranking from "much cheaper" to
        "pricier," and the exact percentage is printed on the right so readers do not have to estimate on a
        log scale. Color is used only for the two groups being compared. The top band and bold red labels
        highlight the five aisles where the discount exceeds 50%, and a grey band marks aisles where it
        reverses. The chart obscures the spread within each aisle (only medians are shown), the number of
        products per aisle, differences between stores, nutrition quality, and the fact that price per
        calorie favors calorie-dense foods (one reason produce looks expensive).""",

        """Development process: I worked in Python (pandas and matplotlib) with an AI coding assistant.
        I first profiled every column for missing values, duplicates and impossible nutrient values, and
        checked that the price-per-calorie column matched price divided by package calories. Splitting
        median price per 100 kcal into ten bins of the processing score showed the drop only in the top two
        bins, which suggested specific aisles were driving the average. An aisle-by-aisle comparison
        confirmed it, with ratios from 74% cheaper (crackers) to 164% pricier (pasta). The first draft
        sorted rows the wrong way and had a legend covering data, so I re-sorted cheapest first, moved the
        legend above the plot and added the two bands. I also changed the title from "a third to a half" to
        "less than half" after checking the real ratios (26% to 47%).""",
    ]


def store_aisles(stats, info):
    o = info["overall"]
    return "Write-up: Is Whole Foods really less processed?", [
        f"""Whole Foods markets itself as the healthier grocery store, and GroceryDB partly agrees:
        {o['WholeFoods']:.0f}% of its products are predicted ultra-processed (NOVA class 3), versus
        {o['Walmart']:.0f}% at Walmart and {o['Target']:.0f}% at Target. The story I want to tell is
        where that difference comes from. In {len(info['all_high'])} aisles (bread, cakes, pizza, cookies,
        chips, crackers, prepared meals and others) at least 90% of products are ultra-processed at all
        three stores, so a shopper picking up bread or snacks at Whole Foods is not getting a meaningfully
        less processed product. About half of Whole Foods' advantage comes from stocking more products in
        aisles like fresh produce, meat, eggs and cheese: if it kept its own processing rate in each aisle
        but had Walmart's mix of aisles, its overall share would be {info['mixadj']:.0f}%. The audience is
        shoppers who choose a store as a proxy for choosing healthier food.""",

        f"""{_cleaning_common(stats)} The outcome is the share of products with FPro_class = 3, which is
        easier to read than the continuous FPro score and matches the NOVA definition of ultra-processed
        food used in nutrition research. This variable has no missing values, so no rows were dropped for
        missingness; price and nutrient outliers do not affect this chart. I merged four Whole Foods-specific
        categories that duplicate general ones (juice, seafood, rice/grains, nuts) and renamed categories as
        readable aisle names. I only show aisles with at least 20 products at every store, so that a single
        product cannot swing a percentage; this drops small aisles like water, tea and coffee beans. The
        "mix-adjusted" number in the subtitle is a standard reweighting: Whole Foods' within-aisle
        ultra-processed rate weighted by Walmart's share of products in each aisle.""",

        """I used a dot plot with one row per aisle and one dot per store on a shared 0 to 100% position
        axis, since position is the most accurate channel and keeps 40 aisles by 3 stores readable without
        the clutter of grouped bars. A grey bar spans the lowest to highest store, so its length directly
        encodes how much the stores disagree in that aisle. The overall result sits on top in larger dots
        as the headline comparison. Rows are sorted by Whole Foods' share, which groups the near-100% aisles
        together at the top and the fresh aisles at the bottom. Store colors are categorical hues chosen to
        echo each brand (Walmart blue, Target red, Whole Foods green) so the legend is easy to remember. A
        red band highlights the aisles that are at least 90% ultra-processed everywhere, and a green band
        marks the mostly unprocessed aisles that drive Whole Foods' assortment advantage. The design obscures
        how many products each aisle has (a small aisle and a large aisle get equal space), how processed
        products are on the continuous FPro score within a class, and anything about price or nutrition.
        The NOVA class is also a model prediction, not a label assigned by a person.""",

        """Development process: I profiled the dataset in pandas and first noticed the store-level gap.
        Before making a store comparison chart, I checked whether the gap held within aisles and found that
        in most aisles it was small. That led me to compute the mix-adjusted share, which confirmed that
        about half of the gap is about which aisles each store stocks. I tried a 100% stacked bar per store
        first, but it hid this aisle-level story, so I switched to the dot plot. I built the chart in
        matplotlib and iterated on sorting, label collisions and the two highlight bands.""",
    ]


def store_price(stats, info):
    m, d = info["m"], info["drops"]
    return "Write-up: Processing, price and where you shop", [
        f"""Ultra-processed foods are often described as the cheap option. This chart tests that claim at
        each of the three stores in GroceryDB. At every store, the median ultra-processed calorie is cheaper
        than the median unprocessed one, by {d['Target']:.0f}% at Target, {d['Walmart']:.0f}% at Walmart and
        {d['WholeFoods']:.0f}% at Whole Foods. But the differences between stores are even larger: a
        median ultra-processed calorie at Whole Foods (${m.loc['WholeFoods', 3]:.2f} per 100 kcal) costs
        more than a median unprocessed calorie at Walmart (${m.loc['Walmart', 0]:.2f}). The takeaway for a
        budget-conscious shopper is that switching stores changes cost at least as much as switching
        processing levels.""",

        f"""{_cleaning_common(stats)} I used the dataset's price-per-calorie column, scaled to dollars per
        100 kcal. I removed {info['clean']['no_price']:,} items with no price-per-calorie,
        {info['clean']['implausible']} items whose protein, fat and carbohydrate add up to more than 100 g
        per 100 g (physically impossible values such as 20,000 g of carbs), and {info['clean']['low_cal']}
        items under 20 kcal per 100 g (water, tea, coffee beans, spices), where price per calorie becomes
        enormous and is not a meaningful measure of affordability, leaving {info['clean']['n']:,} products.
        Classes 1 and 2 are kept even though they are small, because dropping them would hide that the
        trend is not a straight line. I summarize each store and NOVA class with the median
        because price per calorie is extremely right-skewed; a few outliers would otherwise dominate the mean.""",

        """I used a line chart with the four NOVA classes in order on the x-axis and median price on the
        y-axis (starting at zero so heights compare honestly). NOVA is an ordinal scale, so connecting the
        classes with lines is appropriate and helps the reader follow each store from left to right. Each
        store has a consistent categorical color that echoes its brand, and lines are labeled directly at
        their ends instead of with a legend, so the reader does not need to look back and forth. The green
        band and annotation highlight the overlap between Whole Foods' ultra-processed price and Walmart's
        unprocessed price, which is the most surprising comparison. A second note explains why processed
        culinary ingredients (oils, butter, sugar) are so cheap per calorie. Sample sizes under each class
        show that classes 1 and 2 are small. The chart obscures the large spread within each group (only
        medians are shown), the mix of aisles inside each class (unprocessed foods include costly meat and
        seafood), and nutritional quality; price per calorie also favors calorie-dense foods by design.""",

        """Development process: I worked in Python (pandas and matplotlib) with an AI coding assistant. I
        profiled every column for missing values, duplicates and impossible nutrient values, and checked
        that the price-per-calorie column matched price divided by package calories. A table of median
        price across ten bins of the continuous processing score was too noisy to read per store, so I
        switched to the four NOVA classes. Splitting by store showed the store gap was as large as the
        processing gap. My first title said "the most processed calories are the cheapest," but culinary
        ingredients are cheaper at Walmart and Whole Foods, so I narrowed it to ultra-processed versus
        unprocessed and added a note explaining the dip. I also moved sample sizes into the axis labels.""",
    ]


WRITEUPS = {
    "A_aisle_price": aisle_price,
    "B_store_aisles": store_aisles,
    "C_store_price": store_price,
}
