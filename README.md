# TNDP for Binzhou
A data-driven end-to-end process for real-world Transit Network Design Problem (TNDP) in Binzhou city.

## Setup
1. Clone the repository and install the required python packages (`conda install --yes --file requirements.txt`).
2. Edit `path.py` in `./TNDP-Heuristic/src` and `./preProcessing/src`.
3. Switch to directory `./TNDP-Heuristic/src`.
4. (optional) Run the program (`python main_HEU.py <required args>`) to generate a fair result in milliseconds if needed.
5. Run the program (`python main.py <required args>`) to generate final result in 4-5h/200it.
6. Switch to directory `./TNDP-Heuristic/result/geojson` to check the output.