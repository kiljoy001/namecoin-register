FROM ubuntu:latest
LABEL authors="Scott J Guyton"

ENTRYPOINT ["top", "-b"]