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
    def studentize(self, students, careers, organizations=None):
        newS = []
        #TODO: a little inefficient
        for student in students:
            pid = student[0]
            cs = []
            for row in careers:
                if row[0] == pid:
                    cs.append(row[1])

            s = Student(pid, student[1], student[2], student[3],
            student[4], student[5], student[6], student[7], careers=cs,
            organizations=organizations)
            newS.append(s)
        return newS

    # convert to an alumni object
    def alumnize(self, alumni, careers, organizations=None):
        newA = []
        for alum in alumni:
            pid = alum[0]
            cs = []
            for row in careers:
                if row[0] == pid:
                    cs.append(row[1])

            a = Alum(pid, alum[1], alum[2], alum[3],
            alum[4], alum[5], alum[6], alum[7], careers=cs,
            organizations=organizations)
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
            s, c = db.get_students()
            self._students = self.studentize(s, c)
            s2, c2 = db.get_alumni()
            self._alumni = self.alumnize(s2, c2)
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
        random.shuffle(students)

        matches = []
        for svec in students:
            # check ending condition
            if len(alumni) == 0:
                return matches
            students.remove(svec)
            
            bestSim = 0
            bestIdx = 0
            for idx, avec in enumerate(alumni):
                sim = dotProduct(svec, avec)
                if sim > bestSim:
                    bestSim = sim
                    bestIdx = idx
            alum = avec[bestIdx]
            aVecs.remove(alum)
            
            #TODO: change to a student
            matches.append((svec, avec, bestSim))

            # assign more matches
            if svec._numMatch > 1:
                svec._numMatch -= 1
                students.append(svec)
        print(matches)
        return matches


    #sprefs = weightings for career, major, and organizations
    def dotProduct(svec, avec):
        m = 0
        if (svec._major == avec._major):
            m = 1

        carS = 0
        for career in svec._careers:
            if career in avec._careers:
                carS += 1
                
        orgS = 0
        for org in svec._organizations:
            if org in avec._organizations:
                orgS += 1
        
        vals = [m, carS, orgS]

        sim = 0
        #TODO: add spref to the student class
        for i, weight in enumerate(svec._sprefs):
            sim += vals[i] * weight
        
        return sim