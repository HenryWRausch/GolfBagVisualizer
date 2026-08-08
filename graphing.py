from database import BagDatabase


class BagGrapher:
    # holds a database connection to access data for a player
    # contains methods for generating graphs,

    def __init__(self, name: str = "Demo"):

        # create our basics
        self.db = BagDatabase(name)
        self.name = name
        self.bag = self.db.get_bag()
