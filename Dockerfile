FROM node:argon

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY package.json /usr/src/app/
RUN npm install
COPY . /usr/src/app
RUN python get-pip.py
RUN pip install requests
EXPOSE 6001
CMD npm start
