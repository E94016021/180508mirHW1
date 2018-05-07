import numpy as np
import librosa.feature
import librosa
import time

from concurrent.futures import ProcessPoolExecutor
from dataLoader import Data
from template import template
from ksTemplate import kstemplate


def R(x: np.ndarray, y: np.ndarray):
    """
    :param x:
    :param y:
    :return:

    """
    a = sum([(x[k] - x.mean()) * (y[k] - y.mean()) for k in range(12)])
    b1 = sum([(x[k] - x.mean()) ** 2 for k in range(12)])
    b2 = sum([(y[k] - y.mean()) ** 2 for k in range(12)])
    b = (b1 * b2) ** 0.5

    return a / b


def run(genre, question):
    gammas = [1, 10, 100, 1000]
    d = Data(genre)
    counter = 0
    # print("start analyse", genre)

    if question == 'q1':
        # Parallelization of the load file process
        with ProcessPoolExecutor(max_workers=4) as executor:
            for au, sr, key in executor.map(d.__getitem__, range(d.len)):
                key_pred = match_key(au, sr, 100)
                if key == key_pred:
                    counter += 1
        acc = counter / d.len
        # print("\n", genre, "acc =", acc, "\n")
        accs.append(acc)
    elif question == 'q2':
        for gamma in gammas:
            # Parallelization of the load file process
            with ProcessPoolExecutor(max_workers=4) as executor:
                print("gamma =", gamma)
                for au, sr, key in executor.map(d.__getitem__, range(d.len)):
                    key_pred = match_key(au, sr, gamma)
                    if key == key_pred:
                        counter += 1
            acc = counter / d.len
            # print("\n", genre, "acc =", acc, "\n")
            accs.append(acc)
    elif question == 'q3':
        # Parallelization of the load file process
        with ProcessPoolExecutor(max_workers=4) as executor:
            for au, sr, key in executor.map(d.__getitem__, range(d.len)):
                key_pred = match_key(au, sr, 100)
                counter = counter + q3_score(key, key_pred)
        acc = counter / d.len
        # print("\n", genre, "acc =", acc, "\n")
        accs.append(acc)
    else:
        print("q# error")


def match_key(au, sr, gamma):
    """
    :param au: audio file
    :param sr: sample rate
    :param gamma: gamma parameter of nonlinear transform
    :return: key label

    """
    ##########################################################################
    # tonic = template.argmax()
    # correlation = np.array([R(template[k], tonic) for k in range(24)])
    # major = correlation[tonic]
    # minor = correlation[tonic + 12]
    #
    # if major > minor:
    #     return (correlation.argmax() + 3) % 12  # convert to gtzan key
    # else:
    #     return (correlation.argmax() + 3) % 12 + 12  # convert to gtzan key
    ##########################################################################

    # librosa get chroma with clp
    chroma = np.log(1 + gamma * np.abs(librosa.feature.chroma_stft(y=au, sr=sr)))

    # # normalize chroma
    # chroma = chroma / np.tile(np.sum(np.abs(chroma) ** 2, axis=0) ** (1. / 2),
    #                           (chroma.shape[0], 1))

    vector = np.sum(chroma, axis=1)
    ans = np.array([R(template[k], vector) for k in range(24)])

    return (ans.argmax() + 3) % 24


def ks_match_key(au, sr, gamma):
    """
    :param au: audio file
    :param sr: sample rate
    :param gamma: gamma parameter of nonlinear transform
    :return: key label

    """
    ##########################################################################
    # tonic = template.argmax()
    # correlation = np.array([R(template[k], tonic) for k in range(24)])
    # major = correlation[tonic]
    # minor = correlation[tonic + 12]
    #
    # if major > minor:
    #     return (correlation.argmax() + 3) % 12  # convert to gtzan key
    # else:
    #     return (correlation.argmax() + 3) % 12 + 12  # convert to gtzan key
    ##########################################################################

    # librosa get chroma with clp
    chroma = np.log(1 + gamma * np.abs(librosa.feature.chroma_stft(y=au, sr=sr)))

    # # normalize chroma
    # chroma = chroma / np.tile(np.sum(np.abs(chroma) ** 2, axis=0) ** (1. / 2),
    #                           (chroma.shape[0], 1))

    vector = np.sum(chroma, axis=1)
    ans = np.array([R(kstemplate[k], vector) for k in range(24)])

    return (ans.argmax() + 3) % 24


def q3_score(ans, preds):
    """

    :param ans:
    :param preds:
    :return:
    """
    new_accuracy = 0

    pr = preds
    la = ans
    if pr == la:
        new_accuracy += 1.
    if pr < 12 and la < 12:
        if pr == (la + 7) % 12:
            new_accuracy += 0.5
    elif pr >= 12 and la >= 12:
        pr -= 12
        la -= 12
        if pr == (la + 7) % 12:
            new_accuracy += 0.5

    # Relative major/minor
    if pr < 12 <= la:
        la -= 12
        if pr == (la + 3) % 12:
            new_accuracy += 0.3
    elif pr >= 12 > la:
        pr -= 12
        if (pr + 3) % 12 == la:
            new_accuracy += 0.3

    # Parallel major/minor
    if pr == (la + 12) % 24:
        new_accuracy += 0.2

    return new_accuracy


# def testTime(genre, question, ):
#     """
#
#     :param genre:
#     :return:
#     """
#     for mw in range(1, 10):
#         print("maxWorker =", mw, end=' ')
#         tStart = time.time()
#         accs = []
#
#         d = Data(genre)
#         counter = 0
#         print("start analyse", genre)
#
#         # Parallelization of the load file process
#         with ProcessPoolExecutor(max_workers=mw) as executor:
#             for au, sr, key in executor.map(d.__getitem__, range(d.len)):
#                 key_pred = match_key(au, sr, gamma)
#                 # print("[%d,%d]" % (key, key_pred), end=' ', flush=True)
#                 counter = counter + q3_score(key, key_pred)
#                 # if key == key_pred:
#                 #     counter += 1
#
#         acc = counter / d.len
#         # print("\n", genre, "acc =", acc, "\n")
#         accs.append(acc)
#
#         result = list(zip(genre, accs))
#         # print("------------------------------------------\n", result,
#         #       "\n------------------------------------------\n")
#         print(result)
#         tEnd = time.time()
#         duration = tEnd - tStart
#
#         print("%f sec" % (tEnd - tStart))
#
#     print("tResult :\n" + str(duration))


if __name__ == "__main__":
    genres = ['pop', 'blues', 'metal', 'rock', 'hiphop']
    questions = ['q1', 'q2', 'q3']
    accs = []
    # tStart = time.time()

    # testTime('blues')

    # f = open("file.txt", 'w')
    # print("fuck", file=f)

    for question in questions:
        print(question)

        for genre in genres:
            run(genre, question)
            mix = list(zip(genres, accs))

        print(mix)

    # for genre in genres:
    #
    #     d = Data(genre)
    #     counter = 0
    #     # print("start analyse", genre)
    #
    #     # Parallelization of the load file process
    #     with ProcessPoolExecutor(max_workers=4) as executor:
    #         for au, sr, key in executor.map(d.__getitem__, range(d.len)):
    #             key_pred = match_key(au, sr, gamma)
    #             # print("[%d,%d]" % (key, key_pred), end=' ', flush=True)
    #             counter = counter + q3_score(key, key_pred)
    #             # if key == key_pred:
    #             #     counter += 1
    #
    #     acc = counter / d.len
    #     # print("\n", genre, "acc =", acc, "\n")
    #     accs.append(acc)

    # result = list(zip(genres, accs))
    # print("----------------------------------------------\n", result,
    #       "\n------------------------------------------\n")
    # tEnd = time.time()
    # print("It cost %f sec" % (tEnd - tStart))

"""
result:

[('pop', 0.16), ('blues', 0.07), ('metal', 0.05), ('rock', 0.17), ('hiphop', 0.01)]

"""