"""This script gets the raw data outputted by the lorawan test"""
import sage_data_client
import pandas as pd

def get_data():
    """Get data from SAGE"""
    # query and load data into pandas data frame
    df = sage_data_client.query(
        start="2025-04-21T00:00:00Z",
        end="2025-04-25T00:00:00Z",
        filter={
            "vsn": "W027",
            "deviceName":"packet test",
            "devEui": "a8610a34342f7319",
            "task": "lorawan-listener"
        }
    ).sort_values(by='timestamp', ascending=True)

    return df

def process(df):
    """Process the data"""

    # Pivot the DataFrame
    pivot_df = df.pivot_table(index="timestamp", columns="name", values="value", aggfunc="first").reset_index()

    # filter out packets size we don't need
    # drop signal.plr, this column will not work since it's continious and aggrates over time
    # and each location is a different instance
    pivot_df = pivot_df[pivot_df["packet_size"] != 3].drop(columns=["signal.plr"])

    # order by timestamp and packet id
    pivot_df = pivot_df.sort_values(by=["timestamp", "packet_id"])

    # since frame-counter validation was disabled, we need to filter out packets that came in mutltiple times
    # Define a time delta threshold to consider duplicates (e.g., 60 seconds)
    time_threshold = pd.Timedelta(seconds=60)

    # Mark duplicates: same packet_id occurring within 10 seconds
    pivot_df["is_duplicate"] = (
        pivot_df.groupby("packet_id")["timestamp"]
        .diff()
        .fillna(pd.Timedelta(seconds=9999)) < time_threshold
    )

    # Filter out duplicates
    pivot_df = pivot_df[~pivot_df["is_duplicate"]].drop(columns="is_duplicate")

    # filter out packets from 2025-04-23 2:42 to 2:53 pm, this location is unknown
    pivot_df = pivot_df[~((pivot_df["timestamp"] >= "2025-04-23 19:42:00") & (pivot_df["timestamp"] <= "2025-04-23 19:53:00"))]

    # Merge location data based on order
    loc = pd.read_csv("locations.csv")
    loc = loc[loc["success"] == "true"].reset_index(drop=True) # filter our locations that lora device failed to join the network
    pivot_df["lat(EPSG:4326)"] = None
    pivot_df["long(EPSG:4326)"] = None

    pivot_df.loc[:21, "lat(EPSG:4326)"] = loc.loc[0, "lat(EPSG:4326)"]
    pivot_df.loc[:21, "long(EPSG:4326)"] = loc.loc[0, "long(EPSG:4326)"]

    pivot_df.loc[22:44, "lat(EPSG:4326)"] = loc.loc[1, "lat(EPSG:4326)"]
    pivot_df.loc[22:44, "long(EPSG:4326)"] = loc.loc[1, "long(EPSG:4326)"]

    pivot_df.loc[45:90, "lat(EPSG:4326)"] = loc.loc[2, "lat(EPSG:4326)"]
    pivot_df.loc[45:90, "long(EPSG:4326)"] = loc.loc[2, "long(EPSG:4326)"]

    pivot_df.loc[91:113, "lat(EPSG:4326)"] = loc.loc[3, "lat(EPSG:4326)"]
    pivot_df.loc[91:113, "long(EPSG:4326)"] = loc.loc[3, "long(EPSG:4326)"]

    pivot_df.loc[114:135, "lat(EPSG:4326)"] = loc.loc[4, "lat(EPSG:4326)"]
    pivot_df.loc[114:135, "long(EPSG:4326)"] = loc.loc[4, "long(EPSG:4326)"]

    pivot_df.loc[136:169, "lat(EPSG:4326)"] = loc.loc[5, "lat(EPSG:4326)"]
    pivot_df.loc[136:169, "long(EPSG:4326)"] = loc.loc[5, "long(EPSG:4326)"]

    pivot_df.loc[170:193, "lat(EPSG:4326)"] = loc.loc[6, "lat(EPSG:4326)"]
    pivot_df.loc[170:193, "long(EPSG:4326)"] = loc.loc[6, "long(EPSG:4326)"]

    pivot_df.loc[194:219, "lat(EPSG:4326)"] = loc.loc[7, "lat(EPSG:4326)"]
    pivot_df.loc[194:219, "long(EPSG:4326)"] = loc.loc[7, "long(EPSG:4326)"]

    pivot_df.loc[220:238, "lat(EPSG:4326)"] = loc.loc[8, "lat(EPSG:4326)"]
    pivot_df.loc[220:238, "long(EPSG:4326)"] = loc.loc[8, "long(EPSG:4326)"]

    pivot_df.loc[239:257, "lat(EPSG:4326)"] = loc.loc[9, "lat(EPSG:4326)"]
    pivot_df.loc[239:257, "long(EPSG:4326)"] = loc.loc[9, "long(EPSG:4326)"]

    pivot_df.loc[258:, "lat(EPSG:4326)"] = loc.loc[10, "lat(EPSG:4326)"]
    pivot_df.loc[258:, "long(EPSG:4326)"] = loc.loc[10, "long(EPSG:4326)"]
    
    return pivot_df

if main := __name__ == "__main__":

    # get the data
    df = get_data()

    # save raw data to csv
    df.to_csv("raw.csv", index=False)

    # process the data
    processed_df = process(df)

    # save processed data to csv
    processed_df.to_csv("processed.csv", index=False)