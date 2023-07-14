## Authors
Kate Jeon 
Hannah Portes 


## Files
Name | Purpose
--- | ---
`main.py` | Apriori algorithm implementation
`integrated_dataset.csv` | Source data file
`example-run.txt` | Sample output using `min_supp` = 0.1 and `min_conf` = 0.3


## Installation & Usage
### Dependencies
```shell
sudo apt install python3-pip # if pip3 is not installed
pip3 install pandas --upgrade
```

### Program Run Instructions
In the root of the project directory run the following command:
```shell
$ python3 main.py <source file> <minimum support> <minimum confidence>
```
- `source file` is the filename of the source data (e.g. `integrated_dataset.csv`)
- `minimum support` is a number between 0 and 1, indicating the support threshold
- `minimum confidence` is a number between 0 and 1, indicating the confidence threshold


## Architectural Design
### Integrated Dataset
The dataset we chose to work with is titled ``DOHMH New York City Restaurant Inspection Results`` accessible at https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j.

First we replaced all street names that had typos or were spelled slightly differently despite being the same address.

For example, the following addresses are all the same, entered slightly differently into the dataset.

- 126 ST & Roosevelt Ave
- 126 St &  ROOSEVELT AVENUE
- 126 TH  & ROOSEVELT AVENUE
- 126 TH ST & ROOSEVELT AVENUE
- 126TH  & ROOSEVELT AVENUE
- etc.

We standardized these to one value (126 STREET & ROOSEVELT AVENUE) to enable us to group cuisines by street accurately.
Additionally, some streets had the same name but were in different boroughs of New York City, indicating that they share an address by name but not the actual same physical address. To distinguish these, we added the borough column onto the street names.

We similarly sorted the cuisine names in the following way:
```
'Asian/Asian Fusion': 'asian/fusion',
'Southeast Asian': 'southeast/asian',
'Bottled Beverages': 'bottled/beverages',
'Bakery Products/Desserts': 'bakery/desserts',
'Middle Eastern': 'middle/eastern',
'Frozen Desserts': 'frozen/desserts',
'Eastern European': 'eastern/european',
'Chinese/Cuban': 'chinese',
'Chinese/Japanese': 'chinese',
'Soul Food': 'soul/food',
'Creole/Cajun': 'creole',
'Hotdogs': 'hotdogs/pretzels',
'Juice, Smoothies, Fruit Salads': 'juice/smoothies/fruit/salads',
'New American': 'american',
'New French': 'french',
'Sandwiches/Salads/Mixed Buffet': 'sandwiches',
'Soups/Salads/Sandwiches': 'sandwiches',
'Latin American': 'latin/american',
'Tex-Mex': 'tex/mex'
```

We then selected only the street and cuisine columns from the entire dataset. Keeping the street names as the market baskets, we used get_dummies to set all the cuisines as columns, with 1 representing the cuisine corresponding to the street entry, and the rest of the columns set as 0. After this step the dataframe is grouped by street, so that we get an overall count of all cuisines registered to a single street in this dataset.

Since we do not need raw counts of each cuisine per street, we set all values greater than 0 to 1, and all zeros remain.

This final dataframe, with each street acting as a market basket and each cuisine anywhere on this street as an item, is then output to our final integrated_dataset.csv.

### Helper Functions
- `get_street`
    - Returns a set of all cuisine types existing in a street.
    - e.g.
        ```python
        street1 = {'american', 'chinese', 'pizza'}
        street2 = {'french', 'mexican', 'turkish'}
        street3 = {'french', 'italian', 'moroccan', 'turkish'}
        ```

- `get_streets`
    - Returns a list of all sets representing streets from the data.
    - e.g.
        ```python
        streets = [street1, street2, street3]
        ```

- `get_itemset_counts`
    - Returns a dictionary of itemsets as keys and its counts as values. When there are more than one item in an itemset, the key for the itemset is all items joined with underscore.
    - e.g.
        ```python
        {
            'american': 1,
            'chinese': 1,
            'french': 2,
            'italian': 1,
            'mexican': 1,
            'moroccan': 1,
            'pizza': 1,
            'turkish': 2,
            .
            .
            .
            'french_turkish': 2,
            .
            .
            .
            'moroccan_pizza_turkish': 0
            .
            .
            .
        }
        ```

- `get_large_itemsets`
    - Returns two lists `large_itemsets` and `all_large_itemsets`. The former is large itemsets for each iteration and the latter is a list of all large itemsets extracted so far. If the program is inside the third iteration, then `large_itemsets` is L3 discussed in class while `all_large_itemsets` is a union of all L1, L2, and L3. Note that `all_large_itemsets` saves both itemset and its support as a tuple.
    - e.g.
        ```python
        # inside iteration 2
        large_itemsets = [{'french', 'turkish'}] # L2
        all_large_itemsets = [({'french'}, 0.667), ({'turkish'}, 0.667), ({'french', 'turkish'}, 0.667)]
        ```

- `is_joinable`
    - Checks if two itemsets contain one different element each from another. This is equivalent to the `WHERE` clause from the SQL query discussed in class.
        ```sql
        FROM L_k P, L_k Q
        WHERE P.item_1 = Q.item_1
            AND ...
            AND P.item_(k - 1) = Q.item_(k - 1)
            AND P.item_k < Q.item_k
        ```

- `get_apriori_candidates`
    - This is equivalent to `candidate-gen` function mentioned in Section 2.1.1 of Agrawal and Srikant paper in VLDB 1994. It first joins all possible itemsets that meet the `is_joinable` condition. Then, it prunes the newly joined itemsets and returns the final candidate itemsets.

- `get_association_rules`
    - Returns a list of all association rules that have been extracted so far. In each iteration, it passes the large itemsets to this function and the function chooses one item as RHS and the rest as LHS, checks if this rule surpasses the confidence threshold. The calculation for confidence is calculated as the support of the overall itemset divided by the support of the set on the left hand side of this candidate association rule. If this confidence surpasses the requested confidence, the rule is output to our final txt file.

- `apriori`
    - The main Apriori algorithm that derives all association rules. It first finds singleton large itemsets and runs an infinite loop until the large itemsets is empty by solving large itemsets with more elements.

### Main Function
This program extracts association rules between New York City eateries in vicinity. The program takes in the source data file, minimum support, and minimum confidence as arguments. It reads the data into a dataframe where each row represents a street (corresponds to a basket in market-basket model) and columns indicate cuisine types. Then, it runs the apriori algorithm to derive all large itemsets and association rules, and writes to an output file in descending order of support and confidence respecitvely.


## Sample Runs and Analysis
```shell
$ python3 main.py integrated_dataset.csv 0.1 0.3
$ python3 main.py integrated_dataset.csv 0.03 0.4
$ python3 main.py integrated_dataset.csv 0.06 0.7
```

- The program performs best with minimum support values of 0.03 and higher. With a value of 0.03 the program runs in under 20 seconds, and with any higher values the program runs in under 10 seconds.
- The highest minimum support value to produce association rules is 0.23. Using an extremely low confidence of 0.01 and support of 0.23 should produce the following two rules
```shell
python3 main.py integrated_dataset.csv 0.23 .01

>>> ['coffee/tea'] -> ['american'] (Conf: 74%, Supp: 23%)
>>> ['american'] -> ['coffee/tea'] (Conf: 42%, Supp: 23%)
```

- Running with a support of 0.01 and confidence of 0.7 produces a lengthy output with around 7500 rows
```shell
python3 main.py integrated_dataset.csv 0.04 .7
```