# Removes the existing files
hdfs dfs -rm -r -f /user/smullassery/syssec

# Makes a new directory for input and to output the results
hdfs dfs -mkdir /user/smullassery/syssec

# Loads the urllist to HDFS
hdfs dfs -put ./urllist.txt /user/smullassery/syssec
