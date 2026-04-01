import pandas as pd
import json
from typing import List, Dict


class FlightPathExtractor:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._df = None
        self._coords = None

    def load(self):
        """
        Load DJI flight CSV (handles DJI metadata header)
        """
        self._df = pd.read_csv(self.filepath, skiprows=1)
        return self

    def extract(self, include_time=True):
        """
        Extract latitude, longitude, altitude + FIXED date/time
        """
        base_cols = [
            'OSD.latitude',
            'OSD.longitude',
            'OSD.altitude [ft]'
        ]

        cols = base_cols.copy()
        time_col = None

        if include_time:
            possible_time_cols = [
                'OSD.time [local]',
                'OSD.time',
                'CUSTOM.date [local]',
                'CUSTOM.updateTime [local]'
            ]

            for col in possible_time_cols:
                if col in self._df.columns:
                    time_col = col
                    break

            if 'OSD.flyTime' not in self._df.columns:
                raise ValueError("OSD.flyTime column required")

            cols.append('OSD.flyTime')

            if time_col:
                cols.append(time_col)

        coords = self._df[cols].copy()

        # Drop rows missing GPS or altitude
        coords = coords.dropna(subset=base_cols)

        # Remove zero altitude (your requirement)
        coords = coords[coords['OSD.altitude [ft]'] != 0]

        # Rename
        rename_map = {
            'OSD.latitude': 'latitude',
            'OSD.longitude': 'longitude',
            'OSD.altitude [ft]': 'altitude_ft',
            'OSD.flyTime': 'fly_time'
        }

        if time_col:
            rename_map[time_col] = 'timestamp'

        coords = coords.rename(columns=rename_map)

        # -------- TIME FIX --------
        if include_time:
            # Clean fly_time
            coords['fly_time'] = (
                coords['fly_time']
                .astype(str)
                .str.replace(r'[^\d\.]', '', regex=True)
            )

            coords['fly_time'] = pd.to_numeric(coords['fly_time'], errors='coerce')
            coords = coords.dropna(subset=['fly_time'])

            # 🔥 ROUND TIME (your requirement)
            coords['fly_time'] = coords['fly_time'].round().astype(int)

            # Base datetime
            base_datetime = None

            if 'timestamp' in coords.columns:
                parsed = pd.to_datetime(coords['timestamp'], errors='coerce')
                parsed = parsed.dropna()

                if not parsed.empty:
                    base_datetime = parsed.iloc[0]

            if base_datetime is None:
                base_datetime = pd.Timestamp("1970-01-01")

            # Reconstruct datetime
            coords['datetime'] = base_datetime + pd.to_timedelta(coords['fly_time'], unit='s')

            # Extract clean date/time
            coords['date'] = coords['datetime'].dt.date
            coords['time'] = coords['datetime'].dt.time

            # Cleanup
            drop_cols = ['datetime']
            if 'timestamp' in coords.columns:
                drop_cols.append('timestamp')

            coords = coords.drop(columns=drop_cols)

        self._coords = coords
        return self

    def to_meters(self):
        """
        Convert altitude to meters
        """
        if self._coords is None:
            raise RuntimeError("Run extract() first")

        self._coords['altitude_m'] = self._coords['altitude_ft'] * 0.3048
        return self

    def deduplicate(self):
        """
        Remove consecutive duplicate points
        """
        if self._coords is None:
            raise RuntimeError("Run extract() first")

        self._coords = self._coords.loc[
            (self._coords.shift() != self._coords).any(axis=1)
        ]
        return self

    def to_list(self) -> List[Dict]:
        """
        Return list with ISO-formatted date and time
        """
        if self._coords is None:
            raise RuntimeError("Run extract() first")

        result = []

        for _, row in self._coords.iterrows():
            record = {
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'altitude_ft': row['altitude_ft'],
                'altitude_m': row.get('altitude_m', None),
                'date': row['date'].isoformat() if pd.notnull(row.get('date')) else None,
                'time': row['time'].isoformat() if pd.notnull(row.get('time')) else None
            }
            result.append(record)

        return result

    def to_csv(self, output_path: str):
        """
        Save cleaned coordinates to CSV
        """
        if self._coords is None:
            raise RuntimeError("Run extract() first")

        df = self._coords.copy()

        if 'date' in df.columns:
            df['date'] = df['date'].astype(str)

        if 'time' in df.columns:
            df['time'] = df['time'].astype(str)

        df.to_csv(output_path, index=False)

    def to_geojson(self, output_path: str = None) -> Dict:
        """
        Convert to GeoJSON LineString (with timestamps)
        """
        if self._coords is None:
            raise RuntimeError("Run extract() first")

        coordinates = []
        properties = []

        for _, row in self._coords.iterrows():
            coordinates.append([
                row['longitude'],
                row['latitude'],
                row.get('altitude_ft', 0)
            ])

            properties.append({
                'date': row['date'].isoformat() if pd.notnull(row.get('date')) else None,
                'time': row['time'].isoformat() if pd.notnull(row.get('time')) else None
            })

        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            },
            "properties": {
                "timestamps": properties
            }
        }

        if output_path:
            with open(output_path, 'w') as f:
                json.dump(geojson, f, indent=2)

        return geojson