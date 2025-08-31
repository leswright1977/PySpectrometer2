# Storage Folder

This folder contains persistent data for the spectrometer application.

## Contents

- **calibration_data/**: Stores calibration files, such as `caldata.txt`, used for wavelength calibration.
- **snapshots/**: Directory for saved spectrogram snapshots taken by user.

## Developer Notes

- Calibration data is read/written via `src/calibration/`.
- Snapshots are saved via `src/capture_iteration/emittance/save_snapshot.py`.
- Ensure paths in `config.json` match these locations.
- TODO: migrate storage structure and future improvements (e.g., migrating calibration data from simple .txt to proper CSV with descriptive headers).
