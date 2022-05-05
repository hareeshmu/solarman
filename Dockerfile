# ---- Base ----
FROM python:alpine AS base

#
# ---- Dependencies ----
FROM base AS dependencies
# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
 
#
# ---- Release ----
FROM dependencies AS release
# copy project source file(s)
WORKDIR /
COPY solarman.py .
COPY mqtt.py .
CMD ["python", "-u", "/solarman.py", "--repeat"]