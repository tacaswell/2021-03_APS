import datetime
from pathlib import Path

from cycler import cycler
import matplotlib.pyplot as plt
import pandas as pd


class AggregatedTimeTrace:
    def __init__(
        self,
        hourly_data,
        label,
        yearly_ax,
        monthly_ax,
        daily_ax,
        agg_by_day=None,
        agg_by_month=None,
        style_cycle=None,
    ):
        """Class to manage 3-levels of aggregated temperature

        Parameters
        ----------
        hourly_data : DataFrame
            Tempreture measured hourly

        label : str
            The name of this data set_a

        yearly_ax : Axes
            The axes to plot 'year' scale data (aggregated by month) to

        monthly_ax : Axes
            The axes to plot 'month' scale data (aggregated by day) to

        daily_ax : Axes
            The axes to plot 'day' scale data (un-aggregated hourly) to

        agg_by_day : DataFrame, optional

            Data already aggregated by day.  This is just to save
            computation, will be computed if not provided.

        agg_by_month : DataFrame, optional

            Data already aggregated by month.  This is just to save
            computation, will be computed if not provided.

        style_cycle : Cycler, optional
            Style to use for plotting

        """
        # data
        self.data_by_hour = hourly_data
        if agg_by_day is None:
            agg_by_day = aggregate_by_day(hourly_data)
        self.data_by_day = agg_by_day
        if agg_by_month is None:
            agg_by_month = aggregate_by_month(hourly_data)
        self.data_by_month = agg_by_month
        # style
        if style_cycle is None:
            style_cycle = cycler(
                "marker", ["o", "s", "^", "*", "x", "v", "8", "D", "H", "<"]
            ) + cycler(
                "color",
                [
                    "#1f77b4",
                    "#ff7f0e",
                    "#2ca02c",
                    "#d62728",
                    "#9467bd",
                    "#8c564b",
                    "#e377c2",
                    "#7f7f7f",
                    "#bcbd22",
                    "#17becf",
                ],
            )
        self.style_cycle = style_cycle()
        # axes
        self.yearly_ax = yearly_ax
        self.monthly_ax = monthly_ax
        self.daily_ax = daily_ax
        # name
        self.label = label
        # these will be used for book keeping
        self.daily_artists = {}
        self.daily_index = {}
        self.hourly_artiists = {}
        # artists
        self.yearly_art = plot_aggregated_errorbar(
            self.yearly_ax,
            self.data_by_month,
            self.label,
            picker=True,
            pickradius=5,
            **next(self.style_cycle),
        )

        # pick methods
        self.y_cid = self.yearly_ax.figure.canvas.mpl_connect(
            "pick_event", self._yearly_on_pick
        )
        self.m_cid = self.yearly_ax.figure.canvas.mpl_connect(
            "pick_event", self._monthly_on_pick
        )
        self.d_cid = self.yearly_ax.figure.canvas.mpl_connect(
            "pick_event", self._daily_on_pick
        )

    def _yearly_on_pick(self, event):
        """Process picks on 'year' scale axes"""
        # if not the right axes, bail
        if event.mouseevent.inaxes is not self.yearly_ax:
            return
        # make sure the artists we expect exists and we picked it
        if self.yearly_art is None or event.artist is not self.yearly_art[0][0]:
            return
        # loop over the points we hit and plot the 'month' scale data
        for i in event.ind:
            row = self.data_by_month.iloc[i]
            self._plot_T_by_day(int(row["year"]), int(row["month"]))

    def _monthly_on_pick(self, event):
        """Process picks on 'month' scale axes"""
        # if we are not in the right axes, bail
        if event.mouseevent.inaxes is not self.monthly_ax:
            return
        # get the label from the picked aritst
        label = event.artist.get_gid()
        # if the shift key is held down, remove this data
        if event.mouseevent.key == "shift":
            self.daily_index.pop(label, None)
            arts = self.daily_artists.pop(label, [])
            for art in arts:
                # work around a bug!
                if art in self.monthly_ax.containers:
                    self.monthly_ax.containers.remove(art)
                art.remove()
            # regenerate the legend
            self.monthly_ax.legend()
            # ask the GUI to redraw when convenient
            self.monthly_ax.figure.canvas.draw_idle()
            return
        # else, loop through the points we hit and plot the daily
        for i in event.ind:
            print(f"{label=} {i=}")
            try:
                sel_date = self.daily_index[label][i]
            except KeyError:
                print(f"failed on {label=} {i=}")
            else:
                self._plot_T_by_hour(sel_date.year, sel_date.month, sel_date.day)

    def _daily_on_pick(self, event):
        if event.mouseevent.inaxes is not self.daily_ax:
            return
        # grab the canvas
        canvas = event.artist.figure.canvas
        # remove the artist
        event.artist.remove()
        # update the legend
        self.daily_ax.legend()
        # redraw the canvas next time it is convenient
        canvas.draw_idle()

    def _plot_T_by_day(self, year, month):
        # get the data we need
        df = extract_month_of_daily(self.data_by_day, year, month)
        # format the label
        label = "{:s}: {:04d}-{:02d}".format(self.label, year, month)
        # if we have already plotted this, don't bother
        if label in self.daily_artists:
            return
        # plot the data
        eb, fill = plot_aggregated_errorbar(
            self.monthly_ax,
            df,
            label,
            picker=True,
            pickradius=5,
            **next(self.style_cycle),
        )
        # set the gid of the line (which is what will be picked) to label
        eb[0].set_gid(label)
        # stash the artists so we can remove them later
        self.daily_artists[label] = [eb, fill]
        # stash the dates associated with the points so we can use in
        # plotting later
        self.daily_index[label] = df["index"]

    def _plot_T_by_hour(self, year, month, day):
        # get the hourly data for a single day
        df = extract_day_of_hourly(self.data_by_hour, year, month, day)
        # format the label
        label = "{:s}: {:04d}-{:02d}-{:02d}".format(self.label, year, month, day)
        # A 'simple' plot
        (ln,) = self.daily_ax.plot(
            "T",
            linestyle="-",
            picker=True,
            pickradius=10,
            label=label,
            data=df,
            **next(self.style_cycle),
        )
        )
        # update the legend
        self.daily_ax.legend()
        # ask the GUI to redraw the next time it can
        self.daily_ax.figure.canvas.draw_idle()

    def remove(self):
        for art in self.yearly_art:
            art.remove()
        self.yearly_art = None
        self.yearly_ax.figure.canvas.mpl_disconnect(self.cid)


def aggregate_by_month(df, col="T"):
    """Given a data frame of hourly data, compute statistics by month

    Parameters
    ----------
    df : DataFrame
       Must have columns {'year', 'month'}

    col : str, optional
       The column to aggregate.  Defaults to 'T'

    Returns
    -------
    DataFrame
       Indexed on the 15th of the month,
       Has columns of `describe` + 'year' and 'month'
    """
    gb = df.groupby(["year", "month"])[col].describe()
    new_index = [datetime.date(*m, *(15,)) for m in gb.index]
    gb.reset_index(inplace=True)
    gb.index = new_index
    return gb


def aggregate_by_day(df, col="T"):
    """Given a data frame of hourly data, compute statistics by day

    Parameters
    ----------
    df : DataFrame
       Must have columns {'year', 'month', 'day'}

    col : str, optional
       The column to aggregate.  Defaults to 'T'

    Returns
    -------
    DataFrame
       Indexed by day.
       Has columns of `describe` + 'year', 'month', and 'day'
    """

    gb = df.groupby(["year", "month", "day"])[col].describe()
    new_index = [datetime.date(*m) for m in gb.index]
    gb.reset_index(inplace=True)
    gb.index = new_index
    return gb


def extract_month_of_daily(daily, year, month):
    """Given daily values, extract a given month

    Parameters
    ----------
    daily : DataFrame
        must of columns {'year', 'month'}

    year, month : int
        The year and month of interest

    Returns
    -------

    DataFrame
         Indexed on days from start of month.  Same columns as input
    """
    ix = (daily["month"] == month) & (daily["year"] == year)
    df = daily[ix]
    idx = [(m - df.index[0]).days for m in df.index]
    df.reset_index(inplace=True)
    df.index = idx
    return df


def extract_day_of_hourly(hourly_df, year, month, day):
    """Given a data frame with hourly data, extract data for year-month-day

    Parameters
    ----------
    hourly_df : DataFrame
      Must have columns 'year', 'month', 'day' with the expected semantics and
      a time index

    year, month, day : int
        The day to extract the data for
    """

    ix = (
        (hourly_df["month"] == month)
        & (hourly_df["year"] == year)
        & (hourly_df["day"] == day)
    )
    df = hourly_df[ix]
    midnight = datetime.datetime(year, month, day, 0, 0)
    df.index = [(m - midnight).seconds / 3600 for m in df.index]
    return df


def label_date(ax, label, date, df):
    """Helper function to annotate a date

    ``date`` is assumed to be in the index of ``df``

    Parameters
    ----------
    ax : Axes
       The axes to draw to

    label : str
        The text of the label

    date : object in index of df
        The x coordinate

    df : DataFrame
        The data source

    """
    y = df.loc[date]["mean"]
    return ax.annotate(
        label,
        (date, y),
        ha="right",
        xytext=(-10, -30),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->"},
    )


def load_data(dataset):
    """Load data from a given dataset

    Parameters
    ----------
    dataset : str
       Searches from dataset.h5 in this file's directory

    Returns
    -------
    DataFrame
       Hourly temperature data
    """
    p = Path(".") / "data"
    fname = p / f"{dataset}.h5"

    try:
        return pd.read_hdf(str(fname))
    except FileNotFoundError:
        sources = {f.stem for f in p.iterdir() if f.is_file() and f.name.endswith("h5")}
        raise RuntimeError(
            f"Could not not find {dataset!r}.  Existing " f"datasets are {sources}"
        )


def setup_temperature_figure(**kwargs):
    fig, ax_lst = plt.subplots(3, 1, sharey=True, **kwargs, constrained_layout=True)
    for ax in ax_lst:
        ax.set_ylabel("T [℃]")
        ax.grid(True)
    for ax, x_lab in zip(
        ax_lst, ["Date", "days from start of month", "hours from midnight UTC"]
    ):
        ax.set_xlabel(x_lab)

    for ax, x_lab in zip(
        ax_lst,
        [
            "Click to show monthly data",
            "Click to show hourly data, shift-click to remove",
            "click to remove ",
        ],
    ):
        ax.set_title(x_lab)
    ax_lst[1].set_xlim(-1, 32)
    ax_lst[2].set_xlim(-1, 25)
    ax_lst[0].set_ylim(-30, 40)
    return fig, ax_lst


def plot_aggregated_errorbar(ax, gb, label, pickradius=None, **kwargs):
    kwargs.setdefault("capsize", 3)
    kwargs.setdefault("markersize", 5)
    eb = ax.errorbar(
        gb.index,
        "mean",
        yerr="std",
        data=gb,
        label=label,
        pickradius=pickradius,
        **kwargs,
    )
    fill = ax.fill_between(
        gb.index, "min", "max", alpha=0.5, data=gb, color=eb[0].get_color()
    )
    ax.legend()
    ax.figure.canvas.draw_idle()
    return eb, fill
