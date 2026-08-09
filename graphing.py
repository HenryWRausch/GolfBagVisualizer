import matplotlib.pyplot as plt

from database import BagDatabase, Filter

# pyright: basic
# matplotlib and type checkers do not mix


class BagGrapher:
    # holds a database connection to access data for a player
    # contains methods for generating graphs
    # as well as some QoL stuff for getting information

    def __init__(self, name: str = "Demo"):

        # create our basics
        self.db = BagDatabase(name)
        self.name = name
        self.bag = self.db.get_bag()

    def plot_all_points(self, filter_: Filter | None = None):
        # makes a figure that contains all filtered points as colored dots on line
        # color dictated by club, but TODO to allow it by date or course
        # supports at most 15 clubs. TODO to make it infinite
        # TODO - maybe think about a funny hole layout at some distance

        if filter_ is None:
            filter_ = Filter()

        # get our data
        shots = self.db.get_shots(filter_)

        # divide our data into clubs
        if "clubs" in filter_:
            data = {i: [] for i in filter_["clubs"]}
        else:
            bag = self.db.get_bag()
            data = {i["id"]: [] for i in bag}

        for shot in shots:
            data[shot["club_id"]].append(shot["distance"])

        # set up our figure
        fig = plt.figure(figsize=(1, 8))
        ax = fig.add_subplot(111)

        # TODO - put some thought into the order here (reverse)
        colors = [
            "tab:blue",
            "tab:orange",
            "tab:green",
            "tab:red",
            "tab:purple",
            "tab:brown",
            "tab:pink",
            "tab:gray",
            "tab:olive",
            "tab:cyan",
            "steelblue",
            "darkorange",
            "forestgreen",
            "firebrick",
            "slategray",
        ]

        for club in data:
            assert colors, "Graphing currently only supports 15 clubs"
            # LABELLING TO BE HANDLED ELSEWHERE
            color = colors.pop()
            ax.scatter([0] * len(data[club]), data[club], color=color)

        # strip the x-axis
        ax.set_xticks([])

        # make start at zero
        ax.set_ylim(bottom=0)

        fig.tight_layout()


bg = BagGrapher()

bg.plot_all_points()
