# Project for Covid Contact Tracing. Functions take in a 7-tuple data argument. The 7-tuple
# represents a person's visit to a location at a certain time
# E.g.  ("Name", "Location", hourEntry, minuteEntry, hourLeave, minuteLeave)
# List of inputs provided below

def forward_contact_trace(visits, index, day_time, second_order=False):
    """Provides names of those potentially infected through first and 
    second-order contact. Uses a list of visits under 7-tuple data, an 
    infectee, and time of infection."""
    names = []
    contacts = [] 
    infectiontimes = {}
    
    # calling function to assign variables, indexvisits is all visits by the 
    # infected, and infectedvisits are only visits after individual is infected
    infectedvisits = (infected_visits(visits, index, day_time, [], []))[0]
    indexvisits = (infected_visits(visits, index, day_time, [], []))[1]    
    othervisits = set(visits.copy()) - set(indexvisits) 
    
    for people in visits:
        names.append(people[0])    
    
    names = set(names)- set([index])
    
    for name in names:
        visit_set = [] 
        infectiontime = ()
        
        # create a seperate set of visits for each individual
        for visit in othervisits:
            if name == visit[0]:
                visit_set.append(visit) 
                
        # check if any of the infected visits overlap with another person's 
        # visit
        if (potential_contacts(infectedvisits, visit_set))[0]: 
            contacts.append(name)
         
            for times in (potential_contacts(infectedvisits, visit_set))[0]:
                # store day, hour and minute in a tuple
                time_data = (times[1], times[2], times[3]) 
               
                if infectiontime:  # if a value already exists in list
                    if time_data < infectiontime:
                        infectiontime = time_data
                else:
                    infectiontime = time_data
            infectiontimes[name] = infectiontime 
            
    if second_order:
        names2 = names - set(contacts)  # remaining non-infected people    
        contacts2 = []  # contacts from second order
        
        if len(names2)>0:
            for name in contacts:
                # using infectiontimes previously found and 
                # infected_visits() function to re-assign values
                indexvisits = (
                    infected_visits(
                        visits, name, infectiontimes[name], [], []))[1] 
                
                infectedvisits = (
                    infected_visits(
                        visits, name, infectiontimes[name], [], []))[0]
               
                othervisits = othervisits - set(indexvisits)    
                # same process as finding first order            
                for othernames in names2:
                    visit_set = []
                    for visit in othervisits:
                        if othernames == visit[0]:
                            visit_set.append(visit)

                    if (potential_contacts(infectedvisits, visit_set))[0]:
                        contacts2.append(othernames)
                        
            contacts.extend(contacts2) 
    return sorted(set(contacts))  # make sure no duplicates with set()

def infected_visits(visits, index, day_time, infectedvisits, indexvisits):
    """Finds visits of an infected person from when they were infected.
    Also gives a list of all places they have visited. Uses a list of visits,
    name and time of infection"""
    
    for visit in visits:            
        if visit[0] == index:  # if it is the infected person's visit
            indexvisits.append(visit) 
            # if day of visit and infection was same, compare times
            if visit[2] == day_time[0]:                    
                arrival = visit[3] + visit[4] / 100
                leave = visit[5] + visit[6] / 100
                infectedtime = day_time[1] + day_time[2] / 100
            
                # find and add visits where individual was infected during or 
                # before the visit
                if arrival <= infectedtime < leave or infectedtime <= arrival:
                    infectedvisits.append(visit)
                    
            # if day of visit was after infection day, add visit      
            elif visit[2] > day_time[0]:              
                infectedvisits.append(visit)
                
    return infectedvisits, indexvisits

def backward_contact_trace(visits, index, day_time, window):
    """Traces possible sources for an infected individual by checking
    previous visit locations and overlaps with other individuals. Uses
    a list of visits, the name of the infected, time of infection 
    (day, hour, minutes) and a time window to search for"""
    
    indexvisits = []
    backwardcontacts = []
    names = []
    for visit in visits: 
        if visit[0] == index:
            arrival = visit[3] + visit[4] / 100
            infectiontime = day_time[1] + day_time[2] / 100 
            # if infection day was the same as visit day
            if (visit[2] == day_time[0]): 
                #  check they were at location before being infected
                if arrival < infectiontime:  
                    indexvisits.append(visit)
                    
            # otherwise if visit day occured before the infection day
            # and is within the time window to search for
            elif day_time[0] - (window - 1) <= visit[2] < day_time[0]:
                indexvisits.append(visit)
    # visits of all other individuals, besides infectee
    othervisits = set(visits) - set(indexvisits) 
    
    for people in othervisits:
        names.append(people[0]) 
    
    # for each visit of a non-infected, check if it overlaps with the 
    # infectee's visit
    for name in names:
        visit_set = []
        for visit in othervisits: 
            if visit[0] == name:
                visit_set.append(visit)
  
        if (potential_contacts(indexvisits, visit_set))[0]:
            backwardcontacts.append(name)
            
    return sorted(set(backwardcontacts)) 

def potential_contacts(person_a, person_b):
    """Uses a list of 7-tuple visits of two individuals to determine multiple
    potential contacts and the total time of potential contact between the 
    two"""
    
    alloverlaps = []
    visittime = [0, 0]
    overalltime = [0, 0]       
    for a_data in person_a:        
        # testing each visit from person_a to all visits of person_b     
        for b_data in person_b:         
            if contact_event(a_data, b_data):  # if overlapping location, time
                overlap = []                         
                overlap.extend((a_data[1], a_data[2]))  # add location and day
                # arrival and departure times of visits 
                a_arrive = a_data[3] + (a_data[4] / 100)
                a_leave = a_data[5] + (a_data[6] / 100)
                b_arrive = b_data[3] + (b_data[4] / 100)
                b_leave = b_data[5] + (b_data[6] / 100)
                
                # checking which person arrived later, add that time to list
                if max(a_arrive, b_arrive) == a_arrive:
                    overlap.extend((a_data[3], a_data[4]))
                else:
                    overlap.extend((b_data[3], b_data[4]))
                    
                # checking which person left first 
                if min(a_leave, b_leave) == a_leave:
                    overlap.extend((a_data[5], a_data[6]))
                else:
                    overlap.extend((b_data[5], b_data[6]))
                           
                visittime = visit_length(tuple(overlap)) 
                
                for i in range(2):  # adding current visit time to previous
                    overalltime[i] += visittime[i]                   

                alloverlaps.append(tuple(overlap))
                
    return set(alloverlaps), tuple(overalltime)

def contact_event(visit_a, visit_b):
    """Determine's whether two individuals may have had potential contact
    during overlapping visits. Uses two individual's 7-tuple data. Also checks
    for valid visit times"""
    
    # check for valid visits with function visit_length
    if visit_length(visit_a) is None or visit_length(visit_b) is None:
        return None
    
    # Converting arrival and departure times to float numbers e.g 9:30 becomes
    # 9.3, no need to care about only going to 60 minutes
    a_arrive = visit_a[3] + (visit_a[4] / 100)
    a_leave = visit_a[5] + (visit_a[6] / 100)
    b_arrive = visit_b[3] + (visit_b[4] / 100)
    b_leave = visit_b[5] + (visit_b[6] / 100)
    
    # check if time and location match, then check for overlapping visit
    if visit_a[1] == visit_b[1] and visit_a[2] == visit_b[2]:
        if (b_arrive <= a_arrive < b_leave or 
            a_arrive <= b_arrive < a_leave):
            return True        
    return False 
    
def visit_length(visit):
    """Determines individual's visit length at location using the 
    7-tuple data. 7-tuple data is a tuple of the format
    ("Name", "Location", "Integer value of day", hour of entry,
    minute of entry, hour of leave, minute of leave) """ 
    
    # finding the hours and minutes stayed at location
    hours = visit[5] - visit[3]
    minutes = visit[6] - visit[4]
    
    # if the person left the location before reaching the next hour
    if minutes < 0:
        hours -=1
        minutes = 60 + minutes  # +minutes as minutes is a negative integer
    
    # check whether they spent more than 0 minutes at location
    if (hours <= 0 and minutes <= 0) or hours < 0:
        return None
    
    # need to return anything so if statement in contact_event will work
    return 1
   


#for testing of functions

#print(visit_length(('Russel', 'Foodigm', 2, 9, 0, 10, 0)))
#print(contact_event(('Russel', 'Foodigm', 2, 9, 0, 10, 0), ('Natalya', 'Foodigm', 2, 9, 30, 9, 45)))
#potential_contacts([('Russel', 'Foodigm', 2, 9, 0, 10, 0), ('Russel', 'Afforage', 2, 10, 0, 11, 30), ('Russel', 'Nutrity', 2, 11, 45, 12, 0), ('Russel', 'Liberry', 3, 13, 0, 14, 15)], [('Chihiro', 'Foodigm', 2, 9, 15, 9, 30), ('Chihiro', 'Nutrity', 4, 9, 45, 11, 30), ('Chihiro', 'Liberry', 3, 12, 15, 13, 25)])

#for forward_contact_trace and backward_contact_trace
"""visits = [('Russel', 'Nutrity', 1, 5, 0, 6, 0),
           ('Russel', 'Foodigm', 2, 9, 0, 10, 0),
           ('Russel', 'Afforage', 2, 10, 0, 11, 30),
           ('Russel', 'Nutrity', 2, 11, 45, 12, 0),
           ('Russel', 'Liberry', 3, 13, 0, 14, 15),
           ('Natalya', 'Nutrity', 1, 5, 30, 6, 45),
           ('Natalya', 'Afforage', 2, 8, 15, 10, 0),
           ('Natalya', 'Nutrity', 4, 10, 10, 11, 45),
           ('Chihiro', 'Foodigm', 2, 9, 15, 9, 30),
           ('Chihiro', 'Nutrity', 4, 9, 45, 11, 30),
           ('Chihiro', 'Liberry', 3, 12, 15, 13, 25)]

    forward_contact_trace(visits, 'Russel', (1, 9, 0))
    backward_contact_trace(visits, 'Chihiro', (4, 12, 0), 2)"""

