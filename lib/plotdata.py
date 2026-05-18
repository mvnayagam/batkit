import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import LogLocator, FuncFormatter

plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['font.size']      = 12
plt.rcParams['axes.labelpad']  = 12

# ============================================================
# Base plotting style class
# ============================================================

class plotstyle:
    """
    Shared matplotlib styling utilities.
    """

    @staticmethod
    def gridstyle(ax, ax2=None):
        """
        Apply consistent grid styling.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Primary axis.
        ax2 : matplotlib.axes.Axes, optional
            Secondary axis.
        """

        ax.grid(True)

        ax.grid( which='major', linestyle='-', linewidth=0.8, zorder=-1000)
        
        ax.grid( axis='x', which='minor', linestyle=':', linewidth=0.5, zorder=-1000)
        
        if ax2 is not None:
            ax2.grid( True, which='major', zorder=-1000 )

    # ---------------------------------------------------------

    @staticmethod
    def switchonticks(ax, secondy=None, minor=True):
        """
        Configure ticks/spines for single or dual y-axis plots.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Primary axis.

        secondy : matplotlib.axes.Axes, optional
            Secondary y-axis.

        minor : bool
            Enable minor ticks.
        """

        # -----------------------------
        # Minor ticks
        # -----------------------------
        if minor:
            ax.minorticks_on()
        else:
            ax.minorticks_off()

        # -----------------------------
        # Dual y-axis
        # -----------------------------
        if secondy is not None:

            ax.tick_params(axis='x', direction='in', which='major', length=8, top=True, bottom=True, left=False, right=False, zorder=-1000)
            ax.tick_params(axis='x', direction='in', which='minor', length=4, top=True, bottom=True, left=False, right=False, zorder=-1000)
            ax.tick_params(axis='y', direction='in', which='major', length=8, left=True, right=False, zorder=-1000)
            ax.tick_params(axis='y', direction='in', which='minor', length=4, left=True, right=False, zorder=-1000)
            
            # ---------------------------------
            # Secondary axis
            # ---------------------------------
            if minor:
                secondy.minorticks_on()
            else:
                secondy.minorticks_off()
            
            secondy.tick_params(axis='y', direction='in', which='major', length=8, left=False, right=True, zorder=-1000)
            secondy.tick_params(axis='y', direction='in', which='minor', length=4, left=False, right=True, zorder=-1000 )
            secondy.tick_params(axis='y', which='both', colors='r')
            
            # ---------------------------------
            # Spine styling
            # ---------------------------------
            secondy.spines['left'].set_visible(False)
            secondy.spines['bottom'].set_visible(False)
            secondy.spines['top'].set_visible(False)
            secondy.spines['right'].set_color('r')
            secondy.spines[['left', 'bottom', 'top']].set_visible(False)
            
            ax.spines['right'].set_visible(False)
            
            secondy.set_axisbelow(True)
            
        # -----------------------------
        # Single axis
        # -----------------------------
        else:
            
            ax.tick_params(axis='both', direction='in', which='major', length=8, top=True, bottom=True, left=True, right=True )
            
            ax.tick_params(axis='both', direction='in', which='minor', length=4, top=True, bottom=True, left=True, right=True )
            
        ax.set_axisbelow(True)
    

# ============================================================
# Main plotting class
# ============================================================

class plotdata(plotstyle):
    """
    Electrochemistry plotting utilities.
    """

    # ========================================================
    # Internal helpers
    # ========================================================

    @staticmethod
    def _filter_cycles(df, startcycle=0, endcycle=None):

        if endcycle is None or endcycle == -1:
            endcycle = df["cycle number"].max()

        mask = ( (df["cycle number"] >= startcycle) & (df["cycle number"] <= endcycle) )

        return df.loc[mask].copy()

    # --------------------------------------------------------

    @staticmethod
    def _get_average_q(df):

        grouped = df.groupby("cycle number")

        tcycle = np.array(list(grouped.groups.keys()))

        qave = grouped.apply(
            lambda x: x.loc[
                x["Q charge or discharge"] >= 0,
                "Q charge or discharge"
            ].max()
        ).to_numpy()

        dqave = grouped.apply(
            lambda x: x.loc[
                x["Q charge or discharge"] < 0,
                "Q charge or discharge"
            ].min()
        ).to_numpy()

        return tcycle, qave, dqave

    # ========================================================
    # Q charge/discharge
    # ========================================================

    @classmethod
    def plot_Qchargedischarge(cls, df, showtime=True, grid=True, figshow=True, charge_color='g', discharge_color='b'):
        
        fig, ax = plt.subplots(figsize=(14, 5))
        
        cls.switchonticks(ax)
        
        ax.set_xlabel('Cycle number')
        ax.set_ylabel('Q charge or discharge (mAh)')
        
        tcycle, qave, dqave = cls._get_average_q(df)
        
        ax.plot( tcycle, qave, color=charge_color, lw=2, label="Charging" )
        ax.plot( tcycle, np.abs(dqave), color=discharge_color, lw=2, label="Discharging" )

        ax.set_xlim(0, tcycle.max())

        if grid:
            cls.gridstyle(ax)
            
        ax.legend()

        # ----------------------------------------------------
        # Top time axis
        # ----------------------------------------------------
        if showtime:
            
            secax = ax.secondary_xaxis('top')
            
            ticks = ax.get_xticks()
            
            labels = []
            
            for c in ticks:
                c_int = int(round(c))
                if c_int in tcycle:
                    t = df.loc[df['cycle number'] == c_int, 'time'].iloc[0]
                    labels.append(f"{t / 3600:.1f}")
                else:
                    labels.append("")
            secax.set_xticks(ticks)
            secax.set_xticklabels(labels)
            secax.set_xlabel("Time (h)")
        
        plt.tight_layout()
        if figshow:
            plt.show()
        return fig, ax

    # ========================================================
    # Bode impedance
    # ========================================================

    @classmethod
    def plot_bode_impedance(cls, df, startcycle=0, endcycle=None, show=True):

        fig, ax = plt.subplots(figsize=(14, 5))
        
        ax2 = ax.twinx()
        ax.set_xscale('log')
        cls.switchonticks(ax, secondy=ax2)
        cls.gridstyle(ax, ax2)
        
        tcycle = np.unique(df["cycle number"].values)
        
        if endcycle is None:
            endcycle = len(tcycle)
        
        cycles = tcycle[startcycle:endcycle] if endcycle is None else tcycle[startcycle:endcycle+1]
        
        # ----------------------------------------------------
        # Loop over charge/discharge branches
        # ----------------------------------------------------
        branches = [(3, '-', 'Charging'),(11, '--', 'Discharging')]
        
        for i, idx in enumerate(cycles):
            for ns, linestyle, label in branches:
                subset = df[(df["cycle number"] == idx) & (df["Ns"] == ns) ]
                
                if subset.empty:
                    continue
                
                freq = subset["freq"]
                zmag = subset["|Z|"]
                phase = subset["Phase(Z)"]
                
                use_label = label if i == 0 else None
                
                ax.plot(freq, zmag, linestyle=linestyle, color='b', lw=2, label=use_label, rasterized=True )
                ax2.plot(freq, phase, linestyle=linestyle, color='r', lw=2, rasterized=True )
                
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("|Z| (Ohm)")
        
        ax2.set_ylabel("Phase(Z) (deg.)", color='r')
        ax.xaxis.set_major_locator(LogLocator(base=10))
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:g}'))
        ax.legend()
        plt.tight_layout()
        
        if show:
            plt.show()
        
        return fig, (ax, ax2)

    # ========================================================
    # Time vs E and I
    # ========================================================

    @classmethod
    def timevsEandI(cls, df, startcycle=5, endcycle=None, showlegend=False, savefig=False, show=True ):
        
        dftmp = cls._filter_cycles(df, startcycle, endcycle)
        
        fig, ax = plt.subplots(figsize=(14, 5))
        
        l1, = ax.plot( dftmp["time"] / 3600, dftmp["Ewe"], 'b-', lw=2, label="Ecell")
        
        ax.set_xlabel("Time (h)")
        ax.set_ylabel("Ecell (V)")
        
        ax2 = ax.twinx()
        
        l2, = ax2.plot( dftmp["time"] / 3600, dftmp["I"], 'r-', lw=2, label="Current")
        
        ax2.set_ylabel("Current (mA)", c='r')
        
        cls.gridstyle(ax, ax2)
        cls.switchonticks(ax, ax2)

        if showlegend:
            
            lines = [l1, l2]
            labels = [l.get_label() for l in lines]
            
            ax2.legend(lines, labels, loc="best")
            
        plt.tight_layout()
        
        if savefig:
            fig.savefig('timevsEandI.png', dpi=600)
            
        if show:
            plt.show()
        
        return fig, (ax, ax2)

    # ========================================================
    # Cycle vs E and I
    # ========================================================

    @classmethod
    def cyclevsEandI(cls, df, startcycle=5, endcycle=None, showlegend=False, savefig=False, show=True ):
        
        dftmp = cls._filter_cycles(df, startcycle, endcycle)
        
        fig, ax = plt.subplots(figsize=(14, 5))
        
        l1, = ax.plot( dftmp["cycle number"], dftmp["Ewe"], 'b-', lw=2, label="Ecell")
        
        ax.set_xlabel("Cycle Number")
        ax.set_ylabel("Ecell (V)")
        
        ax2 = ax.twinx()
        
        l2, = ax2.plot(dftmp["cycle number"], dftmp["I"], 'r-', lw=2, label="Current" )
        
        ax2.set_ylabel("Current (mA)", c='r')
        
        cls.gridstyle(ax, ax2)
        cls.switchonticks(ax, ax2)
        
        if showlegend:
            lines = [l1, l2]
            labels = [l.get_label() for l in lines]
            ax2.legend(lines, labels, loc="best")
        plt.tight_layout()
        
        if savefig:
            fig.savefig('cyclevsEandI.png', dpi=600)
            
        if show:
            plt.show()
        
        return fig, (ax, ax2)
    
    # ========================================================
    # Time-cycle vs E and I
    # ========================================================

    @classmethod
    def timecyclevsEandI(cls, df, startcycle=5, endcycle=None, interval=5, savefig=False, show=True ):

        dftmp = cls._filter_cycles(df, startcycle, endcycle)
        
        time = dftmp['time'].to_numpy() / 3600
        cycle = dftmp['cycle number'].to_numpy()
        
        Ewe = dftmp['Ewe'].to_numpy()
        I = dftmp['I'].to_numpy()
        
        fig, ax = plt.subplots(figsize=(14, 5))
        
        # ----------------------------------------------------
        # Top cycle axis
        # ----------------------------------------------------
        ax_top = ax.twiny()

        change_idx = np.flatnonzero( np.diff(cycle, prepend=cycle[0] - 1))
        
        sel = change_idx[::interval]
        
        t_sel = time[sel]
        
        for t in t_sel:
            ax_top.axvline(t, lw=0.5, ls='--', color='k', alpha=0.95 )
            
        ax_top.set_xticks(t_sel)
        ax_top.set_xticklabels(cycle[sel])
        
        ax_top.set_xlabel('Cycle number')
        
        ax_top.spines[['bottom', 'left', 'right']].set_visible(False)
        
        # ----------------------------------------------------
        # Twin y-axis
        # ----------------------------------------------------
        ax2 = ax.twinx()
        cls.switchonticks(ax, ax2)
        cls.gridstyle(ax, ax2)
        
        ax.plot(time, Ewe, color='b')
        ax.set_xlabel('Time (h)')
        ax.set_ylabel('Ecell (V)', color='b')
                
        ax2.plot(time, I, color='r')
        ax2.set_ylabel('Current (mA)', color='r')
        
        plt.tight_layout()
        
        if savefig:
            fig.savefig('timecyclevsEandI.png', dpi=600)
            
        if show:
            plt.show()
        
        return fig, (ax, ax2, ax_top)

