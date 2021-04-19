# import zipcodes
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
    def studentize(self, students, careers, organizations):
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
                for row in organizations:
                    if (len(row) > 1):
                        if row[0] == pid:
                            orgs.append(row[1])

                s = Student(pid, student[1], student[2], student[3],
                student[4], student[5], student[6], careers=cs, organizations=orgs)
                newS.append(s)
        return newS

    # convert to an alumni object
    def alumnize(self, alumni, careers, organizations):
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
                for row in organizations:
                    if (len(row) > 1):
                        if row[0] == pid:
                            orgs.append(row[1])

                a = Alum(pid, alum[1], alum[2], alum[3],
                alum[4], alum[5], alum[6], careers=cs, organizations=orgs)
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
            s, c, i = db.get_students()
            self._students = self.studentize(s, c, i)
            s2, c2, i2 = db.get_alumni()
            self._alumni = self.alumnize(s2, c2, i2)
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

    def match(self):
        students = self._students
        alumni = self._alumni
        matches = []
        finalMatches = []
        absoluteFinal = []
        topSim = 0
        while (len(students) > 0):
            if len(alumni) == 0:
                if topSim == 0:
                    return finalMatches
                for match in finalMatches:
                    sim = float(match[6])/topSim
                    sim = round(sim, 2) * 100
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
            sim = round(sim, 2) * 100
            absoluteFinal.append((match[0], match[1], match[2], match[3], match[4], match[5], sim))
        return absoluteFinal

    #sprefs = weightings for career, major, and organizations
    def dotProduct(self, svec, avec):
        m = 0
        if (svec._major == avec._major):
            m = 1

        carS = 0
        if svec._careers != None:
            for career in svec._careers:
                if career in avec._careers:
                    carS += 1

            totalC = len(list(set().union(svec._careers, avec._careers)))
            carS /= totalC

        orgS = 0
        if svec._organizations != None:
            for org in svec._organizations:
                if org in avec._organizations:
                    orgS += 1

            totalO = len(list(set().union(svec._organizations, avec._organizations)))
            orgS /= totalO

        vals = [m, carS, orgS]

        sim = 0
        for i, weight in enumerate(svec._spref):
            sim += vals[i] * weight

        finalS = round(sim, 2) * 100

        return finalS