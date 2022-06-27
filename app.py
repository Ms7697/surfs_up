"""
Main module of the weather server app
"""


__version__ = "0.1.0"


from datetime import date, timedelta
import connexion
from flask import jsonify
from flask.templating import render_template
from sqlalchemy import func
import numpy as np
# Having these separate Python files is good because you can use the same model to query or load data outside of an app.
from models import Measurement, Station
from database import db_session, init_db

#### CONNEXTION FUNCTIONS ###
### https://connexion.readthedocs.io/en/latest/
# Its basically OpenAPI!
def precipitation():
    precipitation = Measurement.query.all()
    return jsonify([precipitation.to_dict() for record in precipitation])


# Create the connexion application instance
connex_app = connexion.FlaskApp(__name__)
# Read the openapi.yaml file to configure the endpoints
connex_app.add_api("openapi.yaml")


# Create a URL route in our application for "/"
@connex_app.route("/")
def index():
    """
    This function just responds to the browser URL
    localhost:5000/
    :return:        the rendered template "index.html"
    """
    return render_template("index.html")


@connex_app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = date(2017, 8, 23) - timedelta(days=365)
    precipitation = (
        db_session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= prev_year)
        .all()
    )
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@connex_app.route("/api/v1.0/stations")
def stations():
    # return('Show stations')
    results = db_session.query(Station.station).all()
    stations = list(np.ravel(results))
    # return jsonify(stations)
    return jsonify(stations=stations)


@connex_app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = date(2017, 8, 23) - timedelta(days=365)
    results = (
        db_session.query(Measurement.tobs)
        .filter(Measurement.station == "USC00519281")
        .filter(Measurement.date >= prev_year)
        .all()
    )
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


@connex_app.route("/api/v1.0/temp/<start>")
@connex_app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
    ]

    if not end:
        results = db_session.query(*sel).filter(Measurement.date <= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = (
        db_session.query(*sel)
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == "__main__":
    init_db()
    connex_app.run(debug=True)