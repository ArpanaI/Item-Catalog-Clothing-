from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, ClothDB, User

engine = create_engine('sqlite:///ClothesCatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="admin", email="arpanasureshi@gmail.com")
session.add(User1)
session.commit()

# Dummy clothes data
dress1 = ClothDB(brandName="ONLY",
               color="Red",
	       price="100",	
               description="Beautifu Skirt", category="Western Wear", user_id=1)

session.add(dress1)
session.commit()

dress2 = ClothDB(brandName="Vishudh",
               color="Pink",
	       price="800",	
               description="Beautifu Salwar Suit", category="Indian Wear", user_id=1)

session.add(dress2)
session.commit()

dress3 = ClothDB(brandName="Libas",
               color ="Blue",
	       price ="1200",
               description="Gorgeous Top", category="Sports Wear", user_id=1)

session.add(dress3)
session.commit()

dress4 = ClothDB(brandName="Admyrin",
               color="Grey",
	       price = "1500",	
               description="Elegant Plazzo", category="India Wear", user_id=1)

session.add(dress4)
session.commit()

dress5 = ClothDB(brandName="Go Colors",
               color="off white",
	       price="600",	
               description="shaping tights", category="Western Wear", user_id=1)

session.add(dress5)
session.commit()


print "added Clothes!"
