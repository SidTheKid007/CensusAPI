from flask import Flask, render_template, request, url_for
import psycopg2
import os


app = Flask(__name__)


# Load Favicon
@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='image/favicon.ico')


# Endpoint Documentation shown on Introduction
@app.route('/')
def loadHome():
	intro = {"Message": "Welcome to the US Census API made by Sid K! Easily explore various data points collected by the US Government with these Endpoints.", 
		"Endpoints": [
			{"/demographics/<zipCode>": "The raw breakdown on various attributes of homeowners in a given Zip Code based on the 2021 American Community Survey"},
			{"/demographicsPercent/<zipCode>": "The percentage breakdown on various attributes of homeowners in a given Zip Code based on the 2021 American Community Survey"}
		]}
	return (intro)


# Endpoint for retrieving raw Zip Code Homeowner Demographic data
@app.route('/demographics/<zipCode>')
def demographics(zipCode):
	if zipInvalid(zipCode):
		error = {"Message": "That Zip Code '" + str(zipCode) + "' is invalid. Please retry this endpoint with a valid Zip Code (ex. /demographics/91007)"}
		return(error)
	connection = dbConnect()
	zipData = queryZip(zipCode, connection)
	demographics = formatDemographics(zipData)
	connection.close()
	return(demographics)


# Endpoint for retrieving percentaged Zip Code Homeowner Demographic data
@app.route('/demographicsPercent/<zipCode>')
def demographicsPercent(zipCode):
	if zipInvalid(zipCode):
		error = {"Message": "That Zip Code '" + str(zipCode) + "' is invalid. Please retry this endpoint with a valid Zip Code (ex. /demographicsPercent/91007)"}
		return(error)
	connection = dbConnect()
	zipData = queryZip(zipCode, connection)
	demographics = formatDemographicsPct(zipData)
	connection.close()
	return(demographics)


# Endpoint Documentation shown on Incorrectly Entered Endpoint
@app.errorhandler(404)
def not_found(err):
	error = {"Message": "The page you are looking for can't be found! Easily explore various data points collected by the US Government with these Endpoints instead.", 
		"Endpoints": [
			{"/demographics/<zipCode>": "The raw breakdown on various attributes of homeowners in a given Zip Code based on the 2021 American Community Survey"},
			{"/demographicsPercent/<zipCode>": "The percentage breakdown on various attributes of homeowners in a given Zip Code based on the 2021 American Community Survey"}
		]}
	return (error)


# Initial connection to external RDS Database
def dbConnect():
	try:
		connection = psycopg2.connect(
			database = "postgres",
			user = "census",
			password = os.environ['PASSWORD'],
			host = os.environ['HOST'],
			port = 5432
			)
		return(connection)
	except (Exception, psycopg2.DatabaseError) as error:
		print("Error: %s" % error)
		connection.rollback()
		cursor.close()
		errorMsg = {"Message": error}
		return(errorMsg)


def zipInvalid(zipCode):
	if ((len(zipCode) == 5) and (zipCode.isdigit())):
		return(False)
	else:
		return(True)


# Demograpics search on entered ZipCode
def queryZip(zipCode, connection):
	try:
		cursor = connection.cursor()
		cursor.execute("""
			SELECT * 
			FROM demographics d
			WHERE d.Zip_Code = %s;
			""",
			[zipCode,])
		zipData = cursor.fetchone()
		cursor.close()
		return(zipData)
	except (Exception, psycopg2.DatabaseError) as error:
		print("Error: %s" % error)
		connection.rollback()
		cursor.close()
		errorMsg = {"Message": error}
		return(errorMsg)


# Formatting the raw query data
def formatDemographics(zipData):
	try:
		cleanZip = {'Zip Code': zipData[0],
			'Population': zipData[1],
			'Race': {'White': zipData[2],
				'Black or African American': zipData[3],
				'American Indian and Alaska Native': zipData[4],
				'Asian': zipData[5],
				'Native Hawaiian and Other Pacific Islander': zipData[6],
				'Some other race': zipData[7],
				'Two or more races': zipData[8]},
			'Hispanic': {'Hispanic or Latino origin': zipData[9],
				'Not Hispanic or Latino': zipData[10]},
			'Age': {'Under 35 years': zipData[11],
				'35 to 44 years': zipData[12],
				'45 to 54 years': zipData[13],
				'55 to 64 years': zipData[14],
				'65 to 74 years': zipData[15],
				'75 to 84 years': zipData[16],
				'85 years and over': zipData[17]},
			'Education': {'Less than high school graduate': zipData[18],
				'High school graduate': zipData[19],
				'Some college': zipData[20],
				"Bachelor's degree or higher": zipData[21]}}
		return(cleanZip)
	except:
		errorMsg = {"Message": "Error"}
		return(errorMsg)


# Formatting the raw query data into percentages
def formatDemographicsPct(zipData):
	try:
		zipPercent = list(zipData[1:])
		zipPercent[:] = [round(100*x/zipPercent[0],2) for x in zipPercent]
		zipPercent = [zipData[0]] + zipPercent
		cleanZip = {'Zip Code': zipPercent[0],
			'Population': zipPercent[1],
			'Race': {'White': zipPercent[2],
				'Black or African American': zipPercent[3],
				'American Indian and Alaska Native': zipPercent[4],
				'Asian': zipPercent[5],
				'Native Hawaiian and Other Pacific Islander': zipPercent[6],
				'Some other race': zipPercent[7],
				'Two or more races': zipPercent[8]},
			'Hispanic': {'Hispanic or Latino origin': zipPercent[9],
				'Not Hispanic or Latino': zipPercent[10]},
			'Age': {'Under 35 years': zipPercent[11],
				'35 to 44 years': zipPercent[12],
				'45 to 54 years': zipPercent[13],
				'55 to 64 years': zipPercent[14],
				'65 to 74 years': zipPercent[15],
				'75 to 84 years': zipPercent[16],
				'85 years and over': zipPercent[17]},
			'Education': {'Less than high school graduate': zipPercent[18],
				'High school graduate': zipPercent[19],
				'Some college': zipPercent[20],
				"Bachelor's degree or higher": zipPercent[21]}}
		return(cleanZip)
	except:
		errorMsg = {"Message": "Error"}
		return(errorMsg)

	
