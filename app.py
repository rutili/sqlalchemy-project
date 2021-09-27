from flask import Flask, render_template, redirect, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

engine = create_engine("sqlite:///resources/hawaii.sqlite?check_same_thread=False")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the API<br/>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>" 
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route('/api/v1.0/precipitation')
def preciptation():
    res = session.query(Measurement.date,Measurement.prcp).all()
    return {date:val for date,val in res}

@app.route('/api/v1.0/stations')
def stations():
    res = session.query(Station.station, Station.name).all()
    return {id:loc for id,loc in res }
    
@app.route('/api/v1.0/tobs')
def tobs():
    mrd = session.query(func.max(Measurement.date)).first()[0]

    oyp = dt.datetime.strptime(mrd, '%Y-%m-%d') - dt.timedelta(days=365)

    mas = session.query(func.count(Measurement.tobs), 
                    Measurement.station).group_by(Measurement.station)\
                    .order_by(func.count(Measurement.tobs).desc()).first()[1]
                
    res = session.query(Measurement.date, Measurement.tobs)\
        .filter((Measurement.date > oyp)&(Measurement.station==mas)).all()
    return {date:temp for date,temp in res }

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def vacation(start, end='2017-08-23'):
    res = session.query(func.min(Measurement.tobs),
    func.avg(Measurement.tobs),
    func.max(Measurement.tobs)).filter((Measurement.date > start)&(Measurement.date<end)).all()
    
    mnt = res[0][0]
    mxt = res[0][1]
    avgt = round(res[0][2],2)
    session.close()
    return (
        f'Summary temperature from {start} - {end}<br/>'
        f'minimum temperature: {mnt}<br/>'
        f'maximum temperature: {mxt}<br/>'
        f'average temperature: {avgt}'
    )
    
if __name__ == "__main__":
    app.run(debug = True)