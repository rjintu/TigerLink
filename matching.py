import zipcodes
from database import Database

class Matching(object):

    #student info: netid, #matches, career interest, major, year, zip, weighting
    #alumni info: netid, #matches, career field, major, year, zip, weighting
    def __init__(self):
        try:
            db = Database()
            db.connect()
            db.init()

    
    # Schematic for matching students-alumni
    # 1) create a PQueue where people are added in a random order for the first time
    # 2) first, all the people w one match are added. then, all the people w at least 2.
    # 3) etc, etc such that no person will have more than one match over anyone else who had
    # 4) the same preference of people

    # next, the way the matching works is as follows (in terms of priority)
    # 1) Career Interest 2) Zip 3) Major
    # generate a vector representing a specific person and then dot-product with all others

    def vectorize(student):
        return [student[0], student[1], student[2], student[3], student[4]]

    def getVecs():
        sVecs = []
        aVecs = []
        for student in self._students:
            sVecs.append(vectorize(student))
        for alum in self._alumni:
            aVecs.append(vectorize(alum))
        return sVecs, aVecs


    def match():
        sVecs, aVecs = getVecs()
        matches = []
        for svec in sVecs:
            bestSim = 0
            bestIdx = 0
            for idx, avec in enumerate(aVecs):
                if sim > bestSim:
                    bestSim = sim
                    bestIdx = idx
            alum = avec[bestIdx]
            aVecs.remove(alum)
            matches.append((svec[0], alum[0], bestSim))
        return matches

    def careerDiff(sC, aC):
        if sC == aC:
            return 1
        return 0

    def majorDiff(sM, aM):
        if sM == aM:
            return 1
        return 0


    #svec[0] = id (ignore)
    #svec[1] = careeer (on a scale of 1 - 30)
    #svec[2] = major (on a scale of 1 - 25)
    #svec[3] = year (not needed rn)
    #svec[4] = zip (free form, find the distance)
    def dotProduct(svec, avec):
        c = careerDiff(svec[1], avec[1])
        m = majorDiff(svec[2], avec[2])



    def similarity():
