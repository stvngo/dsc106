# Ultra-processed calories are cheaper than unprocessed ones at every store, but where you shop matters even more so

## Write-up

Ultra-processed foods are often described as the cheap option. This chart tests that claim at each of the three stores in GroceryDB. At every store, the median ultra-processed calorie is cheaper than the median unprocessed one, by 52% at Target, 36% at Walmart and 19% at Whole Foods. But the differences between stores are even larger: a median ultra-processed calorie at Whole Foods ($0.84 per 100 kcal) costs more than a median unprocessed calorie at Walmart ($0.50). The takeaway for a budget-conscious shopper is that switching stores changes cost at least as much as switching processing levels.

The CSV has 26,250 rows (not the ~50,000 the description mentions), of which 58 are exact duplicates that I removed. I kept products that appear at more than one store, since each listing is a real item on that store's shelf. I used the dataset's price-per-calorie column, scaled to dollars per 100 kcal. I removed 5,449 items with no price-per-calorie, 405 items whose protein, fat and carbohydrate add up to more than 100 g per 100 g (physically impossible values such as 20,000 g of carbs), and 522 items under 20 kcal per 100 g (water, tea, coffee beans, spices), where price per calorie becomes enormous and is not a meaningful measure of affordability, leaving 19,816 products. Classes 1 and 2 are kept even though they are small, because dropping them would hide that the trend is not a straight line. I summarize each store and NOVA class with the median because price per calorie is extremely right-skewed; a few outliers would otherwise dominate the mean.

I used a line chart with the four NOVA classes in order on the x-axis and median price on the y-axis (starting at zero so heights compare honestly). NOVA is an ordinal scale, so connecting the classes with lines is appropriate and helps the reader follow each store from left to right. Each store has a consistent categorical color that echoes its brand, and lines are labeled directly at their ends instead of with a legend, so the reader does not need to look back and forth. The green band and annotation highlight the overlap between Whole Foods' ultra-processed price and Walmart's unprocessed price, which is the most surprising comparison. A second note explains why processed culinary ingredients (oils, butter, sugar) are so cheap per calorie. Sample sizes under each class show that classes 1 and 2 are small. The chart obscures the large spread within each group (only medians are shown), the mix of aisles inside each class (unprocessed foods include costly meat and seafood), and nutritional quality; price per calorie also favors calorie-dense foods by design.

Development process: I worked in Python (pandas and matplotlib) with an AI coding assistant. I profiled every column for missing values, duplicates and impossible nutrient values, and checked that the price-per-calorie column matched price divided by package calories. A table of median price across ten bins of the continuous processing score was too noisy to read per store, so I switched to the four NOVA classes. Splitting by store showed the store gap was as large as the processing gap. My first title said "the most processed calories are the cheapest," but culinary ingredients are cheaper at Walmart and Whole Foods, so I narrowed it to ultra-processed versus unprocessed and added a note explaining the dip. I also moved sample sizes into the axis labels.

---

## Build log (reference, not part of the submission)

This is the step-by-step record of how the chart was made, so you can explain or defend any part of it. Code lives in `project1/make_charts.py` (the `chart_store_price` function builds this chart) and `project1/writeups.py` (write-up text). Regenerate everything with `../.venv/bin/python make_charts.py` from inside `project1/`; the PDF is `output/C_store_price.pdf`.

### 1. Profiling the raw data

Loaded `data/grocerydb.csv` with pandas and checked shape, types, missing values and percentiles for every column.

- 26,250 rows and 16 columns. Stores: Whole Foods 10,851, Walmart 8,896, Target 6,503.
- Missing values: `price` 4,030, `price percal` 5,470, `package_weight` 1,275, `brand` 69. `FPro` and `FPro_class` are complete.
- 58 fully identical rows (exact duplicates).
- Clear data errors: `Carbohydrate` max 20,000 g per 100 g, `Sodium` max 547,619 g per 100 g, `price percal` max $15 per calorie (about 2,600 times the median).

### 2. Checking that `price percal` is trustworthy

Recomputed calories per 100 g from the macronutrients (4 kcal/g protein, 4 kcal/g carbohydrate, 9 kcal/g fat), then estimated price per calorie as `price / (package_weight / 100 × kcal per 100 g)`. The dataset's column and this estimate have a Spearman correlation of 0.94 and a median ratio of 1.01, so the column was used as-is and multiplied by 100 to get dollars per 100 kcal (easier to read than fractions of a cent per calorie).

### 3. Cleaning rules

| Step | Rows affected | Why |
|---|---|---|
| Drop exact duplicates | 58 | Same listing recorded twice |
| Drop missing `price percal` | 5,449 | Cannot place them on the price axis |
| Drop protein + fat + carbs > 100 g per 100 g | 405 | Physically impossible, so the calorie and price values are unreliable |
| Drop items under 20 kcal per 100 g | 522 | Water, tea, coffee beans and spices have near-zero calories, so price per calorie becomes huge and meaningless |

Products sold at more than one store were kept, because each listing is a real product on that store's shelf. After cleaning, 19,816 priced products remain.

### 4. First attempt: continuous processing score

Binned `FPro` (0 to 1) into ten equal bins and took the median price per 100 kcal per store. The result was too jumpy to tell a clear story, for example Target went $1.36, $0.54, $1.03, $1.04, $1.15 across the first five bins. The only consistent pattern was a drop in the two most processed bins. The four NOVA classes are fewer, better known and easier to label, so the chart uses those instead.

### 5. Final numbers (median price per 100 kcal)

| Store | Unprocessed (0) | Culinary ingredients (1) | Processed (2) | Ultra-processed (3) |
|---|---|---|---|---|
| Target | $1.11 | $0.95 | $0.73 | $0.53 |
| Walmart | $0.50 | $0.20 | $0.38 | $0.32 |
| Whole Foods | $1.04 | $0.70 | $1.13 | $0.84 |
| Products (all stores) | 2,204 | 363 | 1,852 | 15,397 |

Drop from unprocessed to ultra-processed: Target 52%, Walmart 36%, Whole Foods 19%. Whole Foods' ultra-processed median ($0.84) is above Walmart's unprocessed median ($0.50).

### 6. Design decisions

- **Mark type: line chart with dots.** NOVA classes are ordered, so lines connecting them are meaningful and let the reader follow one store across all four levels. Dots mark the actual data points.
- **Y-axis starts at $0.** Keeps the vertical distances proportional to the real price differences.
- **Direct labels instead of a legend.** Store names and ultra-processed prices sit at the right end of each line, and unprocessed prices at the left end. The reader never has to match colors to a legend.
- **Store colors.** Walmart blue, Target red, Whole Foods green, roughly matching each brand so they are easy to remember.
- **Green band and arrow.** Shades the price range between Walmart's unprocessed median and Whole Foods' ultra-processed median to make the overlap visible, with an annotation stating it in words.
- **Grey note on culinary ingredients.** Explains the dip at class 1 (oils, butter, sugar are nearly pure calories), so readers do not think the data is wrong.
- **Sample sizes in the x-axis labels.** Show that classes 1 and 2 are much smaller than class 3, so readers weigh them accordingly.
- **Medians instead of means.** Prices are heavily right-skewed, so means would be pulled by a few extreme items.

### 7. Iterations

1. The first draft's two-line title overlapped the subtitle, and the sample-size labels were drawn below the chart and got cut off.
2. The first title, "At every store, the most processed calories are the cheapest," was not true: culinary ingredients are cheaper than ultra-processed foods at Walmart ($0.20 vs. $0.32) and Whole Foods ($0.70 vs. $0.84). The title was narrowed to compare only ultra-processed and unprocessed, and the culinary-ingredients note was added.
3. Fixed the title spacing and moved the sample sizes into the x-axis tick labels.
4. Removed the source and cleaning footnote from the bottom of the chart and enlarged the plot into the freed space.
5. Added a one-line summary of the data transformations to the subtitle ("Medians of 19,816 priced products; removed duplicates, missing prices, impossible nutrient values and items under 20 kcal per 100 g") so the chart still tells readers how the data was filtered, as the rubric's Data Transformations criterion asks. The full counts are in the write-up.
