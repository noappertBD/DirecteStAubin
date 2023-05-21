from sqlobject import sqlhub, connectionForURI, SQLObject, StringCol, IntCol, DateTimeCol, ForeignKey, sqlbuilder
import os

db_filename = os.path.abspath('data.db')
connection_string = f'sqlite:{db_filename}'
sqlhub.processConnection = connectionForURI(connection_string)


class Users(SQLObject):
    discriminentId = StringCol()
    firstName = StringCol()
    lastName = StringCol()
    classLevel = StringCol()

    def toDict(self):
        return {"id": self.id, "discriminentId": self.discriminentId, "firstName": self.firstName, "lastName": self.lastName, "classLevel": self.classLevel}


Users.createTable(ifNotExists=True)
