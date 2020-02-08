# PWSCUP-2017-judge-system-reproduction
Reproducing the judge system of [PWSCUP 2017](http://www.iwsec.org/pws/pwscup/PWSCUP2017.html) for educational and practice purposes. The judgement codes were provided by the PWSCUP 2017 Committee.

## Requirement & Installation

**Ruby** (for executing judgement codes)

Follow the installation instructions of [Ruby's official page](https://www.ruby-lang.org/en/downloads/)

**Python 3.X** (for executing judgement codes)
- Pandas
- Numpy

instruction: 
```
sudo pip3 install pandas numpy
```

**Python 2.7** (for the reproduction system)
- flask
- celery
- redis
- pandas
- numpy
- bson

instructions:
```
sudo pip install flask flask-login flask-wtf flask_sqlalchemy flask_pymongo flask_table
sudo pip install celery
sudo pip install redis
sudo pip install pandas numpy
sudo pip install bson
```

**Redis server** (for the reproduction system)

instruction: 
```
sudo apt-get install redis-server
```

**Mongodb** (for the reproduction system)

instructions:
```
echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo nano /etc/systemd/system/mongodb.service
```

Add the following text and press `ctrl+X` to save the file and exit from nano
```
[Unit]
Description=High-performance, schema-free document-oriented database After=network.target 

[Service]
User=mongodb
ExecStart=/usr/bin/mongod --quiet --config /etc/mongod.conf 

[Install]
WantedBy=multi-user.target
```

## Start the System

### 1. Start Mongodb

instructions:
```
sudo systemctl start mongodb
sudo systemctl status mongodb
sudo systemctl enable mongodb
```

※`sudo systemctl status mongodb` is for the status check

### 2. Start Celery Server

instruction:
```
celery -A app.celery worker --loglevel=info
```

### 3. Start the Reproduction Server

instruction:
```
python app.py
```

## Submitting Rules

First of all, register an account. Note that when you submit your files, please make sure that you do follow the following rules strictly. This system was wrote by myself within only one week, so the examination of the system is not perfect. You might trigger some bugs (e.g. filename inconsistency) which would shut the system down if you don't follow the rules. Unfortunately, I have no time to fix those bugs currently, so please do follow the rules strictly.

The data format of AT and Fh files should follow the rules of PWSCUP 2017, or they will not pass the data check. You can download the rules documents, sample data, and judgement codes from [PWSCUP 2017 official webpage](http://www.iwsec.org/pws/pwscup/PWSCUP2017.html).

### Anonymization

For the anonymization submission, please go to the Anony page and upload your AT file. The filename should follow the following format: AT_xxx.txt, where xxx can be taken at will (**in alphanumeric**).

If the upload is successful, you shall see the check symbol as shown in the following image.

![pic1](https://i.imgur.com/w6aETiL.png)

After that, please click the submit button, the system will take some time to check the format of your AT file, please do not close the page during that period.

The system will show you the confirmation message as shown in the following image after the data checking is done, please click the submit button to finish your submission if all the messages are correct.

![pic2](https://i.imgur.com/gHovQw7.png)

The system usually takes less than one minute to process your submission (depends on hardware of the server). You can close the page after the submission is done, and check your grades in the score page after a while.

![pic3](https://i.imgur.com/QUOQSD6.png)

You can also see the scores of all of your submissions by clicking the "Personal scores" button at the bottom of the score page (since the score page will only show you the scores of latest three submissions).

![pic4](https://i.imgur.com/dLuAxcY.png)

### Re-identification

For the re-identification submission, it's similar to the anonymization submission.

First, you need to go to the Reid page and upload your **four** Fh files **simultaneously** as shown in the following image (**do not upload the S file**).

![pic4](https://i.imgur.com/vS9omRV.png)

The filename of Fh files should follow the following example: if the S file you download from the score page is `S_aa_20171223175348529920.txt`, then your Fh files should be named like `Fh25_aa_20171223175348529920.txt`,  `Fh50_aa_20171223175348529920.txt`, `Fh75_aa_20171223175348529920.txt` and `Fh100_aa_20171223175348529920.txt`.

The rest steps are similar to the anonymization submission, except you will see the evaluation scores immediately after your submission is done. Please do not close the page before you see the evaluation scores.

For the convience of re-identification, I added a new feature that you can download the anonymized files from the score page directly. You can also see the related scores by clicking the username and filename of the target row in the score page.
