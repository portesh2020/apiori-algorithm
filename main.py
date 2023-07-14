import pandas as pd
import sys
from itertools import combinations


def get_street(row):
    street = set()
    for key in row:
        if key == 'street_id' or key == 'street_name':
            continue
        if row[key] == 1:
            street.add(key)
    return street


def get_streets(table):
    streets = list()
    for row in table.to_dict('records'):
        street = get_street(row)
        streets.append(street)
    return streets


def get_itemset_counts(itemset_counts, streets, itemsets):
    for street in streets:
        for itemset in itemsets:
            itemset_key = '_'.join(sorted(itemset))
            if itemset_key not in itemset_counts:
                itemset_counts[itemset_key] = 0
            if itemset.issubset(street):
                itemset_counts[itemset_key] += 1
    return itemset_counts


def get_large_itemsets(all_large_itemsets, candidates, itemset_counts, total, min_supp):
    large_itemsets = list()
    for itemset in candidates:
        itemset_sorted = sorted(itemset)
        itemset_key = '_'.join(itemset_sorted)
        supp = float(itemset_counts[itemset_key] / total)
        if supp >= min_supp:
            large_itemsets.append(itemset)
            all_large_itemsets.append((itemset, supp))
    return large_itemsets, all_large_itemsets


def is_joinable(itemset1, itemset2):
    itemset1_sorted = sorted(itemset1)
    itemset2_sorted = sorted(itemset2)
    for i in range(len(itemset1) - 1):
        if itemset1_sorted[i] != itemset2_sorted[i]:
            return False
    return True


def get_apriori_candidates(large_itemsets, k):
    candidates = list()

    # 'join' step
    for i in range(len(large_itemsets)):
        itemset1 = large_itemsets[i]
        for j in range(i + 1, len(large_itemsets)):
            itemset2 = large_itemsets[j]
            if is_joinable(itemset1, itemset2):
                candidates.append(itemset1.union(itemset2))

    # 'prune' step
    for itemset in candidates:
        subsets = list(combinations(itemset, k - 1))
        for subset in subsets:
            if set(subset) not in large_itemsets:
                candidates.remove(itemset)
                break

    return candidates


def get_association_rules(association_rules, large_itemsets, itemset_counts, total, min_conf):
    candidate_rules = list()

    for itemset in large_itemsets:
        for item in itemset:
            lhs = itemset.copy()
            lhs.remove(item)
            rhs = list()
            rhs.append(item)
            candidate_rules.append((itemset, lhs, rhs))

    for rule in candidate_rules:
        itemset = sorted(rule[0])
        lhs = sorted(rule[1])
        rhs = rule[2]

        if not lhs:
            continue

        itemset_key = '_'.join(itemset)
        lhs_key = '_'.join(lhs)
        itemset_supp = float(itemset_counts[itemset_key] / total)
        lhs_supp = float(itemset_counts[lhs_key] / total)
        conf = round(itemset_supp / lhs_supp, 3)

        if conf >= min_conf:
            association_rules.append((lhs, rhs, conf, itemset_supp))

    return association_rules


def apriori(integrated_dataset, min_supp, min_conf):
    candidates = list()
    for col in list(integrated_dataset.columns):
        if col != 'street_id' and col != 'street_name':
            itemset = set()
            itemset.add(col)
            candidates.append(itemset)
    streets = get_streets(integrated_dataset)
    itemset_counts = get_itemset_counts(dict(), streets, candidates)
    large_itemsets, all_large_itemsets = get_large_itemsets(list(), candidates, itemset_counts, len(streets), min_supp)
    association_rules = list()
    k = 2

    while large_itemsets:
        candidates = get_apriori_candidates(large_itemsets, k)
        if not candidates:
            break
        itemset_counts = get_itemset_counts(itemset_counts, streets, candidates)
        large_itemsets, all_large_itemsets = get_large_itemsets(all_large_itemsets, candidates, itemset_counts, len(streets), min_supp)
        association_rules = get_association_rules(association_rules, large_itemsets, itemset_counts, len(streets), min_conf)
        k += 1

    return all_large_itemsets, association_rules


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 main.py <source file> <minimum support> <minimum confidence>")
        exit()

    filename = sys.argv[1]
    min_supp = float(sys.argv[2])
    min_conf = float(sys.argv[3])

    integrated_dataset = pd.read_csv(filename)
    all_large_itemsets, association_rules = apriori(integrated_dataset, min_supp, min_conf)

    output = open('output.txt', 'w')
    output.write('==================== Large itemsets (min_supp = {}%) ====================\n'.format(round(min_supp * 100)))
    all_large_itemsets.sort(key=lambda x: x[1], reverse=True)
    for itemset in all_large_itemsets:
        output.write('{}, {}%\n'.format(sorted(itemset[0]), round(itemset[1] * 100)))
    output.write('\n========== High confidence association rules (min_conf = {}%) ==========\n'.format(round(min_conf * 100)))
    association_rules.sort(key=lambda x: x[2], reverse=True)
    for rule in association_rules:
        output.write('{} -> {} (Conf: {}%, Supp: {}%)\n'.format(rule[0], rule[1], round(rule[2] * 100), round(rule[3] * 100)))


if __name__ == "__main__":
    main()
