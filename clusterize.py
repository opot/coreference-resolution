# encoding: "utf-8"
import sys
import xml.etree.ElementTree as etree

from Relations import MatchType, r, informative_score, NONE, THRESHOLD

# TODO learning
# TODO nob parts

tree = etree.parse(sys.argv[1])
root = tree.getroot()

mentions = []

# read mentions
for child in root.iter('StrictName'):
    if child[1].attrib['val'] == 'NONE' and child[2].attrib['val'] == 'NONE' and child[3].attrib['val'] == 'NONE':
        continue
    else:
        mention = {
            'fname': child[1].attrib['val'].lower(),
            'lname': child[2].attrib['val'].lower(),
            'patr': child[3].attrib['val'].lower(),
            'gen': child[4].attrib['val'].lower(),
        }

        for part in ['fname', 'lname', 'patr']:
            if mention[part].endswith('-то'):
                mention[part] = mention[part][:-3]
        mentions.append(mention)

# clusterize entities
entities = []
for current in range(len(mentions)):
    relations = [
        [
            [
                r(mentions, current, i, match)
                for match in MatchType
            ]
            for i in entity
        ]
        for entity in entities

    ]

    best_relation = [
        (0, 0) if any(map(lambda e: any(map(lambda x: x == -1, e)), relations[entity_num])) else
        max([
            (match_num, max([
                informative_score(match_num) * relations[entity_num][i][match_num]
                for i in range(len(entities[entity_num]))
            ], default=0)
             )
            for match_num in range(10)
        ], key=lambda x: x[1])
        for entity_num in range(len(entities))
    ]

    condidates = list(filter(lambda x: best_relation[x][1] > 0, range(len(entities))))

    if len(condidates) == 0:
        entities.append([current])
        continue

    probabilities = [
        sum(relations[entity][mention][best_relation[entity][0]] for mention in range(len(entities[entity])))
        /
        sum(sum(relations[entity][mention][best_relation[entity][0]] for mention in range(len(entities[entity2])))
            for entity2 in condidates
            )
        for entity in condidates
    ]

    max_ind = 0
    for cond in range(1, len(condidates)):
        if probabilities[cond] > probabilities[max_ind]:
            max_ind = cond
            continue

        if probabilities[cond] == probabilities[max_ind]:
            if informative_score(best_relation[cond][0]) > informative_score(best_relation[max_ind][0]):
                max_ind = cond

    if probabilities[max_ind] >= THRESHOLD:
        entities[max_ind].append(current)
    else:
        entities.append([current])

# print entities
for entity in entities:
    obj = {}
    for mention in entity:
        for key in mentions[mention]:
            if mentions[mention][key] != NONE:
                obj[key] = mentions[mention][key]
    print(obj)
