import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Homework/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our link from this script to Hawaii
session = Session(engine)

#################################################
# Flask Setup
#################################################
myApp = Flask(__name__)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# HOME ROUTE
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@myApp.route("/")
def welcome():
    return (
        f"This is my homework assignment.<br/>"
        f"Precipitation Data:<br/>"
        f"\t/api/v1.0/precipitation<br/><br/>"
        f"Station Data' from:<br/>"
        f"\t/api/v1.0/stations<br/><br/>"
        f"Temperature Data:<br/>"
        f"\t/api/v1.0/tobs<br/><br/>"
        f"Enter a date for more inforation (e.g. /api/v1.0/2014-04-24):<br/>"
        f"\t/api/v1.0/<start><br/><br/>"
        f"Or enter a date range (e.g. /api/v1.0/2011-01-01/2012-12-12):<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@myApp.route("/api/v1.0/precipitation")
def precipitation():
    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    final = dt.datetime.strptime(latest[0], '%Y-%m-%d')
    last12= final - dt.timedelta(days = 365)

    date_prec = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date.desc()).filter(Measurement.date > last12).\
            filter(Measurement.prcp != None).all()

    d = {key: value for (key, value) in date_prec}

    return jsonify(d)

@myApp.route("/api/v1.0/stations")
def stations():
    station_count = session.query(Station.station, Station.name).distinct(Station.station).all()
    d2 = {key: value for (key, value) in station_count}
    return jsonify(d2)

@myApp.route("/api/v1.0/tobs")
def temp():
    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    final = dt.datetime.strptime(latest[0], '%Y-%m-%d')
    last12= final - dt.timedelta(days = 365)

    date_tobs = session.query(Measurement.date, Measurement.tobs).\
        order_by(Measurement.date.desc()).\
    filter(Measurement.date > last12).filter(Measurement.tobs != None).all()

    d3 = {key: value for (key, value) in date_tobs}
    return jsonify(d3)

@myApp.route("/api/v1.0/<start>")
def start(start):
    st_date = dt.datetime.strptime(start, '%Y-%m-%d')

    min_max = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), \
        func.avg(Measurement.tobs)).filter(Measurement.date >= st_date).all()
    print(min_max)
    d4 = {"min": min_max[0][0], "max": min_max[0][1], "avg": min_max[0][2]} 

    return jsonify(d4)

@myApp.route("/api/v1.0/<start>/<end>")
def range(start, end):
    st_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    st_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), \
        func.avg(Measurement.tobs)).filter(Measurement.date >= st_date).\
            filter (Measurement.date <= end_date).first()
    print(st_end)
    d5 = {"min": st_end[0], "max": st_end[1], "avg": st_end[2]} 

    return jsonify(d5)

if __name__ == '__main__':
    myApp.run(debug=False)