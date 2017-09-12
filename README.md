# navet2ical
Get iCal file with the Navet events your attending.

## Getting started
```bash
git clone https://github.com/Lilleengen/navet2ical.git
cd navet2ical
cp app.example.yaml app.yaml
nano app.yaml # enter username, password and a random token in the env-variables section
pip2 install -t lib -r requirements.txt # intall dependencies to lib-folder
gcloud app deploy app.yaml # upload to Google Cloud app engine
curl https://{name}.appspot.com/?token={token} # test it
```
