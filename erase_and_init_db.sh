rm -rf migrations/
rm -rf app.db
flask db init
flask db stamp head
flask db migrate -m "Initial migration"
flask db upgrade
