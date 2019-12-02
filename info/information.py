import asyncio
import websockets
import json
import utils
import pymysql

# Port used by this module to listen for messages
LISTENING_PORT = 5003

# Called when the info module receives a message from the main module
async def onReception(ws, head, body):
    print("[MAIN > INFO]", head)

    if head == "init-db":
        db = connectToDB()
        addDataToDB(db)
        db.close()
        await utils.wsSend(ws, "db-ready")
    if head == "get-info":
        itemsInfo = getInfo(body)
        await utils.wsSend(ws, "info", itemsInfo)

def connectToDB():
    return pymysql.connect(
        host="infodb",
        user="root",
        password="Jamaica1"
    )

def addDataToDB(db):
    mycursor = db.cursor()
    mycursor.execute("DROP DATABASE IF EXISTS information;")
    mycursor.execute("CREATE DATABASE information;")
    mycursor.execute("USE information;")
    mycursor.execute("CREATE TABLE info (ID INT, Name VARCHAR(100), Price VARCHAR(20), Energy VARCHAR(10), Proteins VARCHAR(4), Carbohydrates VARCHAR(4), Fats VARCHAR(4));")
    #mycursor.execute("INSERT INTO info (id, name, price, energy, proteins, carbohydrates, fats) VALUES(4,'bobo',0.5,80,1,17,1);")
    #mycursor.execute("INSERT INTO info (ID, Name, Price €, Energy kcal/100g, Proteins g/100g, Carbohydrates g/100g, Fats g/100g) VALUES (6,'hola',0.5,80,1,17,1),(7,'buenas',0.5,80,1,17,1);")
    #mycursor.execute("""INSERT INTO info (ID, Name, Price, Energy, Proteins, Carbohydrates, Fats) VALUES (6,'hola',0.5,80,1,17,1),(7,'buenas',0.5,80,1,17,1);""")
    mycursor.execute("""INSERT INTO info (ID, Name, Price, Energy, Proteins, Carbohydrates, Fats) VALUES (1,'Agneau ', 1.5, 255, 19, 20, 1),
    (2,'Boeuf', 2, 165, 19, 10, 1),
    (3,'Cheval', 2, 110, 22, 2, 1),
    (4,'Mouton', 1.6, 170, 17, 11, 1),
    (5,'Porc gras', 1.4, 330, 14, 30, 1),
    (6,'Porc maigre', 1.7, 170, 19, 10, 1),
    (7,'Veau', 2.2, 175, 18, 11, 1),
    (8,'Chevreuil', 2, 95, 20, 2, 1),
    (9,'Lapin', 1, 175, 22, 7, 1),
    (10,'Poulet', 3, 150, 21, 7, 0),
    (11,'Cervelle', 1, 120, 10, 9, 1),
    (12,'Langue', 1, 200, 15, 15, 1),
    (13,'Rillettes', 1, 600, 22, 58, 1),
    (14,'Saucisse porc', 3, 420, 15, 44, 1),
    (15,'Saucisson sec ', 3, 500, 26, 55, 0),
    (16,'Triperie', 4, 140, 20, 5, 5),
    (17,'Lard', 4, 780, 4, 88, 0),
    (18,'Saindoux', 5, 850, 1, 94, 0),
    (19,'Brochet', 1, 80, 19, 1, 0),
    (20,'Cabillaud', 2, 63, 15, 1, 1),
    (21,'Caviar', 3, 310, 32, 20, 7),
    (22,'Hareng maquereau', 4, 135, 19, 7, 1),
    (23,'Moules', 5, 76, 10, 4, 5),
    (24,'Limande', 5, 73, 16, 1, 1),
    (25,'Merlan', 2, 69, 16, 1, 1),
    (26,'Sardine', 3, 107, 21, 2, 1),
    (27,'Saumon frais', 5, 200, 21, 12, 1),
    (28,'Thon frais', 6, 225, 27, 13, 1),
    (29,'Thon en conserve', 3, 217, 28, 12, 1),
    (30,'Truite', 2, 95, 19, 2, 0),
    (31,'Camembert', 4, 306, 20, 27, 1),
    (32,'Chevre frais', 1, 330, 33, 17, 14),
    (33,'Creme fraiche', 2, 255, 4, 28, 4),
    (34,'Emmenthal', 3, 330, 30, 34, 1),
    (35,'Fromage blanc 0%', 1, 40, 8, 0, 3),
    (36,'Fromage blanc 20%', 2, 70, 8, 4, 3),
    (37,'Fromage blanc 40%', 3, 110, 8, 8, 3),
    (38,'Lait de vache ecreme', 1, 36, 4, 1, 5),
    (39,'Lait de vache entier', 2, 67, 4, 4, 5),
    (40,'Oeuf entier', 1, 160, 13, 12, 1),
    (41,'Blanc oeuf', 2, 48, 11, 0, 1),
    (42,'jaune oeuf', 1, 355, 16, 32, 1),
    (43,'Roquefort', 1, 320, 25, 36, 2),
    (44,'Yaourt', 2, 10, 5, 6, 2),
    (45,'Biscottes', 2, 360, 12, 5, 80),
    (46,'Biscuit sec', 1, 410, 11, 9, 73),
    (47,'Blé', 2, 371, 27, 9, 53),
    (48,'Farine', 3, 347, 13, 3, 83),
    (49,'Flocons avoine', 1, 400, 14, 7, 70),
    (50,'Mais', 2, 353, 9, 5, 70);""")
    mycursor.close()
    db.commit()

# Get data for the given items
def getInfo(items):
    db = connectToDB()

    mycursor = db.cursor()
    mycursor.execute("USE information;")

    results = {}

    for i in items:
        mycursor.execute("""SELECT ID, Name, Price, Energy, Proteins, Carbohydrates, Fats FROM info WHERE name = %s""", (i,))
        d = mycursor.fetchone()
        results[i] = {
            "id": d[0],
            "name": d[1],
            "price": d[2],
            "energy": d[3],
            "proteins": d[4],
            "carbohydrates": d[5],
            "fats": d[6],
        }

    db.commit()
    mycursor.close()
    db.close()
    return results

utils.startWsServer(LISTENING_PORT, onReception)
asyncio.get_event_loop().run_forever()
