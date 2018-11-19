import os
import sys
import random
import xml.etree.ElementTree as etree
import numpy as np

from clusterize import predict
from Relations import r, coeffs, MatchType

if __name__ == "__main__":
    # init dataset
    directory = sys.argv[1]
    dataset = []
    for filename in os.listdir(directory):
        tree = etree.parse(directory + "/" + filename)
        root = tree.getroot()

        mentions = []

        # read mentions
        for child in root.iter('StrictName'):
            if child[1].attrib['val'] == 'NONE' and child[2].attrib['val'] == 'NONE' \
                    and child[3].attrib['val'] == 'NONE':
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

        dataset.append(mentions)

    print("Dataset size:", len(dataset))

    # init target coeffs
    coeffs = [random.random() for _ in range(10)]

    ITERATION_SIZE = 100
    DATAPART_SIZE = 11
    LEARN_THRESHOLD = 0.1
    iterations = 0
    while iterations < ITERATION_SIZE:
        print("Start iteration:", iterations)
        dataset_iterator = 0
        new_coeffs = [0.0 for _ in range(10)]
        while dataset_iterator + DATAPART_SIZE < len(dataset):
            datapart = dataset[dataset_iterator:dataset_iterator + DATAPART_SIZE]
            full_entities = []
            for document in datapart:
                entities = predict(document)
                full_entities.append(entities)

            last_coeffs = coeffs.copy()
            for match in range(10):
                match_enum = MatchType(match)
                pos_count = 0.0
                full_pos_count = 0.0
                neg_count = 0.0
                full_neg_count = 0.0
                count = 0.0
                full_count = 0.0

                for document in range(len(datapart)):
                    for entity in full_entities[document]:
                        for a in entity:
                            for b in entity:
                                if not (a is b):
                                    result = 0.0 if r(datapart[document], a, b, match_enum) != 1.0 else 1.0
                                    pos_count += result
                                    neg_count += 1.0 - result
                                    count += 1.0

                    for a in range(len(datapart[document])):
                        for b in range(len(datapart[document])):
                            if a != b:
                                result = 0.0 if r(datapart[document], a, b, match_enum) != 1.0 else 1.0
                                full_pos_count += result
                                full_neg_count += 1.0 - result
                                full_count += 1.0


                def logL(k, n):
                    return k * np.log(k / n) + (n - k) * np.log(1 - (k / n))


                lr = 0 if pos_count == 0 else \
                    2 * (logL(pos_count, full_pos_count) + logL(neg_count, full_neg_count) -
                         logL(count, full_count) - logL((full_count - count), full_count))
                new_coeffs[match] += lr / (len(dataset) / DATAPART_SIZE) if lr > 15 else coeffs[match]

            dataset_iterator += DATAPART_SIZE

        coeff_delta = sum(np.abs(np.subtract(coeffs, new_coeffs)))
        coeffs = np.divide(new_coeffs, np.average(new_coeffs))
        print("Delta:", coeff_delta)
        #print(coeffs)
        if coeff_delta < LEARN_THRESHOLD:
            pass
        iterations += 1

    print(coeffs)
# [7547.779687549429, 7370.560696846439, 0, 7621.7671731875935, 7359.9630068893475, 0, 7393.059471743922, 0, 0, 7377.714808089091]
# [17390.609054977325, 17005.836521839523, 0, 17341.00307384879, 17200.020015525355, 0, 17001.184609536514, 0, 0, 17136.45645576466]
# [2, 0, 0, 3, 0, 0, 0, 0, 0, 1]