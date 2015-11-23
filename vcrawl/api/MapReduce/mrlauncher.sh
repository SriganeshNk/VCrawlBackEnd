#! /bin/bash

# Configuring input and output paths for the job
usage(){
  echo -e "mrlauncher.sh [options]\n \
  -i INPUT_WEBPAGES_PATH, --input=INPUT_WEBPAGES_PATH \t The HDFS path for the loaded list of webpages \n \
  -o OUTPUT_VULNERABILITIES_PATH, --output=OUTPUT_VULNERABILITIES_PATH \t The HDFS prefix path to store result containing vulnerabilities in webpages"
  exit 1
}

while : 
do
    case $1 in
        -h | --help | -\?)
          usage;
          exit 0
          ;;
        -i | --input)
          webPagesPath=$2
          shift 2
          ;;
        --input=*)
          webPagesPath=${1#*=}
          shift
          ;;
        -o | --output)
          resultPath=$2
          shift 2
          ;;
        --output=*)
          resultPath=${1#*=}
          shift
          ;;
        --)
          shift
          break
         ;;
        -*)
          echo "Unknown option: $1" >&2
          shift
          ;;
        *)
          break
          ;;
     esac
done

HJAR=${HADOOP_STREAMING_PATH}/hadoop-streaming.jar
INPUT=${webPagesPath}
OUTPUT=${resultPath}
numreducers=0

hadoop jar ${HJAR} \
 -input ${INPUT} -output ${OUTPUT} \
 -file ./mapper.py -mapper ./mapper.py \
 -reducer None -numReduceTasks 0
