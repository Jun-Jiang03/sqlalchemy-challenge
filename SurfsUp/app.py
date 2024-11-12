# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#
@app.route("/")
def welcome():
    #List all available api routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

@app.route("/api/v1.0/precipitation")
        #precipitation route

def precipitation():
    session = Session(engine)

    one_year_ealier =dt.date(2017,8,23)-dt.timedelta(days=365)

    results= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ealier)\
        .order_by(Measurement.date.desc()).all()

    session.close()

 # Create a dictionary from the row data and append to a list of all_prcp
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

#station route
@app.route("/api/v1.0/stations")
def stations():
    # Create the session
    session = Session(engine)

    # Query station data from the Station dataset
    station_data = session.query(Station.station).all()

    # Close the session                   
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_data))

    # Return a list of jsonified station data
    return jsonify(station_list)

# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session
    session = Session(engine)
    one_year_ealier =dt.date(2017,8,23)-dt.timedelta(days=365)

    # Query tobs data from last 12 months from the most recent date from Measurement table
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= one_year_ealier).all()

    # Close the session                   
    session.close()

    # Create a dictionary from the row data and append to a list of tobs_list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(tobs_list)

# start route 
@app.route('/api/v1.0/<start>', methods=['GET'])
# Define what to do when the user specifies start date or start-end range
@app.route("/api/v1.0/<start>/<end>")
def cal_temp(start=None, end=None):
    # Create the session
    session = Session(engine)
    
    # Make a list to query (the minimum, average and maximum temperature)
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Check if there is an end date then do the task accordingly
    if end == None: 
        # Query the data from start date to the most recent date
        start_data = session.query(*sel).filter(Measurement.date >= start).all()
        # Convert list of tuples into normal list
        start = list(np.ravel(start_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start date
        return jsonify(start)
    else:
        # Query the data from start date to the end date
        start_end_data = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        # Convert list of tuples into normal list
        start_end_list = list(np.ravel(start_end_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start-end date range
        return jsonify(start_end_list)

    # Close the session                   
    session.close()


if __name__ == '__main__':

    app.run(debug=True)

