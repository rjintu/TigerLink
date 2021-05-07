from .database import Database
from .student import Student
from .alum import Alum
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
import random


''' HOW TO RUN MATCHING
1) create a Matching object 
2) call match method on that, which will return pairings
'''
class Matching(object):

    # convert to a student object
    def studentize(self, students, careers, communities):
        newS = []
        for student in students:
            if len(student) >= 7 and int(student[6]) > 0:
                pid = student[0]
                cs = []
                orgs = []
                for row in careers:
                    if (len(row) > 1):
                        if row[0] == pid:
                            cs.append(row[1])
                for row in communities:
                    if (len(row) > 1):
                        if row[0] == pid:
                            orgs.append(row[1])

                s = Student(pid, student[1], student[2], student[3],
                student[4], student[5], student[6], propic=None, careers=cs, communities=orgs)
                newS.append(s)
        return newS

    # convert to an alumni object
    def alumnize(self, alumni, careers, communities):
        newA = []
        for alum in alumni:
            if len(alum) >= 7 and int(alum[6]) > 0:
                pid = alum[0]
                cs = []
                orgs = []
                for row in careers:
                    if (len(row) > 1):
                        if row[0] == pid:
                            cs.append(row[1])
                for row in communities:
                    if (len(row) > 1):
                        if row[0] == pid:
                            orgs.append(row[1])

                a = Alum(pid, alum[1], alum[2], alum[3],
                alum[4], alum[5], alum[6], propic=None, careers=cs, communities=orgs)
                newA.append(a)
        return newA

    #student info: gauth, netid, fname, lname, year, email,
    #           major, zipp, numMatch, grad = None, career = None, organizations = None
    #alumni info: gauth, netid, fname, lname, year, email,
    #           major, zipp, numMatch, career = None, organizations = None
    def __init__(self):
        try:
            db = Database()
            db.connect()
            self._curMatches = db.all_matches()
            s, c, i = db.get_students()
            self._students = self.studentize(s, c, i)
            s2, c2, i2 = db.get_alumni()
            self._alumni = self.alumnize(s2, c2, i2)
            self._majorScore = {'AAR': 0.33, 'ANT': 0.25, 'ARC': 3.35, 'AST': 3.30, 'CEE': 3.00, 'CBE': 3.10,
            'CHM': 3.15, 'CLA': 0.63, 'COL': 1000, 'COS': 3.40, 'EAS': 0.83, 'ECO': 3.60, 'EEB': 3.13, 'ECE': 3.42,
            'ENG': 0.68, 'FIT': 0.88, 'GEO': 0.35, 'GLL': 0.90, 'HIS': 0.40, 'HUM': 0.70, 'LAT': 0.92,
            'LIN': 0.97, 'MAE': 3.40, 'MAT': 3.47, 'MOL': 3.20, 'MUS': 0.05, 'NES': 0.85, 'ORF': 3.45, 'PHI': 0.12, 
            'PHY': 3.32, 'POL': 0.45, 'PSY': 3.25, 'REL': 0.30, 'SOC': 0.28, 'SPI': 0.48, 'VIS': 0.10}
            db.disconnect()
        except Exception as e:
            html = "error occurred: " + str(e)
            print(e)
            make_response(html)
    
    
    # Schematic for matching students-alumni
    # 1) create a PQueue where people are added in a random order for the first time
    # 2) first, all the people w one match are added. then, all the people w at least 2.
    # 3) etc, etc such that no person will have more than one match over anyone else who had
    # 4) the same preference of people

    # generate a vector representing a specific person and then dot-product with all others
    # according to a specific set of preferences

    def _processMatches(self):
        matches = []
        fm = []
        for match in self._curMatches:
            if match[0] in self._students:
                match[0]._numMatch -= 1
            if match[1] in self._alumni:
                match[1]._numMatch -= 1
            matches.append((match[0], match[1]))
            fm.append((match[0]._profileid, match[1]._profileid, match[2], match[3], match[4], match[5], dotProduct(match[0], match[1])))

        return matches, fm

    def match(self):
        students = self._students
        alumni = self._alumni
        matches, finalMatches = self._processMatches()
        absoluteFinal = []
        topSim = 0
        while (len(students) > 0):
            if len(alumni) == 0:
                if topSim == 0:
                    return finalMatches
                for match in finalMatches:
                    sim = float(match[6])/topSim
                    sim = round(sim*100, 2)
                    absoluteFinal.append((match[0], match[1], match[2], match[3], match[4], match[5], sim))
                return absoluteFinal

            svec = students[0]
            students.remove(svec)
            if svec._numMatch > 0:
                bestSim = -1
                bestIdx = -1
                updated = False
                for idx in range(len(alumni)):
                    avec = alumni[idx]
                    # make sure no re-matches EVER
                    potentialMatch = (svec, avec)
                    if potentialMatch not in matches and avec._numMatch > 0:
                        sim = self.dotProduct(svec, avec)
                        if sim > bestSim:
                            bestSim = sim
                            bestIdx = idx
                            updated = True
                                
                if updated:
                    if topSim < bestSim:
                        topSim = bestSim
                    alum = alumni[bestIdx]
                    match = (svec, alum)
                    
                    #match = (svec._name, svec._year, alum._name, alum._year, bestSim)
                    matches.append(match)
                    finalMatches.append((svec._profileid, alum._profileid, svec._name, svec._year, alum._name, alum._year, bestSim))
                    
                    del(alumni[bestIdx])
                    alum._numMatch -= 1

                    if alum._numMatch > 0:
                        alumni.append(alum)

                    svec._numMatch -= 1
                    if svec._numMatch > 0:
                        students.append(svec)
        if topSim == 0:
            return finalMatches
        for match in finalMatches:
            sim = float(match[6])/topSim
            sim = round(sim*100, 2)
            absoluteFinal.append((match[0], match[1], match[2], match[3], match[4], match[5], sim))
        return absoluteFinal

    #sprefs = weightings for career, major, and organizations
    def dotProduct(self, svec, avec):
        m = 0
        sScore = self._majorScore[svec._major]
        aScore = self._majorScore[avec._major]
        m = max(1 - abs(aScore-sScore)*2, 0)

        carS = 0
        if svec._careers != None and (len(svec._careers) + len(avec._careers)) > 0:
            for career in svec._careers:
                if career in avec._careers:
                    carS += 1

            totalC = svec._careers + [x for x in avec._careers if x not in set(svec._careers)]
            carS /= len(totalC)

        orgS = 0
        if svec._communities != None and (len(svec._communities) + len(avec._communities)) > 0:
            for org in svec._communities:
                if org in avec._communities:
                    orgS += 1

            totalO = svec._communities + [x for x in avec._communities if x not in set(svec._communities)]
            orgS /= len(totalO)

        vals = [m, carS, orgS]

        sim = 0
        for i, weight in enumerate(svec._spref):
            sim += vals[i] * weight

        finalS = round(sim * 100, 2)

        return finalS
