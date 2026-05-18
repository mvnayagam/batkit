import os
import numpy as np
import pandas as pd
import yadg


class mprtool:
    """
    Data-processing class for EC-Lab and BT-Lab .mpr files.

    Workflow:
        ds = mprtool(path, filename)
        ds.load()
        ds.df
        ds.get_columns(...)
        ds.filter_cycles(...)
        ds.export_csv(...)
    """

    def __init__(self, path: str, filename: str):
        self.path = path
        self.filename = filename
        self.filepath = os.path.join(path, filename)
        
        self.df = None  # loaded dataset cache

    # ---------------------------------------------------------
    # Load data
    # ---------------------------------------------------------
    def load(self) -> pd.DataFrame:
        """
        Load .mpr file into a pandas DataFrame.
        Cached after first load.
        """
        
        if self.df is not None:
            return self.df
        
        if not os.path.isfile(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        dataset = yadg.extractors.extract(timezone=None, filetype="eclab.mpr", path=self.filepath,).to_dataset()
        
        df = dataset.to_dataframe()
        
        # derived column
        df["cycle number"] = np.floor(df["half cycle"] / 2).astype(int)
        
        self.df = df
        
        return df

    # ---------------------------------------------------------
    # Convenience accessor
    # ---------------------------------------------------------
    def data(self) -> pd.DataFrame:
        """Return loaded DataFrame (loads if needed)."""
        return self.load()

    # ---------------------------------------------------------
    # Column extraction
    # ---------------------------------------------------------
    def get_columns(self, columns):
        """
        Extract one or more columns as numpy arrays.

        Parameters
        ----------
        columns : str | list[str]

        Returns
        -------
        dict or np.ndarray
        """

        df = self.data()

        if isinstance(columns, str):
            return df[columns].to_numpy()

        if isinstance(columns, (list, tuple)):
            return {col: df[col].to_numpy() for col in columns}

        raise TypeError("columns must be str or list/tuple")

    # ---------------------------------------------------------
    # Cycle filtering
    # ---------------------------------------------------------
    def filter_cycles(self, start=0, end=None):
        """
        Return filtered DataFrame view by cycle range.
        """
        
        df = self.data()
        
        if end is None:
            end = df["cycle number"].max()
        
        mask = (df["cycle number"] >= start) & (df["cycle number"] <= end)
        
        return df.loc[mask].copy()
    
    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------
        
    def export_csv(self, columns, start_cycle=0, end_cycle=None, sep="\t"):

        # -------------------------
        # Input validation
        # -------------------------
        if isinstance(columns, str):
            raise TypeError(
                f"""
                [ERROR] 'columns' must be a list of column names, not a string. You passed: {columns}
                
                Correct usage:
                    ds.export_csv(columns=['col1', 'col2'])
                Hint:
                    Available columns: {list(self.data.columns)}
                """
                )

        if not columns:
            raise ValueError("columns cannot be empty. Example: ['col1', 'col2']")
        
        df = self.filter_cycles(start_cycle, end_cycle)
        
        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise KeyError(
                f"""
                    [ERROR] These columns do not exist: {missing}
                    Available columns:{list(df.columns)}
                """)
        
        safe_name = "_".join(str(c).replace("|", "") for c in columns)
        outname = f"{os.path.splitext(self.filename)[0]}_{safe_name}.dat"
        outpath = os.path.join(self.path, outname)

        df.loc[:, columns].to_csv(outpath, sep=sep, index=False)

        print(f"[DONE] Exported: {outpath}")
        return outpath
    
    # ---------------------------------------------------------
    # get_average_q
    # ---------------------------------------------------------
    def get_average_q(self, start_cycle=0, end_cycle=None):
        """
        Compute average charge/discharge capacities per cycle.

        Parameters
        ----------
        start_cycle : int
            First cycle to include.
        end_cycle : int or None
            Last cycle to include. If None, uses max cycle.

        Returns
        -------
        tcycle : np.ndarray
            Unique cycle numbers
        qave : list
            Max charge (Q >= 0) per cycle
        dqave : list
            Min discharge (Q < 0) per cycle
        """

        df = self.data()

        if "cycle number" not in df.columns or "Q charge or discharge" not in df.columns:
            raise ValueError("DataFrame must contain 'cycle number' and 'Q charge or discharge'")

        if end_cycle is None:
            end_cycle = df["cycle number"].max()

        # cycle range filter
        df = df[(df["cycle number"] >= start_cycle) & (df["cycle number"] <= end_cycle)]

        tcycle = np.unique(df["cycle number"].values)

        qave  = []
        dqave = []

        for c in tcycle:
            subset = df[df["cycle number"] == c]

            # charge (positive)
            q_vals = subset[subset["Q charge or discharge"] >= 0]["Q charge or discharge"]
            qave.append(q_vals.max() if not q_vals.empty else np.nan)

            # discharge (negative)
            dq_vals = subset[subset["Q charge or discharge"] < 0]["Q charge or discharge"]
            dqave.append(dq_vals.min() if not dq_vals.empty else np.nan)

        return tcycle, np.array(qave), np.array(dqave)

    # ---------------------------------------------------------
    # Quick inspection helper
    # ---------------------------------------------------------
    def summary(self):
        """
        Print dataset summary
        """
        
        df = self.data()
        
        print("File    :", self.filename)
        print("Shape   :", df.shape)
        print(f"Cycles :{ df["cycle number"].min()} - {df["cycle number"].max()}")
        print(f"No of columns: {len(df.columns)}")
        print(f"Columns: \n {df.columns}")
        
        return

#-----------------------------------------------------------------------
