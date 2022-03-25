import pandas as pd
import numpy as np


def time_to_tuples(dataframe, timecol):
    """given a df with a str representation of time,
    replaces time col with a tuple representation to make it searchable
    e.g.: 1 hr 15 min = (1,15)
    """
    df = dataframe.copy()
    # markers for minutes, hours
    minmarkers = ["min", "minute", "mins", "minutes"]
    hourmarkers = ["hr", "hour", "hrs", "hours"]

    # splitting time column, standardizing markers
    timecols = df[timecol].apply(lambda x: pd.Series(x.split()))
    timecols.replace(minmarkers, "min", inplace=True)
    timecols.replace(hourmarkers, "hr", inplace=True)
    timecols.columns = [str(i) for i in range(9)]

    # conditions for replacement: [(x min), (x hr y min), (x hr)]
    conditions = [
        (timecols["1"] == "min"),
        (timecols["1"] == "hr") & (timecols["3"] == "min"),
        (timecols["1"] == "hr") & (pd.isna(timecols["2"])) & (pd.isna(timecols["3"])),
    ]

    # replacement choices: ['0 x', 'x y', 'x 0']
    choices = [
        "0 " + timecols["0"],
        timecols["0"] + " " + timecols["2"],
        timecols["0"] + " 0",
    ]

    # replacing time col with tuples, default is (x hr, extra instructions)
    df["newtimes"] = np.select(conditions, choices, default=timecols["0"] + " 0")
    df[timecol] = pd.Series(
        [tuple(int(y) for y in str(x).split()) for x in df["newtimes"]]
    )

    return df.drop("newtimes", axis=1)


def getrecipes(cuisine, category, time, rating, ingredients):
    # args_dict = {k:v for k,v in [k.split() for k in kwargs.split(",")]}

    recipes = pd.read_csv("cookieandkaterecipes.csv")
    n = 5

    recipes = time_to_tuples(recipes, "time")
    recipes.drop_duplicates(subset="title", inplace=True)

    maxhrs = 1
    maxmins = max(recipes.time, key=lambda x: x[1])[1]
    cuisines = recipes["cuisine"].unique()
    categories = recipes["category"].unique()

    if cuisine == "Any":
        df = recipes.query(
            "time <= @time and cuisine in @cuisines and category == @category and rating >= @rating"
        )
    if category == "Any":
        df = recipes.query(
            "time <= @time and cuisine == @cuisine and category in @categories and rating >= @rating"
        )
    if cuisine == "Any" and category == "Any":
        df = recipes.query(
            "time <= @time and cuisine in @cuisines and category in @categories and rating >= @rating"
        )
    if cuisine != "Any" and category != "Any":
        df = recipes.query(
            "time <= @time and cuisine == @cuisine and category == @category and rating >= @rating"
        )
    df_ing = df.copy()

    if len(ingredients) > 0:
        ings = ingredients.split(" ")
        print(ings, "BITCH")
        for ingredient in ings:
            df_ing = df_ing[df_ing["ingredients"].str.contains(ingredient)]

    return df_ing.sort_values("rating", ascending=False)[:n]


### NEXT STEPS
#### THINK ABOUT ERRORS - what if you don't have a category or cuisine in the database,
#### what if you don't have certain combos etc
#### how to change input to be more intuitive - select
#### case errors in input
