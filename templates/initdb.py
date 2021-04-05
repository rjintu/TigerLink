from server.database import Database
db = Database()
db.connect()
db.init()
db.disconnect()
