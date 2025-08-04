# data.py
import os
import pandas as pd
from datetime import datetime


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