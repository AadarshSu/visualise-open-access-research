# visualise-open-access-research
 
How to run:

BACKEND :-
cd flask-backend
pip3 install -r requirements.txt
python3 server.py

FRONTEND :-
cd react-frontend
npm install
npm start

UPDATE DATABASE :- 
Download latest ROR (Research Organization Registry) data dump CSV from: https://doi.org/10.5281/zenodo.7926988
Move the CSV file into the flask-backend directory and name it "institution-data-ror.csv"
Run csv_to_sql.py in the flask-backend directory: python3 csv_to_sql.py