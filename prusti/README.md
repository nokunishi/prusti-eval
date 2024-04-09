Some Notes:
`err.py` may take long to complete since it recursively delete the viper log files in /tmp dir
calling `crates.py` should be done with caution, it will overwrite the num of fns with 0 if the viper dump files do not exists in /tmp/log (which is deleted immediate due to optmize storage)
