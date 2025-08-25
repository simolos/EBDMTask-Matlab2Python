# data.py
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Optional: for .mat export
try:
    from scipy.io import savemat
except Exception:
    savemat = None

class DataRecorder:
    """
    Record trial data and export to CSV or XLSX.
    """
    def __init__(self, output_dir: str, prefix: str):
        self.output_dir = output_dir
        self.prefix = prefix
        self.records = []  # list of dicts for each trial

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def add_trial(self, trial_data: dict):
        """
        Add a dictionary containing trial variables.
        Keys must match those in data_tab.pdf.
        """
        self.records.append(trial_data)

    def _get_filename(self, extension: str) -> str:
        """
        Construct a filename with prefix and timestamp.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.prefix}_{timestamp}.{extension}"
        return os.path.join(self.output_dir, filename)

    def save_csv(self):
        """
        Export records to a CSV file.
        """
        df = pd.DataFrame(self.records)
        path = self._get_filename('csv')
        df.to_csv(path, index=False)
        print(f"Data saved to CSV: {path}")
        return path

    def save_xlsx(self):
        """
        Export records to an Excel file (*.xlsx).
        """
        df = pd.DataFrame(self.records)
        path = self._get_filename('xlsx')
        df.to_excel(path, index=False)
        print(f"Data saved to XLSX: {path}")
        return path
    
    def save_all(
        self,
        fmt: str,
        trials_df: pd.DataFrame | None,
        cursor: np.ndarray,
        keypr: np.ndarray,
        tasktimings: list | pd.DataFrame | None,
        Hz: float | None,
        GV: float | None,
        csv_mode: str = "long",   # "long" merges per-frame + per-trial
    ) -> str:
        """
        Save everything (trials + CURSOR + KEYPR + TaskTimings + meta) into ONE file.

        fmt: "csv" | "xlsx" | "mat"
        csv_mode: "long" (recommended; one big long table)
        """
        assert cursor is not None and keypr is not None, "cursor/keypr required"
        nF, nT = cursor.shape

        # Use provided trials_df or the accumulated records
        if trials_df is None:
            trials_df = pd.DataFrame(self.records)
        # Ensure there is a 'trial' column (1..nT) for joins
        if 'trial' not in trials_df.columns:
            trials_df = trials_df.copy()
            trials_df['trial'] = np.arange(1, nT + 1, dtype=int)

        if fmt.lower() == "xlsx":
            path = self._get_filename('xlsx')
            with pd.ExcelWriter(path) as xl:
                # trials (one row per trial)
                trials_df.to_excel(xl, sheet_name="trials", index=False)
                # cursor/keypr (wide, frames as rows, trials as columns)
                pd.DataFrame(cursor).to_excel(xl, sheet_name="cursor", index=False)
                pd.DataFrame(keypr).to_excel(xl, sheet_name="keypr", index=False)
                # timings
                if tasktimings:
                    if isinstance(tasktimings, pd.DataFrame):
                        df_tt = tasktimings
                    else:
                        df_tt = pd.DataFrame(tasktimings, columns=["timestamp", "event"])
                    df_tt.to_excel(xl, sheet_name="timings", index=False)
                # meta
                meta = pd.DataFrame([{
                    "prefix": self.prefix,
                    "Hz": float(Hz) if Hz is not None else None,
                    "GV": float(GV) if GV is not None else None,
                    "nFrames": int(nF),
                    "nTrials": int(nT),
                }])
                meta.to_excel(xl, sheet_name="meta", index=False)
            print(f"All data saved to XLSX: {path}")
            return path

        elif fmt.lower() == "csv":
            # Build long framewise table and merge trials info → one big CSV
            if Hz is None:
                raise ValueError("Hz is required for CSV long export.")
            trial_idx = np.repeat(np.arange(1, nT+1), nF)
            frame_idx = np.tile(np.arange(nF), nT)
            time_s    = frame_idx / float(Hz)
            df_long = pd.DataFrame({
                "trial":  trial_idx,
                "frame":  frame_idx,
                "time_s": time_s,
                "cursor": cursor.flatten(order="F"),  # preserve [f,i] column-major
                "keypr":  keypr.flatten(order="F"),
            })
            # Merge per-trial columns (duplicated along frames)
            merged = df_long.merge(trials_df, on="trial", how="left")
            path = self._get_filename('csv')
            merged.to_csv(path, index=False)
            print(f"All data saved to CSV (long): {path}")
            return path

        elif fmt.lower() == "mat":
            if savemat is None:
                raise RuntimeError("scipy is required for .mat export. Install scipy.")
            path = self._get_filename('mat')
            mdict = {
                "CURSOR": cursor,
                "KEYPR":  keypr,
                "Hz":     float(Hz) if Hz is not None else None,
                "GV":     float(GV) if GV is not None else None,
                "prefix": self.prefix,
                # trials as dict of arrays (MATLAB-friendly)
                "trials": {col: trials_df[col].to_numpy() for col in trials_df.columns},
            }
            if tasktimings:
                if isinstance(tasktimings, pd.DataFrame):
                    mdict["TaskTimings"] = tasktimings.to_numpy(object)
                else:
                    mdict["TaskTimings"] = np.array(tasktimings, dtype=object)
            savemat(path, mdict)
            print(f"All data saved to MAT: {path}")
            return path

        else:
            raise ValueError("fmt must be one of: 'csv', 'xlsx', 'mat'")