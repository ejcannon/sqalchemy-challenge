# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    mostrecent = session.query(func.max(Measurement.date)).first()
    mostrecentdate = dt.datetime.strptime(mostrecent[0], "%Y-%m-%d")
    oneyearago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    scores = session.query(Measurement.date, Measurement.prcp).filter(
    Measurement.date >= oneyearago,
    Measurement.date <= mostrecentdate
    )
    results = scores.all()
    all_scores = {}
    for date, prcp in results:
        all_scores[date] = prcp
        
    return jsonify(all_scores)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    stations = session.query(Station.station).all()
    
    return jsonify(stations)
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    stationcount = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    mostactive = stationcount[0][0]
    oneyearago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    mostactivestats = session.query(Measurement.station, Measurement.tobs).filter(Measurement.station 
    ==mostactive).all()
    yearmostactive = session.query(Measurement.date, Measurement.tobs).filter(
    Measurement.date >= oneyearago,
    Measurement.station == mostactive
    )
    results = yearmostactive.all()
    activestats = {}
    for station, tobs in results:
        activestats[station] = tobs
        
    return jsonify(activestats)

@app.route("/api/v1.0/<start><br>")
def start(start = None, end = None):

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]


    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel) \
                     .filter(Measurement.date >= start) \
                     .all()
        session.close()
        temps = list(np.ravel(results))
        return(jsonify(temps))  
@app.route("/api/v1.0/<start>/<end>")    
def startend(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if start and end:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        end_date = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*sel) \
            .filter(Measurement.date >= start_date) \
            .filter(Measurement.date <= end_date) \
            .all()

        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps)
if __name__ == '__main__':
    app.run(debug=True)
