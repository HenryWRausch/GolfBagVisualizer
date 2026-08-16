import io
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

from database import BagDatabase, Filter

# pyright: basic
# matplotlib and type checkers do not mix


class BagGrapher:
    # holds a database connection to access data for a player
    # contains methods for generating graphs
    # as well as some QoL stuff for getting information

    def __init__(self, name: str = "Demo", filter_: Filter | None = None):

        # create our basics
        self.db = BagDatabase(name)
        self.name = name
        self.bag = self.db.get_bag()

        # TODO - put some thought into the order here (reverse)
        self.colors = [
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

        self.filter_ = Filter() if filter_ is None else filter_

    def plot_all_points(self):
        # makes a figure that contains all filtered points as colored dots on line
        # color dictated by club, but TODO to allow it by date or course
        # supports at most 15 clubs. TODO to make it infinite
        # TODO - maybe think about a funny hole layout at some distance

        filter_ = self.filter_

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
        fig = plt.figure(figsize=(0.3, 8))
        ax = fig.add_subplot(111)

        # TODO - put some thought into the order here (reverse)
        colors = [color for color in self.colors]

        legend_labels = []

        for club in data:
            assert colors, "Graphing currently only supports 15 clubs"

            color = colors.pop()
            legend_labels.append(club)
            ax.scatter([0] * len(data[club]), data[club], color=color)

            # include averages in legend
        averages = self.averages_within_bound()

        # convert club id to club abbreviation
        for idx, club_id in enumerate(legend_labels):
            legend_labels[idx] = (
                f"{self.db.get_club_by_id(club_id)['abbreviation']}: {round(averages[club_id])}"
            )

        ax.legend(legend_labels, loc="center left", bbox_to_anchor=(1.02, 0.5))

        ax.set_title("Summary")

        # strip the x-axis
        ax.set_xticks([])

        # make start at zero
        ax.set_ylim(bottom=0)

        fig.tight_layout()

        return fig

    def plot_clubs_discrete(self):

        filter_ = self.filter_

        # construct club list
        if "clubs" in filter_:
            clubs = []
            for club in filter_["clubs"]:
                fetched_club = self.db.get_club_by_id(club)
                clubs.append((fetched_club["id"], fetched_club["abbreviation"]))
        else:
            bag = self.db.get_bag()
            clubs = [(club["id"], club["abbreviation"]) for club in bag]

        assert len(clubs) > 0, "Must graph at least one club"

        # get shots
        shots = self.db.get_shots(filter_)

        # divide our data into clubs
        if "clubs" in filter_:
            data = {i: [] for i in filter_["clubs"]}
        else:
            bag = self.db.get_bag()
            data = {i["id"]: [] for i in bag}

        for shot in shots:
            data[shot["club_id"]].append(shot["distance"])

        # construct figure
        fig, axes = plt.subplots(
            1, len(clubs), figsize=(len(clubs), 8), squeeze=False, sharey=True
        )  # one ax for each plot, 1 inch each ax

        axes = axes.flat
        colors = [color for color in self.colors]

        long_swing = 0

        for ax, club in zip(axes, clubs):
            id_, name = club

            ax.set_title(name)
            curr_data = data[id_]
            frequencies = Counter(curr_data)

            xs, ys = [], []
            # TODO - adjusting bin size
            max_width = 0
            for distance, count in frequencies.items():
                edge = count - 1
                max_width = max(max_width, edge)
                long_swing = max(long_swing, distance)
                x_range = range(-edge, edge + 1, 2)
                xs.extend(list(x_range))
                ys.extend([distance] * count)

            buffer = 1  # TODO - dial this in please
            ax.set_xlim(-max_width - buffer, max_width + buffer)

            # strip the x-axis
            ax.set_xticks([])

            # make start at zero
            upper_limit = (long_swing // 25 * 25) + 25  # nearest 25 after longest swing
            ax.set_ylim(0, upper_limit)

            # set y axis ticks
            ax.set_yticks(range(0, upper_limit + 1, 50))
            ax.set_yticks(range(0, upper_limit + 1, 10), minor=True)

            ax.tick_params(which="both", right=True)

            ax.scatter(xs, ys, color=colors.pop())

        axes[-1].tick_params(right=True, labelright=True)

        return fig

    def plot_clubs_continuous(self):
        filter_ = self.filter_

        # construct club list
        if "clubs" in filter_:
            clubs = []
            for club in filter_["clubs"]:
                fetched_club = self.db.get_club_by_id(club)
                clubs.append((fetched_club["id"], fetched_club["abbreviation"]))
        else:
            bag = self.db.get_bag()
            clubs = [(club["id"], club["abbreviation"]) for club in bag]

        assert len(clubs) > 0, "Must graph at least one club"

        # get shots
        shots = self.db.get_shots(filter_)

        # divide our data into clubs
        if "clubs" in filter_:
            data = {i: [] for i in filter_["clubs"]}
        else:
            bag = self.db.get_bag()
            data = {i["id"]: [] for i in bag}

        for shot in shots:
            data[shot["club_id"]].append(shot["distance"])

        # construct figure
        fig, axes = plt.subplots(
            1, len(clubs), figsize=(len(clubs), 8), squeeze=False, sharey=True
        )  # one ax for each plot, 1 inch each ax

        axes = axes.flat
        colors = [color for color in self.colors]

        long_swing = 0

        for ax, club in zip(axes, clubs):
            id_, name = club

            ax.set_title(name)
            curr_data = data[id_]
            if curr_data:
                long_swing = max(long_swing, max(curr_data))
            sns.violinplot(y=curr_data, color=colors.pop(), inner="quartile", ax=ax)

            # strip the x-axis
            ax.set_xticks([])

            # make start at zero
            upper_limit = (long_swing // 25 * 25) + 25  # nearest 25 after longest swing
            ax.set_ylim(0, upper_limit)

            # set y axis ticks
            ax.set_yticks(range(0, upper_limit + 1, 50))
            ax.set_yticks(range(0, upper_limit + 1, 10), minor=True)

            ax.tick_params(which="both", right=True)

        axes[-1].tick_params(right=True, labelright=True)

        return fig

    def averages_within_bound(self):
        shots = self.db.get_shots(self.filter_)

        # construct club list
        if "clubs" in self.filter_:
            clubs = []
            for club in self.filter_["clubs"]:
                fetched_club = self.db.get_club_by_id(club)
                clubs.append((fetched_club["id"], fetched_club["abbreviation"]))
        else:
            bag = self.db.get_bag()
            clubs = [(club["id"], club["abbreviation"]) for club in bag]

        assert len(clubs) > 0, "Must have at least one club"

        # divide our data into clubs
        if "clubs" in self.filter_:
            data = {i: [] for i in self.filter_["clubs"]}
        else:
            bag = self.db.get_bag()
            data = {i["id"]: [] for i in bag}

        for shot in shots:
            data[shot["club_id"]].append(shot["distance"])

        averages = {}

        for club, shots in data.items():
            shots.sort()

            # 10th and 90th percentile
            # TODO - make this smarter
            lower_index = int(len(shots) * 0.1)
            upper_index = int(len(shots) * 0.9)

            shots = shots[lower_index : upper_index + 1]

            if len(shots) > 0:
                averages[club] = sum(shots) / len(shots)

        return averages

    def make_summary_image(
        self, method: str, destination: str | Path = "Report.png", show: bool = True
    ):
        if method == "discrete":
            clubs_plot = self.plot_clubs_discrete()
        elif method == "continuous":
            clubs_plot = self.plot_clubs_continuous()
        else:
            raise ValueError('Method must be either "discrete" or "continuous"')

        summary_plot = self.plot_all_points()

        # save both to memory
        summary_buf = io.BytesIO()
        clubs_buf = io.BytesIO()

        summary_plot.savefig(summary_buf, format="png", bbox_inches="tight")
        clubs_plot.savefig(clubs_buf, format="png", bbox_inches="tight")

        # load them into pil
        summary_buf.seek(0)
        clubs_buf.seek(0)
        summary_img = Image.open(summary_buf)
        clubs_img = Image.open(clubs_buf)

        # merge them
        total_width = summary_img.width + clubs_img.width
        max_height = max(summary_img.height, clubs_img.height)

        output = Image.new("RGB", (total_width, max_height), (255, 255, 255))

        output.paste(summary_img, (0, 0))
        output.paste(clubs_img, (summary_img.width, 0))  # offset by summary width

        # save it
        output.save(destination)

        # show it if we want
        if show:
            output.show()


bg = BagGrapher()
bg.make_summary_image("continuous")
