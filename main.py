
# main.py
# <Ivan Deng>
# 
# University of Illinois at Chicago
# CS 341: Spring 2022
# Project #1 : Analyzing CTA2 L data in Python

import sqlite3
import matplotlib.pyplot as figure


###########################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General stats:")
    
    dbCursor.execute("Select count(*) From Stations;")
    StationsRow = dbCursor.fetchone();
    print("  # of stations:", f"{StationsRow[0]:,}")

    # Count all the stops on the Stops table
    dbCursor.execute("Select count(*) From Stops;")
    StopsRow = dbCursor.fetchone();
    print("  # of stops:", f"{StopsRow[0]}")


    # Extract the number of stops, last date of table, first date of table, total number of riders
    dbCursor.execute("Select count(Station_ID), max(date(Ride_Date)), min(date(Ride_Date)), sum(Num_Riders) from ridership;")
    RidershipRow = dbCursor.fetchall();
    print("  # of ride entries:", f"{RidershipRow[0][0]:,}")
    print("  date range:", RidershipRow[0][2], "-" , RidershipRow[0][1])
    print("  Total ridership:",  f"{RidershipRow[0][3]:,}")

    # Extract total of riders where type of day is on a weekday
    dbCursor.execute("Select sum(Num_Riders) from ridership where Type_of_Day = 'W' ; ")
    WRidershipRow = dbCursor.fetchone();
    weekday = WRidershipRow[0] / RidershipRow[0][3] * 100
    print("  Weekday ridership:", f"{WRidershipRow[0]:,}", f'({weekday:.2f}%)')

    # Extract total of riders where type of day is on a saturday
    dbCursor.execute("Select sum(Num_Riders) from ridership where Type_of_Day = 'A' ; ")
    ARidershipRow = dbCursor.fetchone();
    saturday = ARidershipRow[0] / RidershipRow[0][3] * 100
    print("  Saturday ridership:", f"{ARidershipRow[0]:,}", f'({saturday:.2f}%)')

    # Extract total of riders where type of day is on a sunday
    dbCursor.execute("Select sum(Num_Riders) from ridership where Type_of_Day = 'U' ; ")
    URidershipRow = dbCursor.fetchone();
    sunday = URidershipRow[0] / RidershipRow[0][3] * 100
    print("  Sunday/holiday ridership:", f"{URidershipRow[0]:,}", f'({sunday:.2f}%)')


# Command 1 where retrieve the stations name and output in ascending order. If none is found, 
# output *No stations found...'
def search_station(dbConn, name):
    dbCursor = dbConn.cursor()
    sql = """Select Station_ID, Station_Name from stations 
             where Station_name like ? order by Station_name asc;""" 
    dbCursor.execute(sql, [name] )
    StationName = dbCursor.fetchall()
    #check if the row is empty
    if len(StationName) == 0 : #if the row is empty, this mean it mean sql didn't found any station
      print('**No stations found...')
    else :
      for row in StationName:
        print (row[0], ":", row[1])

# Command 2 where to output the ridership for every station by ascending order in terms of name. # Along with the ridership data, output this value compare to the total ridership.
def output_ridership(dbConn, ridership):
  dbCursor = dbConn.cursor()
  sql = """Select Station_Name, sum(Num_Riders)
           from ridership
           join stations 
           on Stations.Station_ID = ridership.Station_ID
           group by Stations.Station_ID
           order by Station_Name asc;"""
  dbCursor.execute(sql)
  StationRiders = dbCursor.fetchall()
  for row in StationRiders:
    percentage = row[1] / ridership[0] * 100
    print(row[0], ":", f"{row[1]:,}", f"({percentage:.2f}%)")


# Command 3 and 4 where to output the top 10 busiest or least busiest stations # in the L in terms of number of riders. The total ridership is feed in to make # computing percentage easier.
# If the flag is 0, it will run the most busiest sql. If it 1, it will run the least busiest sql
def output_busiest(dbConn, ridership, flag) :
  dbCursor = dbConn.cursor()
  sql = """Select Station_Name, sum(Num_Riders)
           from ridership
           join stations 
           on Stations.Station_ID = ridership.Station_ID
           group by Stations.Station_ID
           order by sum(Num_Riders) desc
           limit 10;"""

  sql2 = """Select Station_Name, sum(Num_Riders)
           from ridership
           join stations 
           on Stations.Station_ID = ridership.Station_ID
           group by Stations.Station_ID
           order by sum(Num_Riders) asc
           limit 10;"""
  if flag == 0 :
    dbCursor.execute(sql)
  else :
    dbCursor.execute(sql2)
  BusiestStations = dbCursor.fetchall()
  for row in BusiestStations:
    percentage = row[1] / ridership[0] * 100
    print(row[0], ":", f"{row[1]:,}", f"({percentage:.2f}%)")


# Command 5 to output all the stops from user input line color. The function, take in dbconn and user input of "color". 
def line_color(dbConn, color):
  dbCursor = dbConn.cursor()
  sql = """select Stop_Name, Direction, ADA
           from stops 
           join StopDetails
           on Stops.Stop_ID = StopDetails.Stop_ID
           join Lines
           on StopDetails.Line_ID = Lines.Line_ID
           where Color like ?
           order by Stop_Name asc"""
  dbCursor.execute(sql, [color])
  line = dbCursor.fetchall();
  if len(line) == 0 :
      print('**No such line...')
  else :
    for row in line:
      print(row[0], ": direction =", row[1], "(accessible? ", end = '')
      # To check for accessible, we check ADA column where 1 represent yes and 0 represent no. 
      if row[2] == 1:  
        print ('yes)')
      else :
        print('no)')


# Command 6 where to output total ridership by month in 
# ascending order. The 
# function also put month and ridership into a array to 
# make graphing easier. 
def monthly_ridership(dbConn, x, y):
  dbCursor = dbConn.cursor()
  sql = """select strftime('%m',Ride_Date) as month, sum(Num_riders)
           from Ridership
           group by month
           order by month asc;"""
  dbCursor.execute(sql)
  monthly = dbCursor.fetchall()
  for row in monthly:
    x.append(row[0])
    y.append(row[1])
    print(row[0], ':' , f"{row[1]:,}")

# Command 7 output the total ridership by year in ascending order. 
# Afterwards, the program allow the user to plot this graph.
def yearly_ridership(dbConn, x, y):
  dbCursor = dbConn.cursor()
  sql = """select strftime('%Y',Ride_Date) as year, sum(Num_riders)
           from Ridership
           group by year
           order by year asc;"""
  dbCursor.execute(sql)
  yearly = dbCursor.fetchall()
  for row in yearly :
    x.append(row[0])
    y.append(row[1])
    print(row[0], ':' , f"{row[1]:,}")

# Command 8 where to compare the daily ridership between two stations. 
# The function only output the first and last days of the data.
# At the end, if the user enter y, it will graph the two statiosn data. 
def compare_two(dbConn, year, station, x, y):
  dbCursor = dbConn.cursor()
  sql = "Select Station_ID, Station_Name from stations where Station_name like ? "
  dbCursor.execute(sql, [station])
  station1 = dbCursor.fetchall()
  if (len(station1) == 0) :
    print('**No station found...')
  elif (len(station1) > 1) :
    print('**Multiple stations found...\n')
  else :
    sql = """Select date(Ride_date), Num_Riders
             from ridership
             join stations 
             on Stations.Station_ID = ridership.Station_ID
             where Station_name like ?  and strftime('%Y',Ride_Date) = ?
             order by date(Ride_date) asc;"""
    dbCursor.execute(sql, [station, year])
    station_data = dbCursor.fetchall()
    counter = 0
    for row in station_data: 
      x.append(counter)
      y.append(row[1])
      counter += 1
    
    # Return the station name and station id from the search
    return [station1[0][0], station1[0][1]]


#Command 9 where to output all station name and coordinate from a giver user line color. 
# Then, the program ask the user if they want to plot the graph on a chicago map/
def station_line(dbConn,color, x, y, stop) :
  dbCursor = dbConn.cursor() 

  # I use a inner select statement to get the station name from the given station_id from stop table.
  sql = """select distinct Latitude, Longitude, 
          (select Station_name 
          from Stations where
          Station_ID = Stops.Station_ID) as name
          from stops
          join StopDetails
          on Stops.Stop_ID = StopDetails.Stop_ID
          join Lines
          on StopDetails.Line_ID = Lines.Line_ID
          where Color like ?
          order by name asc;"""

  dbCursor.execute(sql, [color])
  station_location = dbCursor.fetchall()
  if len(station_location) == 0 :
      print('**No such line...\n')
  else:
    for row in station_location: 
        x.append(row[1])
        y.append(row[0])
        stop.append(row[2])
        print(f"{row[2]} : ({row[0]}, {row[1]})")
    


###########################################################  
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)
print()
print("1:Retrieve the stations name and output")
print("2:Output the ridership for every station")
print("3:Output the top 10 busiest station")
print("4:Output the top 10 least station")
print("5:Output all the stops from select train color")
print("6:Output total ridership by month")
print("7:Output the total ridership by year")
print("8:Compare the daily ridership between two stations")
print("9:Output all station name and coordinate from a select train color")
print()
username = input("Please enter a command (1-9, x to exit): ")

dbCursor = dbConn.cursor()
# Retrieve the total ridership for the percentage 
dbCursor.execute("select sum(Num_Riders) from ridership;") 
ridership = dbCursor.fetchone();


# while loop to continue until the user enter x
while username != 'x' :
  
  if username == '1' : # Search station
    print()
    name = input("Enter partial station name (wildcards _ and %): ")
    search_station(dbConn, name)
    print()
  
  elif username == '2' : # Output ridership at every station
    print('** ridership all stations **')
    output_ridership(dbConn, ridership)
    print()

  elif username == '3' : # Output top 10 busiest stations
    print('** top-10 stations **')
    output_busiest(dbConn, ridership, 0)
    print()

  elif username == '4' : # Output top 10 least busiest stations 
    print('** least-10 stations **')
    output_busiest(dbConn, ridership, 1)
    print()

  elif username == '5' : # Output every stops at a line
    print()
    color = input("Enter a line color (e.g. Red or Yellow): ")
    line_color(dbConn, color)
    print()

  elif username == '6' : # Outputs total ridership by month,
    x = []
    y = []
    print('** ridership by month **')
    monthly_ridership(dbConn,x,y)
    print()
    plot = input("Plot? (y/n) ")
    if plot == "y" :
      figure.xlabel("month")
      figure.ylabel("number of ridership")
      figure.title("monthly ridership")
      figure.plot(x, y)
      figure.show()

    print()

  elif username == '7' : # Outputs total ridership by year
    x = []
    y = []
    print('** ridership by year **')
    yearly_ridership(dbConn, x, y)
    print()
    plot = input("Plot? (y/n) ")
    if plot == "y" :
      figure.xlabel("year")
      figure.ylabel("number of ridership")
      figure.title("yearly ridership")
      figure.plot(x, y)
      figure.show()
    print()

  elif username == '8' : # Compare two stations ridership
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    year = input("\nYear to compare against? ")
    station1 = input("\nEnter station 1 (wildcards _ and %): ")
    first_station = compare_two(dbConn, year, station1, x1, y1)

    if x1 :
      station2 = input("\nEnter station 2 (wildcards _ and %): ")
      second_station = compare_two(dbConn, year, station2, x2, y2)

    # check if the array is empty
    # if the array is empty, sql didn't find any stations from our search
    if x1 and x2 :
      
      # Get the last five ridership data
      length_first = len(y1) - 5
      length_second = len(y2) - 5
      print("Station 1:", first_station[0],first_station[1])
      for i in range(0,5):
        date = str(year) + "-01-0" + str(i + 1)
        print(date, y1[i])

      for i in range(27,32):
        date = str(year) + "-12-" + str(i)
        print(date, y1[length_first])
        length_first += 1    

      print("Station 2:", second_station[0],second_station[1])
      for i in range(0,5):
        date = str(year) + "-01-0" + str(i + 1)
        print(date, y2[i])

      for i in range(27,32):
        date = str(year) + "-12-" + str(i)
        print(date, y2[length_second])
        length_second += 1          

      plot = input("\nPlot? (y/n) ")
      if plot == "y" :
        figure.xlabel("day")
        figure.ylabel("number of ridership")
        title = "riders each day of " + year
        figure.title(title)
        figure.plot(x1, y1)
        figure.plot(x2, y2)
        figure.show()
    print()

  elif username == '9' : # Output all station name on a line
    x = []
    y = []
    stop = []
    color = input("\nEnter a line color (e.g. Red or Yellow): ")
    flag = station_line(dbConn,color, x, y, stop)
    if x :
      plot = input("\nPlot? (y/n) ")
      if plot == "y":
        image = figure.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
        figure.imshow(image, extent=xydims)
        figure.title(color + " line")
        figure.plot(x, y, "o", c=color)
    
        if (color.lower() == "purple-express"):
          color="Purple" 

        counter = 0
        for row in stop:
          figure.annotate(row, (x[counter], y[counter]))
          counter += 1
        
        figure.plot(x, y, "o", c=color)
        figure.xlim([-87.9277, -87.5569])
        figure.ylim([41.7012, 42.0868])
        figure.show()
    print()


  else :
    print('**Error, unknown command, try again...\n')


  username = input("Please enter a command (1-9, x to exit): ")

#
# done
#