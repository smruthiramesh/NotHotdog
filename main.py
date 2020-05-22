import pandas as pd
import numpy as np

def time_to_tuples(dataframe,timecol):
    ''' given a df with a str representation of time,
        replaces time col with a tuple representation to make it searchable
        e.g.: 1 hr 15 min = (1,15)
    ''' 
    df = dataframe.copy()
    #markers for minutes, hours
    minmarkers = ["min","minute","mins","minutes"]
    hourmarkers = ["hr","hour","hrs","hours"]

    #splitting time column, standardizing markers
    timecols = df[timecol].apply(lambda x: pd.Series(x.split()))
    timecols.replace(minmarkers,"min",inplace=True)
    timecols.replace(hourmarkers,"hr",inplace=True)
    timecols.columns = [str(i) for i in range(9)]

    #conditions for replacement: [(x min), (x hr y min), (x hr)]
    conditions = [
    (timecols["1"] == "min"),
    (timecols["1"] == "hr") & (timecols["3"] == "min"),
    (timecols["1"] == "hr") & (pd.isna(timecols["2"])) & (pd.isna(timecols["3"]))
    ]

    #replacement choices: ['0 x', 'x y', 'x 0']
    choices = [
        "0 "+timecols["0"],
        timecols["0"]+" "+timecols["2"],
        timecols["0"]+" 0"
        ]

    #replacing time col with tuples, default is (x hr, extra instructions)
    df["newtimes"] = np.select(conditions,choices,default=timecols["0"]+" 0")
    df[timecol] = pd.Series([tuple(int(y) for y in str(x).split()) for x in df["newtimes"]])
    
    return df.drop("newtimes",axis=1)


def main(**kwargs):
    recipes = pd.read_csv("cookieandkaterecipes.csv")

    recipes = time_to_tuples(recipes, "time")
    recipes.drop_duplicates(subset="title",inplace=True)

    maxhrs = 1
    maxmins = max(recipes.time, key= lambda x:x[1])[1]
    cuisines = recipes["cuisine"].unique()
    categories = recipes["category"].unique()

    #possible arguments: time,cuisine,category,rating
    #getting arguments/picking random values
    time = tuple(int(k) for k in kwargs.get("time", str(maxhrs)+":"+str(maxmins)).split(":"))
    cuisine = kwargs.get("cuisine", np.random.choice(cuisines))
    category = kwargs.get("category", categories).tolist()
    rating = float(kwargs.get("rating", 4))

    return recipes.query('time <= @time and cuisine == @cuisine and category in @category and rating >= @rating').\
        sort_values("rating",ascending=False)[:3]

if __name__ == "__main__":
    args = input()
    args_dict = {k:v for k,v in [k.split() for k in args.split(",")]}
    print(main(**args_dict)[["cuisine","title","rating","category","time"]])


### curr input format: cuisine American, time 110, rating 4, category Breakfast

### NEXT STEPS
#### THINK ABOUT ERRORS - what if you don't have a category or cuisine in the database,
#### what if you don't have certain combos etc
#### how to change input to be more intuitive - select
#### case errors in input