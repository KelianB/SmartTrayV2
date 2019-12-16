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
        await utils.wsSend(ws, "items-info", itemsInfo)

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
    mycursor.execute("CREATE TABLE info (ID INT, Name VARCHAR(100), Price VARCHAR(20), Energy VARCHAR(20), Proteins VARCHAR(20), Carbohydrates VARCHAR(20), Fats VARCHAR(20));")

    # Energy: kcal/100g, Proteins: g/100g, Carbohydrates: g/100g, Fats: g/100g

    mycursor.execute("""INSERT INTO info (ID, Name, Price, Energy, Proteins, Carbohydrates, Fats) VALUES
        (1,'person', 'priceless', 'fun', 'cool', 'awesome', 'lovely'),
        (2,'bicycle', 150, 'wheels', 'handlebars', 'seat', 'brakes'),
        (3,'car', 30000, 'wheels' , 'doors', 'seats', 'lights'),
        (4,'motorcycle', 5000, 'wheels', 'handlebars', 'seat', 'lights'),
        (5,'airplane', 64100000, 'wheels', 'windows', 'wings', 'motors'),
        (6,'bus', 60000, 'wheels', 'windows', 'seats', 'lights'),
        (7,'train', 20000000, 'windows', 'seats', 'doors', 'lights'),
        (8,'truck', 40000, 'wheels', 'seat', 'steering wheel', 'lights'),
        (9,'boat', 50000, 'design', 'seats', 'steering wheel', 'lifesaver'),
        (10,'traffic light', 5000, 'Stop', 'Yellow', 'green', 'Go'),
        (11,'fire hydrant', 200, 'Red', 'water', 'source', 'lifesaver'),
        (12,'stop sign', 50, 'Red', 'Stop', 'Think', 'Act' ),
        (13,'parking meter', 300, 'park', 'your', 'car' , 'here'),
        (14,'bench', 150, 'Take', 'a', 'break', 'here'),
        (15,'bird', 'priceless', 'Free', 'flying', 'two-legged', 'animal'),
        (16,'cat ', 'priceless', 'Adopt', 'do', 'not', 'buy'),
        (17,'dog', 'priceless', 'Adopt', 'do' , 'not' , 'buy'),
        (18,'horse', '4/100g', 'Coolest', 'mammal', 'animal', 'ever'),
        (19,'sheep', '2/100g', 175, 18, 11, 1),
        (20,'cow', '3/100g', 165, 19, 10, 1),
        (21,'elephant', 'priceless', 'Sweetest', 'giant', 'animal', 'ever'),
        (22,'bear', 'priceless', 'Cutest', 'salmon', 'eater', 'ever'),
        (23,'zebra', 'priceless', 'It s', 'a', 'horse', 'in pijamas'),
        (24,'giraffe', 'priceless', 'Coolest', 'long', 'necked', 'animal'),
        (25,'backpack', 100, 'indispensable', 'accesory', 'at', 'school'),
        (26,'umbrella', 15, 'indispensable', 'accesory', 'for', 'autumn/winter'),
        (27,'handbag', 50, 'cool', 'everyday', 'accesory', 'for men/women'),
        (28,'tie', 50, 'Elegant', 'accesory', 'for' , 'special days'),
        (29,'suitcase', 200, 'Best', 'accesory', 'for' , 'travelling'),
        (30,'frisbee', 10, 'Ultimate', 'is' , 'so' , 'cool'),
        (31,'skis', 280, 'Perfect', 'for' , 'winter' , 'Holidays'),
        (32,'snowboard', 300, 'Great', 'for' , 'winter' , 'Holidays'),
        (33,'sports ball', 40, 'Sports' , 'are', 'the', 'best'),
        (34,'kite', 3, 'Great', 'for' , 'august', 'winds'),
        (35,'baseball bat', 40, 'Metallic', 'or' , 'wooden', 'material'),
        (36,'baseball glove', 25, 'Leather', 'or', 'synthethic', 'made'),
        (37,'skateboard', 60, 'wheels', 360, 'degree', 'turn'),
        (38,'surfboard', 150, 'Great', 'for' , 'big', 'sea waves'),
        (39,'tennis racket', 80, 'Tennis', 'is' , 'the best', 'sport ever'),
        (40,'Bottle', 0.80, 'Keep' , 'yourself' , 'hydrated', 'Please'),
        (41,'wine glass', 4.5, 125, 0, 38, 0),
        (42,'cup', 3, 'best', 'gift', 'ever', '!'),
        (43,'fork', 1, 'this', 'is', 'a', 'fork'),
        (44,'knife', 1, 'this', 'is', 'a', 'knife'),
        (45,'spoon', 1, 'this', 'is', 'a', 'spoon'),
        (46,'bowl', 2, 0, 0, 0, 0),
        (47,'banana', 0.5, 89, 1, 23, 0),
        (48,'apple', 0.5, 104, 1, 28, 0),
        (49,'sandwich', 3.5, 361, 19, 32.5, 16),
        (50,'orange', 0.5, 60, 1, 14, 0),
        (51,'broccoli', 2, 31, 2.5 ,6 ,0),
        (52,'carrot', 0.5, 41, 1, 10, 0),
        (53, 'hot dog', 3.5, 290, 9, 13, 23),
        (54, 'pizza', 2.5, 266, 11, 33, 10),
        (55, 'donut', 2, 260, 3, 30, 14),
        (56, 'cake', 1.5, 262, 2, 38, 12),
        (57, 'chair', 60, 'you', 'can', 'seat', 'here'),
        (58, 'couch', 50, 'to', 'seat9', 'and', 'sleep'),
        (59, 'potted plant', 4, 'I', 'love', 'my', 'plants'),
        (60, 'bed', 200, 'sweet', 'dreams', 'for', 'you'),
        (61,'dining table', 200, 0, 0, 0, 0),
        (62,'toilet', 100, 100, 25, 0, 0),
        (63,'tv', 600, 'Let s', 'watch', 'the', 'game'),
        (64,'laptop', 350, 0, 0, 0, 0),
        (65,'mouse', 17, 0, 0, 0, 0),
        (66,'remote', 10, 0, 0, 0, 0),
        (67,'keyboard', 25, 0, 0, 0, 0),
        (68,'cell phone', 400, 'so', 'call', 'me', 'maybe'),
        (69,'microwave', 100, 'to', 'heat', 'your', 'food'),
        (70,'oven', 200, 100, 25, 0, 0),
        (71,'toaster', 30, 0, 0, 0, 0),
        (72,'sink', 80, 0, 0, 0, 0),
        (73,'refrigerator', 800, 0, 0, 0, 0),
        (74,'book', 25, 'be', 'greater', 'than', 'average'),
        (75,'clock', 15, 0, 0, 0, 0),
        (76,'vase', 15, 0, 0, 0, 0),
        (77,'scissors', 2, 0, 0, 0, 0),
        (78,'teddy bear', 15, 0, 0, 0, 0),
        (79,'hair drier', 35, 0, 0, 0, 0),
        (80,'toothbrush', 1, 0, 0, 0, 0)
    ;""")
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
